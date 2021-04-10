import cv2
import numpy as np
import os
import queue

def FaceRecognizer(q):
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
    while True:
        if q.empty():
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
                        q.put(('Camera',idTemp1st))
                        break
                    else:
                        recognizerCount = 0
        else:
            break
    cam.release() 

