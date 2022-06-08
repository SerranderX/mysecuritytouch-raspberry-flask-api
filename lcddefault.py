from subprocess import Popen, PIPE
from time import sleep
from datetime import datetime

import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
#from leds.leds import Led_utils

# Modify this if you have a different sized character LCD
lcd_columns = 16
lcd_rows = 2

# compatible with all versions of RPI as of Jan. 2019
# v1 - v3B+
lcd_rs = digitalio.DigitalInOut(board.D22)
lcd_en = digitalio.DigitalInOut(board.D17)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d6 = digitalio.DigitalInOut(board.D23)
lcd_d7 = digitalio.DigitalInOut(board.D18)


# Initialise the lcd class
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
                                      lcd_d7, lcd_columns, lcd_rows)

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

# looking for an active Ethernet or WiFi device
def find_interface():
    find_device = "ip addr show"
    interface_parse = run_cmd(find_device)
    for line in interface_parse.splitlines():
        if "state UP" in line:
            dev_name = line.split(':')[1]
    return dev_name

# find an active IP on the first LIVE network device
def parse_ip():
    find_ip = "ip addr show %s" % interface
    find_ip = "ip addr show %s" % interface
    ip_parse = run_cmd(find_ip)
    for line in ip_parse.splitlines():
        if "inet " in line:
            ip = line.split(' ')[5]
            ip = ip.split('/')[0]
    return ip

# run unix shell command, return as ASCII
def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output.decode('ascii')

lcd.clear()
sleep(2)
interface = find_interface()
ip_address = parse_ip()



leds = Led_utils()
leds.apagarLedsAutoEncendibles()
led = 1
while (led < 8):
    leds.encenderLed(led,True)
    sleep(0.2)
    led = led + 1

led = 1
while (led < 8):
    leds.encenderLed(led,False)
    sleep(0.2)
    led = led + 1
    
leds.encenderLed(4,True)

while True:

    # date and time
    lcd_line_1 = datetime.now().strftime('%b %d  %H:%M:%S\n')

    # current ip address
    lcd_line_2 = "IP " + ip_address

    # combine both lines into one update to the display
    lcd.message = lcd_line_1 + lcd_line_2

    sleep(1)
