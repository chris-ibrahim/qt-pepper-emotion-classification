#!/usr/bin/env python
import rospy
from object_detector_ros_app.msg import object_detector1

import rospy
import os
import cv2
import time
import argparse
import multiprocessing
import numpy as np
import tensorflow as tf

import utils.app_utils
import object_detection.anchor_generators.grid_anchor_generator
from object_detector_ros_app import util 
from utils.app_utils import FPS, WebcamVideoStream
from multiprocessing import Queue, Pool
from utils import label_map_util
from utils import visualization_utils as vis_util

def talker():
    pub = rospy.Publisher('custom_chatter', object_detector1)
    rospy.init_node('custom_talker', anonymous=True)
    r = rospy.Rate(1) #10hz
    msg = object_detector1()
    msg.nomA = "ROS User"
    msg.humeurA = "content"

    while not rospy.is_shutdown():
        rospy.loginfo(msg)
        pub.publish(msg)
        r.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException: pass

