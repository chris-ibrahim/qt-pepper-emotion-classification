#!/usr/bin/env python
import rospy
from std_msgs.msg import String

rate = rospy.rate(0.1)

def callback2(data):
	rospy.loginfo(rospy.get_caller_id() + "I understand that you are %s", data.data)
    
    
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
	rate.sleep()

if __name__ == '__main__':
	listener()

