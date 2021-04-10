import cv2
import numpy as np
from PIL import Image
import os

Path = '/home/pi/capstone/Project/usr_faces'

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier("/home/pi/capstone/Cascade/frontface.xml")

def __getImgsAndLabels(path):
    imgPaths = [os.path.join(path,f) for f in os.listdir(path)]
    faceSamples = []
    ids = []

    for imgPath in imgPaths:
        PIL_img =  Image.open(imgPath).convert('L')
        img_Array = np.array(PIL_img, 'uint8')
        
        id = int(os.path.split(imgPath)[-1].split('.')[1])
        faces = detector.detectMultiScale(img_Array)

        for (x,y,w,h) in faces:
            faceSamples.append(img_Array[y:y+h,x:x+w])
            ids.append(id)
    
    return faceSamples, ids

def trainner():
    #print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces,ids = __getImgsAndLabels(Path)
    recognizer.train(faces, np.array(ids))

    # Save the model into trainer/trainer.yml
    recognizer.write('/home/pi/capstone/Project/trainer/trainer.yml') 

    # Print the numer of faces trained and end program
    #print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
