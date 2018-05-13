#!/usr/bin/env python
import rospy
from std_msgs.msg import String


# Initialize the node with rosp
rospy.init_node('publisher_node')
# Create publisher
#publisher = rospy.Publisher("~topic",String,queue_size=1)
publisher = rospy.Publisher("/speaker",String,queue_size=10)
sentence = ''

# Define Timer callback
def callback1(event):
	msg = String()
	#msg.data = "%s is %s!" %(util.getName(),util.getStatus())
	msg.data = "I understand that you're angry"
	publisher.publish(msg)
# Read parameter
pub_period = rospy.get_param("~pub_period",5.0)
# Create timer
rospy.Timer(rospy.Duration.from_sec(pub_period),callback1)
# spin to keep the script for exiting
rospy.spin()

def callback2(data):
	rospy.loginfo(rospy.get_caller_id() + "I understand that you are %s", data.data)
    
	publisher.publish(msg)
    
def listener():

	# In ROS, nodes are uniquely named. If two nodes with the same
	# node are launched, the previous one is kicked off. The
	# anonymous=True flag means that rospy will choose a unique
	# name for our 'listener' node so that multiple listeners can
	# run simultaneously.
	rospy.init_node('listener', anonymous=True)

	rospy.Subscriber("/qt_face/setEmotion", String, callback2)

	# spin() simply keeps python from exiting until this node is stopped
	rospy.spin()

if __name__ == '__main__':
	listener()

