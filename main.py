from Device_Driver.peripheral_init import Initial_Peripheral
from Dependent_Package.Face_Trainner import trainner
from Dependent_Package.User_Data import Usr_Data
from Dependent_Package.T9 import T9_input
from datetime import datetime
import os
import time
import numpy as np
import cv2
import paho.mqtt.client as mqtt
from multiprocessing import Process, Queue, Manager, Value
import threading
#import threading, queue
from Dependent_Package.dataRewriter import server_addUser
from Dependent_Package.dataRewriter import server_modifyUserName
from Dependent_Package.dataRewriter import server_deleteUser
from Dependent_Package.dataRewriter import server_modifyUserPassword



sizeOfDataBase = 10

manager = Manager()
exit_flag = manager.Value('i', 0)
pause_flag = manager.Value('i',0)

LCD = Initial_Peripheral.LCD_SETUP()


KEYPAD = Initial_Peripheral.KEYPAD_SETUP()
BUZZER = Initial_Peripheral.Buzzer_SETUP()
FPS = Initial_Peripheral.FingerPrintSensor_SETUP()
LOCK = Initial_Peripheral.Lock_SETUP()

UserArray = np.empty(sizeOfDataBase, dtype= Usr_Data)
userCount = 0

mqttClient = mqtt.Client("theLock")
mqttClient.username_pw_set("lock","thisislock")

def on_connect(client, userdata, flags, rc):
    #0 connection success
    #4 wrong password/username
    #5 without autho
    print("Connection returned "+ str(rc))
    
def on_message(client, userdata, message):
    topic = message.topic
    fromWho = client.client_id
    msg = message.payload.decode(encoding='UTF-8')
    print("Message form "+str(fromWho)+"\nTopic as "+str(topic)+"\nMessage payload "+str(msg))

def connectionStatus(client, userdata, flags, rc):
    mqttClient.subscribe("rpi/lock")

def messageDecoder(client, userdata, msg):
    global pause_flag
    message = msg.payload.decode(encoding = 'UTF-8')
    print(message)
    info = message.split('/')
    print(info)
    #format
    #/  0   /    1   /   2   /     3     /       4         /
    #/modify/username/newname/newpassword/changefingerprint
    #/  add /username/newname/newpassword/
    #/delete/username/Deleteusername
    if info[0] == "modify":
        for i in UserArray:
            if i is not None and i.retUsrName() == info[1]:
                nameflag = False
                psdflag = False
                if info[2] != '*': #change user name
                    server_modifyUserName(i.retUsrName(),info[2],i.retPasscode())
                    i.changeName(info[2])
                if info[3] != '*': #change user password
                    server_modifyUserPassword(i.retUsrName(),info[3])
                    i.wirelessChangePasscode(info[3])
                if info[4] != '*': #change user finger print
                    # tell user putfinger on the sensor
                    pause_flag.value = 1
                    time.sleep(0.5)
                    FPS.delete(i.retUsrID())
                    while True:
                        LCD.clear()
                        LCD.write_string('Place your new finger on the sensor')
                        try:
                            FPS.changeFingerPrint(i.retUsrID())
                            LCD.clear()
                            LCD.write_string("please place your finger on the sensor for verify")
                            idTemp = FPS.IdentifyUser()
                            if idTemp == i.retUsrID():
                                LCD.clear()
                                LCD.write_string("Change successful")
                                time.sleep(1)
                                break
                            else:
                                LCD.clear()
                                LCD.write_string("try again")
                                time.sleep(1)
                        except:
                            LCD.clear()
                            LCD.write_string("something wrong, please try again")
                            time.sleep(1)
                            pass
                    pause_flag.value = 0
                    #FPS.set_Led()
                break
            #"No Match User"

    elif info[0] == "add":
        pause_flag.value = 1
        time.sleep(0.5)
        try:
            insertTemp = FPS.get_Next_Empty_Space()
            if UserArray[insertTemp] == None and insertTemp <= sizeOfDataBase:
                UserArray[insertTemp] = Usr_Data(True,LCD,FPS,info[2],info[3])
                LCD.clear()
                LCD.write_string("Enroll Succesful")
                userCount += 1
                time.sleep(1)
            else:
                raise ValueError("No Sapce")
        except:
            #No Space
            LCD.clear()
            LCD.write_string("No more sapce")
            time.sleep(1)
        pause_flag.value = 0

    elif info[0] == "delete":
        pause_flag.value = 1
        for i in UserArray:
            if i is not None and i.retUsrName() == info[2]:
                LCD.clear()
                LCD.write_string('Deleting user'+ info[2])
                delID = i.retUsrID()
                FPS.delete(delID)   #del finger
                imgPath = '/home/pi/capstone/Project/usr_faces/'
                for file in os.listdir(imgPath):
                    if file.startswith('User.'+str(delID)+'.'):
                        os.remove(os.path.join(imgPath+file))   #del img
                trainner() #retrainnng the trainner
                UserArray[delID] = None
                LCD.clear()
                LCD.write_string('Deleted successfully')
                userCount -= 1
                time.sleep(1)
        pause_flag.value = 0
    
    elif info[0] == "lock":
        if info[1] == "off":
            LOCK.lock_ON()
        else:
            LOCK.lock_OFF()
    else:
        print("error")
    
