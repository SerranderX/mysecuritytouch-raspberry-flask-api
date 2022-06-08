from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

class LcdPanel:
    # Modify this if you have a different sized character LCD
    def __init__(self):
        self.lcd_columns = 16
        self.lcd_rows = 2
        # compatible with all versions of RPI as of Jan. 2019
        # v1 - v3B+
        self.lcd_rs = digitalio.DigitalInOut(board.D22)
        self.lcd_en = digitalio.DigitalInOut(board.D17)
        self.lcd_d4 = digitalio.DigitalInOut(board.D25)
        self.lcd_d5 = digitalio.DigitalInOut(board.D24)
        self.lcd_d6 = digitalio.DigitalInOut(board.D23)
        self.lcd_d7 = digitalio.DigitalInOut(board.D18)
        # Initialise the lcd class
        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en, self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7, self.lcd_columns, self.lcd_rows)

    def escribir(self, message):
        self.lcd.clear()
        result = False
        stringValue = "some text"
        if(type(message) == type(stringValue)):
            messageToPrint = ""
            lengthMessage = len(message)    
            if(lengthMessage <= 32):
                messageToPrint += message[0:16] + "\n"
                messageToPrint += message[16:lengthMessage]
                self.lcd.message = messageToPrint
            else:
                print("some error")
        
         
