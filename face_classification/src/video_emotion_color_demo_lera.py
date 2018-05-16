#!/usr/bin/env python
import roslib
import rospy
import cv2
import sys

from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


import logging as log
import datetime as dt
from time import sleep

from statistics import mode
from keras.models import load_model
import numpy as np

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input


class image_converter:

  def __init__(self):
    rospy.init_node('image_converter', anonymous=True)
    
    rospy.loginfo("recognizer started")
    print "1................................................"
    
    self.bridge = CvBridge()

    self.image_pub = rospy.Publisher("/face_detection/image_raw",Image, queue_size=10)

    self.image_sub = rospy.Subscriber("/cv_camera/image_raw", Image, self.callback)

    self.detection_model_path = '../trained_models/detection_models/haarcascade_frontalface_default.xml'
    self.emotion_model_path = '../trained_models/emotion_models/fer2013_mini_XCEPTION.110-0.65.hdf5'
    self.emotion_labels = get_labels('fer2013')

    # hyper-parameters for bounding boxes shape
    self.frame_window = 10
    self.emotion_offsets = (20, 40)

    # loading models
    self.face_detection = load_detection_model(self.detection_model_path)
    self.emotion_classifier = load_model(self.emotion_model_path, compile=False)

    # getting input model shapes for inference
    self.emotion_target_size = self.emotion_classifier.input_shape[1:3]

    # starting lists for calculating modes
    self.emotion_window = []    
    

  def callback(self,data):
    try:
      bgr_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      print(e)



######################### Start the image processing
    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    faces = detect_faces(self.face_detection, gray_image)

    for face_coordinates in faces:

        x1, x2, y1, y2 = apply_offsets(face_coordinates, self.emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]
	
        try:
            gray_face = cv2.resize(gray_face, (self.emotion_target_size))
        except:
            continue

        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        print "start"
        print len(gray_face)
        
        print gray_face
        print "end"

        emotion_prediction = self.emotion_classifier.predict(gray_face)
        emotion_probability = np.max(emotion_prediction)
        emotion_label_arg = np.argmax(emotion_prediction)
        emotion_text = emotion_labels[emotion_label_arg]	
	print emotion_text
	print(emotion_probability)
	print('%')
        self.emotion_window.append(emotion_text)

	


        if len(self.emotion_window) > self.frame_window:
            self.emotion_window.pop(0)
        try:
            emotion_mode = mode(self.emotion_window)
        except:
            continue

        if emotion_text == 'angry':
            color = emotion_probability * np.asarray((255, 0, 0))
        elif emotion_text == 'sad':
            color = emotion_probability * np.asarray((0, 0, 255))
        elif emotion_text == 'happy':
            color = emotion_probability * np.asarray((255, 255, 0))
        elif emotion_text == 'surprise':
            color = emotion_probability * np.asarray((0, 255, 255))
        else:
            color = emotion_probability * np.asarray((0, 255, 0))

        color = color.astype(int)
        color = color.tolist()

        draw_bounding_box(face_coordinates, rgb_image, color)
        draw_text(face_coordinates, rgb_image, emotion_mode,
                  color, 0, -45, 1, 1)

    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    
######################### End the image processing	



    cv2.imshow("Image window", bgr_image)
    cv2.waitKey(3)

    try:
      self.image_pub.publish(self.bridge.cv2_to_imgmsg(bgr_image, "bgr8"))
    except CvBridgeError as e:
      print(e)

if __name__ == '__main__':
  rospy.loginfo("simple_face_detection ...........")
  print "................................................"
  ic = image_converter()
  
  
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print("Shutting down")
  cv2.destroyAllWindows()
 
