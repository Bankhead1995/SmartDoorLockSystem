import paho.mqtt.client as mqtt
from .T9 import T9_input
from .Face_Capture import capturingFace
from .Face_Trainner import trainner
from time import sleep
import os

class Usr_Data:
    __userID = None
    __userName = ''
    __userPassCode = ''
    __LCD = None
    __KEYPAD = None
    __BUZZER = None
    __FPS = None

    """ def __init__(self, lcd, keypad, buzzer ,fps, mobile_flag):
        self.__LCD = lcd
        self.__KEYPAD = keypad
        self.__BUZZER = buzzer
        self.__FPS = fps
        if not mobile_flag
            self.__nameEnroll()
            self.__passcodeEnroll()
            self.__fingerPrintEnroll()
            self.__faceEnroll()
            self.__enrollUserIntoServer() """
    def __init__(self, *args):
        if not args[0]:
            self.__LCD = args[1]
            self.__KEYPAD = args[2]
            self.__BUZZER = args[3]
            self.__FPS = args[4]
            self.__nameEnroll()
            self.__passcodeEnroll()
            self.__fingerPrintEnroll()
            self.__faceEnroll()
            self.__enrollUserIntoServer()
        #when register from mobile
        #mobile_flag | LCD | FPS | username | passcode | 
        if args[0]:
            self.__LCD = args[1]
            self.__FPS = args[2]
            self.__userName = args[3]
            self.__userPassCode = args[4]
            self.__fingerPrintEnroll()
            self.__faceEnroll()
            self.__enrollUserIntoServer()
        
    def __nameEnroll(self):
        self.__LCD.clear()
        self.__LCD.write_string('Pleae enter your name ')
        self.__userName = T9_input(self.__LCD, self.__KEYPAD,self.__BUZZER)
        self.__LCD.clear()
        self.__LCD.write_string("Hi "+self.__userName)
        sleep(1)

    def __passcodeEnroll(self):
        verifyPasscodeFlag = False
        while not verifyPasscodeFlag:   
            passcodeTemp = ''
            verifyPasscode = ''
            verifyPasscodeFlag = False
            keyinput = ''
    
            self.__LCD.clear()
            self.__LCD.write_string("Please enter your Passcode on keypad (4 digits):")
            self.__LCD.crlf()
            while(len(passcodeTemp) < 4):
                keyinput = self.__KEYPAD.getKey()
                if keyinput is not None and keyinput is not 'A' and keyinput is not 'B' and keyinput is not 'C' and keyinput is not 'D' and keyinput is not '#' and keyinput is not '*':
                    self.__BUZZER.BUZ_ON()
                    passcodeTemp += keyinput
                    self.__LCD.clear()
                    self.__LCD.write_string("Please enter your Passcode on keypad (4 digits):")
                    self.__LCD.crlf()
                    for i in range(len(passcodeTemp)):
                        self.__LCD.write_string('*')

            self.__LCD.clear()
            self.__LCD.write_string("Please enter again for verify your passcode")
            self.__LCD.crlf()   
            while(len(verifyPasscode) < 4):   
                keyinput = self.__KEYPAD.getKey()
                if keyinput is not None and keyinput is not 'A' and keyinput is not 'B' and keyinput is not 'C' and keyinput is not 'D' and keyinput is not '#' and keyinput is not '*':
                    self.__BUZZER.BUZ_ON()
                    verifyPasscode += keyinput
                    self.__LCD.clear()
                    self.__LCD.write_string("Please enter again for verify your passcode")
                    self.__LCD.crlf()
                    for i in range(len(verifyPasscode)):
                        self.__LCD.write_string('*')
                
                if len(verifyPasscode) is 4:
                    if verifyPasscode == passcodeTemp:
                        self.__LCD.clear()
                        self.__LCD.write_string('Verification successful')
                        sleep(1)
                        verifyPasscodeFlag = True
                        self.__userPassCode = passcodeTemp
                    else:
                        self.__LCD.clear()
                        self.__LCD.write_string('Verification failed please re-enter passcode')
                        sleep(2)
    
    def __fingerPrintEnroll(self):
        while (True):
            self.__LCD.clear()
            self.__LCD.write_string('Put your finger three times at the scanner to enroll')
            try:
                usrID_Temp = self.__FPS.enrollUser()
                if usrID_Temp is not False:
                    self.__LCD.clear()
                    self.__LCD.write_string("Finger enroll successful")
                    self.__userID = usrID_Temp
                    sleep(1)
                    break
            except :
                self.__LCD.clear()
                self.__LCD.write_string("Please Try again")
                sleep(1.5)
                pass
    
    def __faceEnroll(self):
        while True:
            self.__LCD.clear()
            self.__LCD.write_string("Lets enroll your face")
            if capturingFace(str(self.__userID)):
                self.__LCD.clear()
                self.__LCD.write_string("please wait...")
                trainner()
                self.__LCD.clear()
                self.__LCD.write_string("Face enrolled successful")
                sleep(1)
                break
            else:
                self.__LCD.clear()
                self.__LCD.write_string("Face enroll failed")
                sleep(1)
    
    def retUsrID(self):
        return self.__userID
    
    def retUsrName(self):
        return self.__userName
    
    def changeName(self, newName):
        self.__userName = newName
    
    def changePasscode(self):
        self.__passcodeEnroll()
    
    def wirelessChangePasscode (self, newPasscode):
        self.__userPassCode = newPasscode

    def verifyPasscode(self, vfpc):
        if vfpc == self.__userPassCode:
            return True
        else:
            return False
    
    def __enrollUserIntoServer(self):
        os.chdir('/etc/mosquitto/')
        os.system('echo %s|sudo -S %s' % ('lock', 'mosquitto_passwd -b passwd '+self.__userName+' '+self.__userPassCode))
        os.system('echo %s|sudo -S %s' % ('lock', 'systemctl restart mosquitto.service'))
    
    def retPasscode(self):
        return self.__userPassCode