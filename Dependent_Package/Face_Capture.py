import numpy as np
import cv2
import os
from time import sleep

def capturingFace(usr_id):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # set buffer = 1
    cap.set(3,640) # set Width
    cap.set(4,480) # set Height
    minW = 0.1*cap.get(3)
    minH = 0.1*cap.get(4)

    face_cascade = cv2.CascadeClassifier('/home/pi/capstone/Cascade/frontface.xml')

    path = '/home/pi/capstone/Project/usr_faces'
    img_count = 0
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.5, 5,minSize=(int(minW), int(minH)))

        for (x,y,w,h) in faces:
            #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
            img_count += 1
            cv2.imwrite(os.path.join(path,'User.'+usr_id+'.'+str(img_count)+'.jpg'), gray[y:y+h,x:x+w])
        #cv2.imshow('frame', frame)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break
        if img_count >= 150:
            break
    cap.release()
    #cv2.destroyAllWindows()
    return True