def service_on():
    mqttClient.on_connect = connectionStatus
    mqttClient.on_message = messageDecoder

    mqttClient.connect("127.0.0.1",port=1883)
    mqttClient.loop_start()

def showDNT(exit_flag, theQueue, pause_flag):
    print('showDNT process begin')
    while exit_flag.value == 0:
        Today = datetime.today().strftime("%B %d, %Y")
        Now = datetime.now().strftime("%H:%M:%S")
        LCD.clear()
        LCD.write_string(Today)
        LCD.crlf()
        LCD.write_string(Now)
        time.sleep(0.7)
        while pause_flag.value == 1:
            pass
    print('showDNT process terminate')

def isKeyPadPressed(exit_flag, theQueue, pause_flag):
    print('isKeyPadPressed process begin')
    while exit_flag.value == 0:
        if KEYPAD.getKey() is not None:
            theQueue.put(('Keypad',True))
        while pause_flag.value == 1:
            pass
    print('isKeyPadPressed process terminate')
    #print(exit_flag.value)

def isFingerPressed(exit_flag, theQueue, pause_flag):
    print('isFingerPressed process begin')
    
    while exit_flag.value == 0:
        FPS.set_Led()
        if FPS.is_Press_Finger() == 0:
            theQueue.put(('Finger',True))
        while pause_flag.value == 1:
            pass
    FPS.off_Led()
    print('isFingerPressed process terminate')

def FaceRecognizer(exit_flag, theQueue, pause_flag):
    print('FaceRecognizer process begin')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('/home/pi/capstone/Project/trainer/trainer.yml')

    face_cascade = cv2.CascadeClassifier('/home/pi/capstone/Cascade/frontface.xml')

    id = 0
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video widht
    cam.set(4, 480) # set video height

    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    recognizerCount = 0
    while exit_flag.value == 0:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5,minSize=(int(minW), int(minH)))
        for(x,y,w,h) in faces:
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            if (confidence < 65):
                if recognizerCount == 0:
                    idTemp1st = id
                elif recognizerCount == 20:
                    idTempLast = id
                recognizerCount += 1
            elif confidence >90:
                recognizerCount = 0
            if recognizerCount > 20:
                if idTemp1st == idTempLast:
                    theQueue.put(('Camera',idTemp1st))
                    break
                else:
                    recognizerCount = 0
        if pause_flag.value == 1:
            cam.release()
            while pause_flag.value == 1:
                pass
            cam = cv2.VideoCapture(0)
            cam.set(3, 640) # set video widht
            cam.set(4, 480) # set video height

            minW = 0.1*cam.get(3)
            minH = 0.1*cam.get(4)

    cam.release() 
    print('FaceRecognizer process terminate')

def setProcessFlag(exit_flag, theQueue):
    print('setProcessFlag process begin')
    while theQueue.empty():
        pass
    exit_flag.value = 1 
    print('setProcessFlag process terminate')

