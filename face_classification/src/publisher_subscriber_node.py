#!/usr/bin/env python
import rospy
from object_detector_ros_app import util
from std_msgs.msg import String
from optparse import OptionParser

#This programs enables QT to say the emotion he is observing

# Initialize the node with rosp
rospy.init_node('publisher_subscriber_node')

# Create publisher
publisher = rospy.Publisher("/speech",String,queue_size=10)

# Define Timer callback
def callback(data):
	msg = String()
	rospy.sleep(5.0)
	msg.data = "I understand that you are " + data.data
	publisher.publish(msg)

def listener():
	# spin to keep the script for exiting
	# Create timer
	rospy.Subscriber("/qt_face/setEmotion", String, callback)
	rospy.spin()

if __name__ == '__main__':
    listener()
