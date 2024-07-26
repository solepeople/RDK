#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import time
from sensor_msgs.msg import Image
 
class NodePublisher(Node):
    def __init__(self,name):
        super().__init__(name)
        self.get_logger().info('hello%s!'% name)
        
def main(args=None):
    height = 480
    width =  640
    capture = cv2.VideoCapture(8)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)    
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))  
    rclpy.init()
    node = NodePublisher("Camera_image") 
    image_pub = node.create_publisher(Image,"image_data",10) 
    bridge = CvBridge() 
    while True:       
        ret, frame = capture.read()        
        frame = np.array(cv2.flip(frame,1))         
        data = bridge.cv2_to_imgmsg(frame,encoding="bgr8") 
        image_pub.publish(data) 