class verify():
    def PasscodeVerify():
        LCD.clear()
        LCD.write_string("Please enter your Passcode on keypad (4 digits):")
        LCD.crlf()
        passcodeTemp = ''
        while(len(passcodeTemp) < 4):
            keyinput = KEYPAD.getKey()
            if not keyinput in ('A','B','C','D','*','#',None):
                BUZZER.BUZ_ON()
                passcodeTemp += keyinput
                LCD.clear()
                LCD.write_string("Please enter your Passcode on keypad (4 digits):")
                LCD.crlf()
                for i in range(len(passcodeTemp)):
                    LCD.write_string('*')
        
        for i in UserArray:
            if i is not None and i.verifyPasscode(passcodeTemp):
                LCD.clear()
                LCD.write_string('Welcome')
                LCD.crlf()
                LCD.write_string(i.retUsrName())
                return True
        
        LCD.clear()
        LCD.write_string('PassCode Incorrect')
        time.sleep(1)
        return False

    def FingerPrintVerify():
        while True: 
            LCD.clear()
            LCD.write_string("Place finger on the sensor")
            try:
                pos = FPS.IdentifyUser()
                if  pos is not False:
                    LCD.clear()
                    LCD.write_string('Welcome')
                    LCD.crlf()
                    LCD.write_string(UserArray[pos].retUsrName())
                    return True
                else:
                    LCD.clear()
                    LCD.write_string('Finger is not recognized')
                    return False
            except:
                LCD.clear()
                LCD.write_string("Please try again")
                time.sleep(1.5)
    
    def FaceVerify(id):
        LCD.clear()
        LCD.write_string('Welcome')
        LCD.crlf()
        LCD.write_string(UserArray[id].retUsrName())

def FirstLevelMenu():
    startFirstLevel = time.time()
    waitingFirstlevel = 0
    while waitingFirstlevel < 10:
        if KEYPAD.getKey() == 'D':
            LCD.clear()
            LCD.write_string("1.Add New User")
            LCD.crlf()
            LCD.write_string("2.Delete User")
            LCD.crlf()
            LCD.write_string("3.Modify User")
            startTime = time.time()
            waitingTime = 0
            while waitingTime < 10:
                time.sleep(0.05)
                keyinput = KEYPAD.getKey()
                time.sleep(0.05)
                if keyinput in ('1', '2', '3'):
                    if keyinput is '1':
                        AddNewUserMenu()
                    elif keyinput is '2':
                        if userCount > 1:
                            DeleteUser()
                        else:
                            LCD.clear()
                            LCD.write_string('Failed')
                            LCD.crlf()
                            LCD.write_string('need atleast one file in the system')
                            time.sleep(1)
                    else:
                        ModifyUserMenu()
                    break
                waitingTime = time.time() - startTime
        waitingFirstlevel = time.time() - startFirstLevel
    
def AddNewUserMenu():
    global userCount
    try:
        insertTemp = FPS.get_Next_Empty_Space()
        if UserArray[insertTemp] == None and insertTemp <= sizeOfDataBase:
            UserArray[insertTemp] = Usr_Data(False,LCD,KEYPAD,BUZZER,FPS)
            LCD.clear()
            LCD.write_string("Enroll Succesful")
            userCount += 1
            time.sleep(2)
        else:
            raise ValueError("No Sapce")
    except:
        #No Space
        LCD.clear()
        LCD.write_string("No more sapce")
        time.sleep(2)
     
def DeleteUser():
    global userCount
    LCD.clear()
    LCD.write_string('Please enter the name wish to delete')
    delName = T9_input(LCD, KEYPAD,BUZZER)
    for i in UserArray:
        if i is not None and i.retUsrName() == delName:
            LCD.clear()
            LCD.write_string('Deleting')
            delID = i.retUsrID()
            FPS.delete(delID)   #del finger
            imgPath = '/home/pi/capstone/Project/usr_faces/'
            for file in os.listdir(imgPath):
                if file.startswith('User.'+str(delID)+'.'):
                    os.remove(os.path.join(imgPath+file))   #del img
            trainner() #retrainnng the trainner
            UserArray[delID] = None
            LCD.clear()
            LCD.write_string('Deleted successfully')
            userCount -= 1
            time.sleep(1)
            return True

    LCD.clear()
    LCD.write_string('No matched user')
    time.sleep(1)
    #no element as entered

