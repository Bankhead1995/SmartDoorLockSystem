from . import GT_521F52
from . import solenoid_lock
from . import buzzer
import RPi.GPIO as GPIO
from pad4pi import rpi_gpio
from RPLCD.gpio import CharLCD

class Initial_Peripheral:
    GPIO.setwarnings(False)
    #initial Keypad
    def KEYPAD_SETUP():
        KEYPAD = [["1", "2", "3", "A"],
                ["4", "5", "6", "B"],
                ["7", "8", "9", "C"],
                ["*", "0", "#", "D"]]
        ROW_PINS = [18, 27, 22, 23]
        COL_PINS = [4, 5, 6, 17]
        return rpi_gpio.KeypadFactory().create_keypad(keypad = KEYPAD, row_pins = ROW_PINS, col_pins = COL_PINS)

    #initial LCD
    def LCD_SETUP():
        PIN_RS = 10
        PIN_RW = 9
        PIN_E = 11
        PINS_DATA = [12, 16, 20, 21] #D4, D5, D6, D7
        return CharLCD(pin_rs = PIN_RS, pin_rw  = PIN_RW, pin_e = PIN_E, pins_data = PINS_DATA, numbering_mode = GPIO.BCM, cols = 20, rows = 4, dotsize = 8, charmap = 'A02', auto_linebreaks = True)

    #initial FingerPrintSensor
    def FingerPrintSensor_SETUP():
        try:
            F = GT_521F52.PyFingerprint_GT_521F52('/dev/ttyS0')
            F.delete_all()
        except Exception as e:
            print('Exception message: ' + str(e))
        return F

    #initial Lock
    def Lock_SETUP():
        PIN_LOCK = 26
        PIN_LED_R = 19
        PIN_LED_G = 13
        return solenoid_lock.the_Lock(PIN_LOCK, PIN_LED_R, PIN_LED_G)

    #initial buzzer
    def Buzzer_SETUP():
        PIN_Buzzer = 24
        return buzzer.BUZZER(24)