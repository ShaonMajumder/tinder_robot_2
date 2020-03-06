from shutil import copyfile,move
import cv2
import numpy as np
import imutils
import os
import time

folders = {
    'images_folder' : 'private/data',
    'face_found_image_path' : "private/data/faces/",
    'face_not_found_image_path' : "private/data/not_faces/"
}

def try_creating_folders():
    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)

face_found_folders = {
    'dnn_image_path' : 'dnn1',
    'rotated_haarcascade_frontalface_alt_image_path' : 'rotated_haarcascade_frontalface_alt',
    'haarcascade_frontalface_alt_image_path' : 'haarcascade_frontalface_alt'
}


    #os.mkdir(face_found_image_path+haarcascade_frontalface_alt_image_path)
    #os.mkdir(face_found_image_path+rotated_haarcascade_frontalface_alt_image_path)
    #os.mkdir(face_found_image_path+dnn_image_path)



haar_face_cascade = cv2.CascadeClassifier('resources/models/haarcascade_frontalface_alt.xml')
#enter_key = u'\ue007'

dnn_face_confidence_threshold = 0.6
face_prototxt  = "D:/D/work/Automation/tinder_robot/resources/models/deploy_face.prototxt"
face_model_name = "D:/D/work/Automation/tinder_robot/resources/models/facenetres10_300x300_ssd_iter_140000.caffemodel"



def face_detection_dnn(image_name,confidence_threshold):
    image = cv2.imread(image_name)
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

    # pass the blob through the network and obtain the detections and
    # predictions
    print("[INFO] computing object detections...")
    # load our serialized model from disk
    face_net = cv2.dnn.readNetFromCaffe(face_prototxt, face_model_name)    
    face_net.setInput(blob)

    detections = face_net.forward()
    
    
    face_count = 0
    confidence_list = []
    face_coordinates = []
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > confidence_threshold:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            face_coordinates.append(box.astype("int"))
            confidence_list.append(confidence)
            face_count = face_count + 1

    print(face_coordinates)
    return face_count,confidence_list



def face_detection_haarcascade(image_file):
    "haarcascade_1"
    if(isinstance(image_file,np.ndarray)):
        test1 = image_file
    else:
        test1 = cv2.imread(image_file)

    gray_img = cv2.cvtColor(test1, cv2.COLOR_BGR2GRAY)
    # For brightness standardization or additional standardization - then  to apply Histogram  Equalization  [8] as  a very  simple  method  of  automatically standardizing  the  brightness  and contrast of your facial images.
    # edge or contour detection

    faces = haar_face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5);
    return len(faces)

def try_detect_face_algorithms(image_name,mode=""):
    confidence_list = [0]
    
    image = cv2.imread(image_name)
    
    if mode == "recheck":
        angles = list(np.arange(20, 75, 20))+list(360- np.arange(20, 75, 20))
        #[20, 40, 60, 340, 320, 300]
    else:
        angles = list(np.arange(0, 75, 20))+list(360- np.arange(20, 75, 20))
        #[0, 20, 40, 60, 340, 320, 300]
    faces = 0
    cindex = 0
    
    while faces == 0:
        if(cindex<len(angles)):
            #rotate and apply haarcascade_frontalface_alt method
            angle = angles[cindex]
            rotated = imutils.rotate_bound(image, angle)
            faces = face_detection_haarcascade(image)
            algorithm_name = 'haarcascade_frontalface_alt' if angle == 0  else "rotated_haarcascade_frontalface_alt"
            cindex += 1
            if angle == 0:
                print("[INFO] Trying haarcascade_frontalface_alt")
            else:
                print("[INFO] Trying haarcascade_frontalface_alt at rotation")

        else:
            faces,confidence_list = face_detection_dnn(image_name,dnn_face_confidence_threshold)
            algorithm_name = 'dnn_caffe' if faces != 0 else "None"
            print("[INFO] Trying deep neural network Caffe model")
            break
    
    return faces,algorithm_name,confidence_list
    


def store_classfying_image(faces,algorithm_name,source_image):
    if(faces > 0):
        if algorithm_name == 'dnn_caffe':
            path = folders['face_found_image_path']+face_found_folders['dnn_image_path']+source_image
        elif algorithm_name == 'rotated_haarcascade_frontalface_alt':
            path = folders['face_found_image_path']+face_found_folders['rotated_haarcascade_frontalface_alt_image_path']+source_image
        elif algorithm_name == 'haarcascade_frontalface_alt':
            path = folders['face_found_image_path']+face_found_folders['haarcascade_frontalface_alt_image_path']+source_image
    else:
        path = folders['face_not_found_image_path']+source_image
    
    #copyfile(source_image, path)




