#!/usr/bin/env python
import rospy
import sys
# Ros Messages
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
# We do not use cv_bridge it does not support CompressedImage in python
# from cv_bridge import CvBridge, CvBridgeError

from statistics import mode
import cv2
from keras.models import load_model
import numpy as np

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input

class PepperEmotionListener:

	def __init__(self):
		# parameters for loading data and images
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

		# Initialize the node with rosp
		rospy.init_node('publisher_node')
		self.emotion_publisher = rospy.Publisher("/qt_face/setEmotion",String,queue_size=10)
		self.speech_publisher = rospy.Publisher("/speaker",String,queue_size=10)
		self.emotion_msg = String()
		self.speech_msg = String()

		# starting video streaming
		cv2.namedWindow('window_frame')
		#video_capture = cv2.VideoCapture(0)
		print "init!"
		rospy.Subscriber("/naoqi_driver/camera/front/image_raw/compressed", CompressedImage, self.callback, queue_size = 1)

	def callback(self,data):#### direct conversion to CV2 ####
		print "callback!"
		np_arr = np.fromstring(data.data, np.uint8)
		print np_arr
		#bgr_image = cv2.imdecode(np_arr, cv2.CV_LOAD_IMAGE_COLOR)
		bgr_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # OpenCV >= 3.0:
		print bgr_image

		#cam_image = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8)
		gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
		rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
		faces = detect_faces(self.face_detection, gray_image)
		print "to the for loop!"
		print faces

		for face_coordinates in faces:
			print "inside the for loop!"
			print face_coordinates

			x1, x2, y1, y2 = apply_offsets(face_coordinates, self.emotion_offsets)
			gray_face = gray_image[y1:y2, x1:x2]
			print gray_face

			print "inside the for loop, just before the try except!"
			try:
				gray_face = cv2.resize(gray_face, (self.emotion_target_size))
			except:
				continue
			print "inside the for loop, after the try except!"

			gray_face = preprocess_input(gray_face, True)
			gray_face = np.expand_dims(gray_face, 0)
			gray_face = np.expand_dims(gray_face, -1)
			emotion_prediction = self.emotion_classifier.predict(gray_face)
			emotion_probability = np.max(emotion_prediction)
			emotion_label_arg = np.argmax(emotion_prediction)
			emotion_text = emotion_labels[emotion_label_arg]	
			print emotion_text
			print(emotion_probability)
			print('%')
			emotion_window.append(emotion_text)

	
			self.emotion_msg.data = emotion_text
			self.emotion_publisher.publish(emotion_msg)
			self.speech_msg.data = 'I see that you are ' + emotion_text
			#self.speech_publisher.publish(speech_msg)

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

		
		print "after the for loop"
		bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
		print rgb_image
		print bgr_image
		cv2.imshow('window_frame', bgr_image)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			return


def main(argv):
	PepperEmotionListener()
	try:
		rospy.spin()
    	except KeyboardInterrupt:
		print "Shutting down ROS Image feature detector module"
    	cv2.destroyAllWindows()




if __name__ == '__main__':
	main(sys.argv)
