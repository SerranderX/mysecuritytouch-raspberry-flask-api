import time
import board
import busio
import os
from lcdpanel.lcdpanel import *
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
import serial

class Fingerprint_utils():
    
    def __init__(self):
        self.led = DigitalInOut(board.D13)
        self.led.direction = Direction.OUTPUT

        self.uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
         
        self.finger = adafruit_fingerprint.Adafruit_Fingerprint(self.uart)

        self.lcdPanel = LcdPanel()
        
    def get_fingerprint(self):
        os.system('sudo systemctl stop lcdDefault.service')
        self.lcdPanel.escribir("Esperando una huella")
        while self.finger.get_image() != adafruit_fingerprint.OK:
            pass
        if self.finger.image_2_tz(1) != adafruit_fingerprint.OK:
            self.lcdPanel.escribir("Error al authenticar")
            time.sleep(1)
            os.system('sudo systemctl start lcdDefault.service')  
            return False
        self.lcdPanel.escribir("   Cargando...  ")
        time.sleep(1)
        if self.finger.finger_search() != adafruit_fingerprint.OK:
            self.lcdPanel.escribir("Error al authenticar")
            time.sleep(1)
            os.system('sudo systemctl start lcdDefault.service')
            return False
        self.lcdPanel.escribir("Usuario #{} authenticado".format(self.finger.finger_id))
        time.sleep(1)
        os.system('sudo systemctl start lcdDefault.service')
        return True
     
     
    # pylint: disable=too-many-branches
    def get_fingerprint_detail(self):
        os.system('sudo systemctl stop lcdDefault.service')
        self.lcdPanel.escribir("Esperando huella...")
        time.sleep(1)
        i = self.finger.get_image()
        if i == adafruit_fingerprint.OK:
            self.lcdPanel.escribir("Imagen tomada correctamente.")
            time.sleep(1)
        else:
            if i == adafruit_fingerprint.NOFINGER:
                self.lcdPanel.escribir("No se detecto huella.")
                time.sleep(1)
            elif i == adafruit_fingerprint.IMAGEFAIL:
                self.lcdPanel.escribir("Error creando imagen.")
                time.sleep(1)
            else:
                self.lcdPanel.escribir("Ocurrio un error.")
                time.sleep(1)
            os.system('sudo systemctl start lcdDefault.service')
            return False
     
        self.lcdPanel.escribir("Esperando huella...")
        time.sleep(1)
        i = self.finger.image_2_tz(1)
        if i == adafruit_fingerprint.OK:
            self.lcdPanel.escribir("Imagen tomada correctamente")
            time.sleep(1)
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                self.lcdPanel.escribir("Imagen demasiado difusa")
                time.sleep(1)
            elif i == adafruit_fingerprint.FEATUREFAIL:
                self.lcdPanel.escribir("Error al identificar detalles")
                time.sleep(1)
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                self.lcdPanel.escribir("Imagen invalida")
                time.sleep(1)
            else:
                self.lcdPanel.escribir("Ocurrio un error.")
                time.sleep(1)
            os.system('sudo systemctl start lcdDefault.service')
            return False
     
        self.lcdPanel.escribir("   Cargando...  ")
        time.sleep(1)
        i = self.finger.finger_fast_search()
        # pylint: disable=no-else-return
        # This block needs to be refactored when it can be tested.
        if i == adafruit_fingerprint.OK:
            self.lcdPanel.escribir("Found fingerprint!")
            time.sleep(1)
            os.system('sudo systemctl start lcdDefault.service')
            return True
        else:
            if i == adafruit_fingerprint.NOTFOUND:
                self.lcdPanel.escribir("No se encontro usuario")
                time.sleep(1)
            else:
                self.lcdPanel.escribir("Ocurrio un error.")
                time.sleep(1)
            os.system('sudo systemctl start lcdDefault.service')
            return False
     
     
    # pylint: disable=too-many-statements
    def enroll_finger(self, location):
        os.system('sudo systemctl stop lcdDefault.service')
        """Take a 2 finger images and template it, then store in 'location'"""
        for fingerimg in range(1, 3):
            if fingerimg == 1:
                self.lcdPanel.escribir("Coloque su dedo en el sensor")
                time.sleep(1)
            else:
                self.lcdPanel.escribir("Vuelva a colocar su dedo")
                time.sleep(1)
                 
            while True:
                i = self.finger.get_image()
                if i == adafruit_fingerprint.OK:
                    self.lcdPanel.escribir("Imagen tomada")
                    time.sleep(1)
                    break
                if i == adafruit_fingerprint.NOFINGER:
                    a = 1
                elif i == adafruit_fingerprint.IMAGEFAIL:
                    self.lcdPanel.escribir("Error creando imagen.")
                    time.sleep(1)
                    os.system('sudo systemctl start lcdDefault.service')
                    return False
                else:
                    self.lcdPanel.escribir("Ocurrio un error.")
                    time.sleep(1)
                    os.system('sudo systemctl start lcdDefault.service')
                    return False
     
            self.lcdPanel.escribir("Guardando imagen...")
            time.sleep(1)
            i = self.finger.image_2_tz(fingerimg)
            if i == adafruit_fingerprint.OK:
                self.lcdPanel.escribir("Imagen guardada exitosamente")
                time.sleep(1)
            else:
                if i == adafruit_fingerprint.IMAGEMESS:
                    self.lcdPanel.escribir("Imagen demasiado difusa")
                    time.sleep(1)
                elif i == adafruit_fingerprint.FEATUREFAIL:
                    self.lcdPanel.escribir("Error al identificar detalles")
                    time.sleep(1)
                elif i == adafruit_fingerprint.INVALIDIMAGE:
                    self.lcdPanel.escribir("Imagen invalida")
                    time.sleep(1)
                else:
                    self.lcdPanel.escribir("Ocurrio un error.")
                    time.sleep(1)
                os.system('sudo systemctl start lcdDefault.service')
                return False
     
            if fingerimg == 1:
                self.lcdPanel.escribir("Remueva su dedo porfavor")
                time.sleep(1)
                while i != adafruit_fingerprint.NOFINGER:
                    i = self.finger.get_image()
     
        self.lcdPanel.escribir("   Cargando...  ")
        time.sleep(1)
        i = self.finger.create_model()
        if i == adafruit_fingerprint.OK:
            self.lcdPanel.escribir("Registro creado correctamente")
            time.sleep(1)
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                self.lcdPanel.escribir("Imagenes no concuerdan...")
                time.sleep(1)
            else:
                self.lcdPanel.escribir("Ocurrio un error.")
                time.sleep(1)
            os.system('sudo systemctl start lcdDefault.service')
            return False
     
        self.lcdPanel.escribir("Guardando usuario en: {}".format(location))
        time.sleep(2)
        i = self.finger.store_model(location)
        if i == adafruit_fingerprint.OK:
            self.lcdPanel.escribir("Stored")
            time.sleep(1)
        else:
            if i == adafruit_fingerprint.BADLOCATION:
                self.lcdPanel.escribir("Bad storage location")
                time.sleep(1)
            elif i == adafruit_fingerprint.FLASHERR:
                self.lcdPanel.escribir("Flash storage error")
                time.sleep(1)
            else:
                self.lcdPanel.escribir("Other error")
                time.sleep(1)
            os.system('sudo systemctl start lcdDefault.service')
            return False
        
        os.system('sudo systemctl start lcdDefault.service')
        return True
