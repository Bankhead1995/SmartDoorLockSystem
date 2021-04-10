import RPi.GPIO as GPIO
from time import sleep

class the_Lock:
    __Status = False
    __PIN = None
    __LED_R = None
    __LED_G = None

    def __init__(self, pin, led_r, led_g):
        GPIO.setmode(GPIO.BCM)
        self.__PIN = pin
        self.__LED_R = led_r
        self.__LED_G = led_g
        GPIO.setup(self.__PIN, GPIO.OUT, initial = GPIO.LOW)
        GPIO.setup(self.__LED_R, GPIO.OUT, initial = GPIO.HIGH)
        GPIO.setup(self.__LED_G, GPIO.OUT, initial = GPIO.LOW)

    def lock_ON(self):
        if self.__Status is not False:
            self.__Status = False
            GPIO.output(self.__PIN, self.__Status)
            GPIO.output(self.__LED_G, False)
            GPIO.output(self.__LED_R, True)
        return "DOOR LOCKED"

    def lock_OFF(self):
        if self.__Status is not True:
            self.__Status = True
            GPIO.output(self.__PIN, self.__Status)
            GPIO.output(self.__LED_G, True)
            GPIO.output(self.__LED_R, False)
        return "DOOR UNLOCKED"
    
    def lock__Status(self):
        if self.__Status:
            return "Door is unlocked"
        elif not self.__Status:
            return "Door is locked"
        else:
            return "ERROR"