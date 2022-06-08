from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
from bson import json_util
from bson.objectid import ObjectId
from lcdpanel.lcdpanel import *
from leds.leds import Led_utils
from fingerprint.fingerprint_utils import Fingerprint_utils
from time import sleep

import requests
import datetime
import os
import configparser
import threading
import json
import time
import board
import socketio
import asyncio

from werkzeug.security import generate_password_hash, check_password_hash

config = configparser.ConfigParser()
config.read_file(open('aplication.config.ini'))
urlBackend = config['MySecurityTouch-Backend']['URL']

app = Flask(__name__)

#app.secret_key = 'myawesomesecretkey'

#conexion a base de datos local de mongo db
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mysecuritytouch'
mongo = PyMongo(app)

os.system('sudo systemctl start lcdDefault.service')

#object class from Leds_utils
leds = Led_utils()
leds.apagarLedsAutoEncendibles()
leds.encenderLed(4,True)

#fingerprint object class to manupulate fingerprint
fingerprintUtils = Fingerprint_utils()

#COMENTARIO UTIL PARA REINICIAR EL AUTO INCREMENTABLE DE LAS HUELLAS DIGITALES
#mongo.db.fingerprint.delete_one({'_id': ObjectId("5f6aa9ea696f8204c5bffe0b")})
#mongo.db.fingerprint.insert_one({"id":1})

@app.route('/llamadaTimbre', methods=['POST'])
def llamarTimbre():
    config = configparser.ConfigParser()
    config.read_file(open('aplication.config.ini'))
    idDispositivo = config['MySecurityTouch-DeviceData']['_id']
    nombreDispositivo = config['MySecurityTouch-DeviceData']['nombre']
    objDataRequest = {"idDispositivo": idDispositivo, "nombreDispositivo": nombreDispositivo ,"event":"llamadaTimbre"}
    sio.emit('llamarTimbre', objDataRequest)
    return "True response if it is Ok // cambiar"

#CONTROLLER HUELLA Y ACCESO
@app.route('/fingerprint/enrolarUsuario', methods=['POST'])
def enrolarUsuario():
    result = None
    try:
        json_data = request.get_json()
        
        usuario = json_data["usuario"]
        
        if not usuario:
            raise Exception()
        
        fingerprint = json_util.loads(json_util.dumps(mongo.db.fingerprint.find()))
        if not fingerprint:
            print("no existe index")
            mongo.db.fingerprint.insert_one({"id":1})
        else:
            _id = fingerprint[0]["_id"]
            id = fingerprint[0]["id"] + 1
            #GuardarHuellaUsuario
            registroHuella = fingerprintUtils.enroll_finger(id)

            if registroHuella:
                dateNow = datetime.datetime.now()
                
                usuarioGrupoFamiliar = {
                        "idGrupoFamiliar": json_data["idGrupoFamiliar"],
                        "idUsuario": json_data["idUsuario"],
                        "username": json_data["usuario"],
                        "fechaCreacion": str(dateNow),
                        "idRegistroHuella": id
                }
                
                print(usuarioGrupoFamiliar)
                
                mongo.db.usuarioGrupoFamiliar.insert_one(usuarioGrupoFamiliar)
                
                print(usuarioGrupoFamiliar)
                
                mongo.db.fingerprint.update_one({'_id': ObjectId(_id)},{'$set': {'id': id}})
                fingerprintAutoIncrementable = json_util.loads(json_util.dumps(mongo.db.fingerprint.find()))
                
                
                message = {
                    'status': 200,
                    'data': {
                        'status': True,
                        'usuarioGrupoFamiliar': usuarioGrupoFamiliar   
                    }
                }
                
                message['data']['usuarioGrupoFamiliar'].pop('_id')
                
                response = json_util.dumps(message)
                return Response(response, mimetype="application/json")
            else:
                raise Exception()      
    except Exception as error:
        message = {
                    'message': "No se pudo grabar la huella del usuario: {0}".format(error),
                    'status': 500 
        }
        response = jsonify(message)
        response.status_code = 500 
        return response

@app.route('/fingerprint/entrar', methods=['POST'])
def entrar():
    messaje = None
    result = fingerprintUtils.get_fingerprint()
    if result:
        messaje = "Usuario authenticado"
    else:
        messaje = "No te pudo authenticar el usuario"
    return messaje

