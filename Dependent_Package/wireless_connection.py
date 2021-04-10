import paho.mqtt.client as mqtt

brockerAddr = "192.168.50.128"
port  = 1883
clientName = "theLock"
username = "lock"
passwd = "thisislock"

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
                    server_modifyUserName(i.retUsrName,info[2])
                    i.changeName(info[2])
                if info[3] != '*': #change user password
                    server_modifyUserPassword(i.retUsrName,info[3])
                    i.wirelessChangePasscode(info[3])
                if info[4] != '*': #change user finger print
                    # tell user putfinger on the sensor
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
                        else:
                            LCD.clear()
                            LCD.write_string("try again")
                    except:
                        LCD.clear()
                        LCD.write_string("try again")
                break
            #"No Match User"
            elif info[0] == "add":
                break
            elif info[0] == "delete":
                break
            else:
                print("error")
    
def service_on_temp():
    mqttClient.on_connect = connectionStatus
    mqttClient.on_message = messageDecoder

    mqttClient.connect("192.168.50.128",port=1883)
    mqttClient.loop_start()