def ModifyUserMenu():
    LCD.clear()
    LCD.write_string('Please enter the name wish to modify')
    time.sleep(0.3)
    ModName = T9_input(LCD, KEYPAD,BUZZER)
    for i in UserArray:
        if i is not None and i.retUsrName() == ModName:
            LCD.clear()
            LCD.write_string('Change:')
            LCD.crlf()
            LCD.write_string('1. User Name')
            LCD.crlf()
            LCD.write_string('2. Finger Print')
            LCD.crlf()
            LCD.write_string('3. Passcode')
            while True:
                key = KEYPAD.getKey()
                if key is '1':
                    LCD.clear()
                    LCD.write_string('Please enter new user name')
                    newName = T9_input(LCD,KEYPAD,BUZZER)
                    i.changeName(newName)
                    LCD.clear()
                    LCD.write_string('Hello ' + i.retUsrName())
                    time.sleep(1)
                    return True
                    
                elif key is '2':
                    try:
                        FPS.delete(i.retUsrID())
                        LCD.clear()
                        LCD.write_string('Place your new finger on the sensor')
                        FPS.changeFingerPrint(i.retUsrID())
                        LCD.clear()
                        LCD.write_string("please place your finger on the sensor for verify")
                        idTemp = FPS.IdentifyUser()
                        if idTemp == i.retUsrID():
                            LCD.clear()
                            LCD.write_string("Change successful")
                            time.sleep(1)
                            return True
                        else:
                            LCD.clear()
                            LCD.write_string("try again")
                            break
                    except:
                        LCD.clear()
                        LCD.write_string("try again")
                        break
                
                elif key is '3':
                    time.sleep(0.2)
                    i.changePasscode()
                    return True
    LCD.clear()
    LCD.write_string('No matched user')
    time.sleep(1)

def standByMode():
    """ manager = Manager()
    exit_flag = manager.Value('i', 0) """
    global manager
    global exit_flag
    global pause_flag
    exit_flag.value = 0
    theQueue = manager.Queue()
    ProcList = []
    ProcList.append(Process(target=showDNT, args=(exit_flag, theQueue, pause_flag)))
    ProcList.append(Process(target=isKeyPadPressed, args=(exit_flag, theQueue, pause_flag)))
    ProcList.append(Process(target=isFingerPressed, args=(exit_flag, theQueue, pause_flag)))
    ProcList.append(Process(target=FaceRecognizer, args=(exit_flag, theQueue, pause_flag)))
    ProcList.append(Process(target=setProcessFlag, args=(exit_flag, theQueue)))

    for P in ProcList:
        P.start()
    for P in ProcList:
        P.join()

    QueueTemp = theQueue.get()

    if QueueTemp[0] == 'Finger':
        print('Finger Print Sensor been pressed')
        return 'F'
    elif QueueTemp[0] == 'Keypad':
        print('Keypad been pressed')
        return 'K'
    elif QueueTemp[0] == 'Camera':
        print('Face Detected')
        print('User %d detected'%QueueTemp[1])
        return QueueTemp[1]
    else:
        print('UnKnown')
        return None

def main():
    service_on()
    AddNewUserMenu()
    while True: #stand by mode loop
        while True: #verify loop
            retTemp = standByMode()
            if retTemp is not None:
                if retTemp is 'F': #finger print
                    if verify.FingerPrintVerify():
                        LOCK.lock_OFF()
                        time.sleep(2)
                        LOCK.lock_ON()
                        break
                elif retTemp is 'K': #keypad
                    if verify.PasscodeVerify():
                        LOCK.lock_OFF()
                        time.sleep(2)
                        LOCK.lock_ON()
                        break
                else: #Face
                    verify.FaceVerify(retTemp)
                    LOCK.lock_OFF()
                    time.sleep(2)
                    LOCK.lock_ON()
                    break
        FirstLevelMenu()

if __name__ == "__main__":
    main()