#CONTROLLER IP UTILS
@app.route('/ipUtils/guardarIpCurrent', methods=['POST'])
def guardarIpCurrent():
    result = {"message":None, "data":0}
    updateCentralDB = False
    try:
        json_data = request.get_json()
        
        ipCurrent = json_data["ipCurrent"]
        
        if (ipCurrent is not None):
            
            ipRegExist = json_util.loads(json_util.dumps(mongo.db.ipCurrent.find()))
            
            if(len(ipRegExist) == 0):
                print("option 1")
                ipCurrentInsert = {"ipCurrent": ipCurrent} 
                mongo.db.ipCurrent.insert_one(ipCurrentInsert)                
                aux = False
                
                while aux is not True:
                    registro = json_util.loads(json_util.dumps(mongo.db.ipCurrent.find()))
                    print(registro)
                    if registro[0]['ipCurrent'] == ipCurrent:
                        aux = True
                    else:
                        mongo.db.ipCurrent.update_one({'_id': ObjectId(registro[0]['_id'])},{'$set': {'ipCurrent': ipCurrent}})
                result['message'] = "Creacion del registro de ip current"
                result['data'] = 1
                updateCentralDB = True
            elif(len(ipRegExist) > 0):
                print("option 2")
                print(ipRegExist[0]['ipCurrent'])
                if(ipRegExist[0]['ipCurrent'] == ipCurrent):
                    print("option 21")
                    result['message'] = "No existen cambios en la ip current"
                    result['data'] = 0
                elif(ipRegExist[0]['ipCurrent'] != ipCurrent):
                    print("option 22")
                    aux = True
                    
                    _idRegistro = ipRegExist[0]['_id']
                    ipHistoric = ipRegExist[0]['ipCurrent']
                    
                    mongo.db.ipCurrent.update_one({'_id': ObjectId(_idRegistro)},{'$set': {'ipCurrent': ipCurrent, 'ipHistoric': ipHistoric}})
                    while aux is not True:
                        registro = json_util.loads(json_util.dumps(mongo.db.ipCurrent.find()))
                        if registro[0]['ipCurrent'] == ipCurrent:
                            print("option 221")
                            aux = True
                        else:
                            print("option 222")
                            mongo.db.ipCurrent.update_one({'_id': ObjectId(_idRegistro)},{'$set': {'ipCurrent': ipCurrent, 'ipHistoric': ipHistoric}})
                        result['message'] = "Ejecucion exitosa"
                        result['data'] = 1
                    updateCentralDB = True
            else:
                raise Exception()
        
        if updateCentralDB is True:
            print(ipCurrent)
            config = configparser.ConfigParser()
            config.read_file(open('aplication.config.ini'))
            idDispositivo = config['MySecurityTouch-DeviceData']['idDispositivo']
            _id = config['MySecurityTouch-DeviceData']['_id']
            fechaCreacion = datetime.datetime.now()
            
            ipRegExist = json_util.loads(json_util.dumps(mongo.db.ipCurrent.find()))
                            
            dispositivoDTO = {
                "nombre": "sdfdsf",
                "idDispositivo": idDispositivo,
                "idGrupoFamiliar": "asdasdas",
                "fechaCreacion": str(fechaCreacion),
                "status": False,
                "ipDispositivo": ipCurrent
            }
            jsonRequest = json_util.dumps(dispositivoDTO)
            print(jsonRequest)
            endPoint = urlBackend + "MySecurityTouch-RestApi/dispositivos/updateDispositivo/" + _id + "/2"
            print(endPoint)
            auxSuccess = False
            
            while auxSuccess is not True:
                print("antes del request")
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                response = requests.put(endPoint,data=jsonRequest,headers=headers)
                
                print(response.json())
                print("response")
                print(response)
                
                auxSuccess = True
            #config['MySecurityTouch-DeviceData']['ipCurrent'] = ipRegExist[0]['ipCurrent']
    except Exception as error:
        message = {
                    'message': "{0}".format(error),
                    'status': 500 
        }
        return json_util.dumps(message)
    return json_util.dumps(result)
        
@app.route('/ipUtils/getIpCurrent', methods=['GET'])
def getIpCurrent():
    result = None
    if result:
        return result
    return None
    
#CONTROLLER UTILS
@app.route('/utils/initializateDevice', methods=['POST'])
def initializateDevice():
    result = None
    try:
        json_data = request.get_json()
        
        idO = json_data["_id"]
        idDispositivo = json_data["idDispositivo"]
        fechaCreacion = json_data["fechaCreacion"]
        nombre = json_data["nombre"]
        status = json_data["status"]
        if (idDispositivo is not None or nombre is not None):
            config = configparser.ConfigParser()
            config.read_file(open('aplication.config.ini'))
            config['MySecurityTouch-DeviceData']['_id'] = idO
            config['MySecurityTouch-DeviceData']['idDispositivo'] = str(idDispositivo)
            config['MySecurityTouch-DeviceData']['fechaCreacion'] = str(fechaCreacion)
            config['MySecurityTouch-DeviceData']['nombre'] = nombre
            config['MySecurityTouch-DeviceData']['status'] = str(status)
            
            with open('aplication.config.ini', 'w') as configfile:
                config.write(configfile)
            
            responseObj = {"message":"Datos guardados con exito", "data": True}
            
            response = json_util.dumps(responseObj)
            
            result = response
        else:
            raise Exception("Error, variable(s) se encuentra(n) vacias.")
        
        return Response(result, mimetype="application/json")
    except Exception:
        return "A ocurrido un error"
    except:
        return "A ocurrido un error"
    return None

@app.errorhandler(406)
def bad_request(error=None):
    message = {
        'message': 'Request Not Acceptable ' + request.url,
        'status': 406 
    }
    response = jsonify(message)
    response.status_code = 406 
    return response

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'message': 'Resource Not Found ' + request.url,
        'status': 404
    }
    print(message)
    response = jsonify(message)
    response.status_code = 404
    return response

try:
    sio = socketio.Client()
    sio.connect(urlBackend)
    print("servidor {} inicializado!".format(urlBackend))
except:
    print("no se logro levantar socket io")
    

@sio.on('msgToClient')
def message(data):
    print('mensaje recivido!:')
    leds.encenderLed(6,True)
    sleep(1)
    leds.encenderLed(6,False)
    print(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1234 )
