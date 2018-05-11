#!/usr/bin/env python
import rospy
from object_detector_ros_app import util
from std_msgs.msg import String
from optparse import OptionParser


# Initialize the node with rosp
rospy.init_node('publisher_node')
# Create publisher
#publisher = rospy.Publisher("~topic",String,queue_size=1)
publisher = rospy.Publisher("/otherspeaker",String,queue_size=10)
publisher2 = rospy.Publisher("/speaker",String,queue_size=10)

# Define Timer callback
def callback1(event):
	msg = String()
	#msg.data = "%s is %s!" %(util.getName(),util.getStatus())
	msg.data = "Oh no!"
	publisher2.publish(msg)

def callback2(event):
	msg = String()
	#msg.data = "%s is %s!" %(util.getName(),util.getStatus())
	msg.data = "I understand that " + "as mad as " + "you're angry"
	publisher.publish(msg)

# Read parameter
pub_period = rospy.get_param("~pub_period",3.0)
# Create timer
rospy.Subscriber("/otherspeaker", String, callback1)
rospy.Timer(rospy.Duration.from_sec(pub_period),callback2)
# spin to keep the script for exiting
#rospy.sleep(5)
#msg = String()
#msg.data = "%s is %s!" %(util.getName(),util.getStatus())
#msg.data = "I understand that you're angry"
#publisher.publish(msg)
rospy.spin()
