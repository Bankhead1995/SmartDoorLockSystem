import RPi.GPIO as GPIO
from time import sleep

class BUZZER:
    __PIN = None
    def __init__(self, pin):
        self.__PIN = pin
        GPIO.setup(self.__PIN, GPIO.OUT, initial = GPIO.LOW)
    
    def BUZ_ON(self):
        GPIO.output(self.__PIN, True)
        sleep(0.2)
        GPIO.output(self.__PIN, False)
