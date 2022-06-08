#import RPi.GPIO as GPIO
import board
import digitalio
import time


class Led_utils:
    
    def __init__(self):
        self.led1 = digitalio.DigitalInOut(board.D6)
        self.led2 = digitalio.DigitalInOut(board.D13)
        self.led3 = digitalio.DigitalInOut(board.D26)
        self.led4 = digitalio.DigitalInOut(board.D2)
        self.led5 = digitalio.DigitalInOut(board.D3)
        self.led6 = digitalio.DigitalInOut(board.D16)
        self.led7 = digitalio.DigitalInOut(board.D21)
        self.led8 = digitalio.DigitalInOut(board.D20)
        
        self.led1.direction = digitalio.Direction.OUTPUT
        self.led2.direction = digitalio.Direction.OUTPUT
        self.led3.direction = digitalio.Direction.OUTPUT
        self.led4.direction = digitalio.Direction.OUTPUT
        self.led5.direction = digitalio.Direction.OUTPUT
        self.led6.direction = digitalio.Direction.OUTPUT
        self.led7.direction = digitalio.Direction.OUTPUT
        self.led8.direction = digitalio.Direction.OUTPUT
        
        self.switcher = {
                1:self.led1,
                2:self.led2,
                3:self.led3,
                4:self.led4,
                5:self.led5,
                6:self.led6,
                7:self.led7,
                8:self.led8
            }
        
        #GPIO.setmode(GPIO.BOARD)
        #Protoboard inferior
        #self.pin = 31 #azul
        #self.pin2 = 33 #rojo 
        #self.pin3 = 37 #verde

        #Protoboard superior derecha
        #self.pin4 = 3 #verde
        #self.pin5 = 5 #rojo 

        #Protoboard pequena
        #self.pin6 = 36 #amarillo
        #self.pin7 = 40 #rojo
        #self.pin8 = 38 #verde
        
        #self.switcher = {
        #        1:31,
        #        2:33,
        #        3:37,
        #        4:3,
        #        5:5,
        #        6:36,
        #        7:40,
        #        8:38
        #    }
        
        #GPIO.setup(self.pin, GPIO.OUT)
        #GPIO.setup(self.pin2, GPIO.OUT)
        #GPIO.setup(self.pin3, GPIO.OUT)
        #GPIO.setup(self.pin4, GPIO.OUT)
        #GPIO.setup(self.pin5, GPIO.OUT)
        #GPIO.setup(self.pin6, GPIO.OUT)
        #GPIO.setup(self.pin7, GPIO.OUT)
        #GPIO.setup(self.pin8, GPIO.OUT)
        
    def encenderLed(self, pin=0, instruccion=False):
        result = False
        if pin != 0:
            #print("pin vale {0}".format(pin))
            
            option = self.switcher.get(pin,False)
            
            #print("option vale {}".format(option))
            if option != False:
                if instruccion:
                    option.value = True
                else:
                    option.value = False
            else:
                print("opcion no se encontro")
        return result

    def apagarLedsAutoEncendibles(self):
        self.led1.value = False
        self.led2.value = False
        self.led3.value = False
        #self.led4.value = False
        self.led5.value = False
        self.led6.value = False
        self.led7.value = False
        self.led8.value = False
        
        
#resultOutMethod = None
#leds_utils = Led_utils()
#resultOutMethod = leds_utils.encenderLed(1, True)
#print("Funcion enciende {}".format(resultOutMethod))
#time.sleep(2)
#resultOutMethod = leds_utils.encenderLed(1, False)
#print("Funcion apaga {}".format(resultOutMethod))