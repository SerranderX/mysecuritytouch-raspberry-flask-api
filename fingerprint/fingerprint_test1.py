import time
import board
import busio
import os
from lcdpanel.lcdpanel import *
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

 
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

import serial
uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
 
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

lcdPanel = LcdPanel()

def get_fingerprint():
    lcdPanel.escribir("Esperando una huella")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    lcdPanel.escribir("   Cargando...  ")
    time.sleep(1)
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True
 
 
# pylint: disable=too-many-branches
def get_fingerprint_detail():
    lcdPanel.escribir("Esperando huella...")
    time.sleep(1)
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        lcdPanel.escribir("Imagen tomada correctamente.")
        time.sleep(1)
    else:
        if i == adafruit_fingerprint.NOFINGER:
            lcdPanel.escribir("No se detecto huella.")
            time.sleep(1)
	elif i == adafruit_fingerprint.IMAGEFAIL:
            lcdPanel.escribir("Error creando imagen.")
            time.sleep(1)
        else:
            lcdPanel.escribir("Ocurrio un error.")
            time.sleep(1)
        return False
 
    lcdPanel.escribir("Esperando huella...")
    time.sleep(1)
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        lcdPanel.escribir("Imagen tomada correctamente")
        time.sleep(1)
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            lcdPanel.escribir("Imagen demasiado difusa")
            time.sleep(1)
        elif i == adafruit_fingerprint.FEATUREFAIL:
            lcdPanel.escribir("Error al identificar detalles")
            time.sleep(1)
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            lcdPanel.escribir("Imagen invalida")
            time.sleep(1)
        else:
            lcdPanel.escribir("Ocurrio un error.")
            time.sleep(1)
        return False
 
    lcdPanel.escribir("   Cargando...  ")
    time.sleep(1)
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        lcdPanel.escribir("Found fingerprint!")
        time.sleep(1)
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            lcdPanel.escribir("No se encontro usuario")
            time.sleep(1)
        else:
            lcdPanel.escribir("Ocurrio un error.")
            time.sleep(1)
        return False
 
 
# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            lcdPanel.escribir("Coloque su dedo en el sensor")
            time.sleep(1)
        else:
            lcdPanel.escribir("Vuelva a colocar su dedo")
            time.sleep(1)
             
        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                lcdPanel.escribir("Imagen tomada")
                time.sleep(1)
                break
            if i == adafruit_fingerprint.IMAGEFAIL:
                lcdPanel.escribir("Error creando imagen.")
                time.sleep(1)
                return False
            else:
                lcdPanel.escribir("Ocurrio un error.")
                time.sleep(1)
                return False
 
        lcdPanel.escribir("Guardando imagen...")
        time.sleep(1)
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            lcdPanel.escribir("Imagen guardada exitosamente")
            time.sleep(1)
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                lcdPanel.escribir("Imagen demasiado difusa")
                time.sleep(1)
            elif i == adafruit_fingerprint.FEATUREFAIL:
                lcdPanel.escribir("Error al identificar detalles")
                time.sleep(1)
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                lcdPanel.escribir("Imagen invalida")
                time.sleep(1)
            else:
                lcdPanel.escribir("Ocurrio un error.")
                time.sleep(1)
            return False
 
        if fingerimg == 1:
            lcdPanel.escribir("Remueva su dedo porfavor")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()
 
    lcdPanel.escribir("   Cargando...  ")
    time.sleep(1)
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        lcdPanel.escribir("Registro creado correctamente")
        time.sleep(1)
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            lcdPanel.escribir("Imagenes no concuerdan...")
            time.sleep(1)
        else:
            lcdPanel.escribir("Ocurrio un error.")
            time.sleep(1)
        return False
 
    lcdPanel.escribir("Guardando usuario en: {}".format(location))
    time.sleep(2)
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        lcdPanel.escribir("Stored")
        time.sleep(1)
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            lcdPanel.escribir("Bad storage location")
            time.sleep(1)
        elif i == adafruit_fingerprint.FLASHERR:
            lcdPanel.escribir("Flash storage error")
            time.sleep(1)
        else:
            lcdPanel.escribir("Other error")
            time.sleep(1)
        return False
 
    return True
 
 
##################################################
 
 
def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i
 
 
while True:
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates:", finger.templates)
    print("e) enroll print")
    print("f) find print")
    print("d) delete print")
    print("----------------")
    c = input("> ")
 
    if c == "e":
        os.system('sudo systemctl stop lcdDefault.service')
        enroll_finger(get_num())
        time.sleep(1)
        os.system('sudo systemctl start lcdDefault.service')
    if c == "f":
        os.system('sudo systemctl stop lcdDefault.service')
        if get_fingerprint():
            lcdPanel.escribir("Usuario #{} authenticado".format(finger.finger_id))
            time.sleep(1)
            #print("Detected #""with confidence", finger.confidence)
        else:
            lcdPanel.escribir("No se encontro coincidencia.")
            time.sleep(1)
        os.system('sudo systemctl start lcdDefault.service')
    if c == "d":
        os.system('sudo systemctl stop lcdDefault.service')
        if finger.delete_model(get_num()) == adafruit_fingerprint.OK:
            lcdPanel.escribir("Registro eliminado!")
            time.sleep(1)
        else:
            lcdPanel.escribir("Error al eliminar el registro")
            time.sleep(1)
        os.system('sudo systemctl start lcdDefault.service')
