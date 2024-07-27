# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import signal

import smbus,time

bus = smbus.SMBus(0) # start comm with i2c bus

def PCA9685_Write(addr,data):
    bus.write_byte_data(PCA_Addr,addr,data)
    
def PCA9685_Read(addr):
    value = bus.read_byte_data(PCA_Addr,addr)
    return value
    
def PCA9685_setPWM(num,on,off):
    # data = [hex(on&0xFF),hex(on>>8),hex(off&0xFF),hex(off>>8)]
    data1 = int(on) & 0xFF
    data2 = int(on) >> 8
    data3 = int(off) & 0xFF
    data4 = int(off) >> 8
    bus.write_i2c_block_data(PCA_Addr,LED0_ON_L+4*num,[data1,data2,data3,data4])
    

def PCA9685_setFreq(Freq):
    # Freq *= 0.98
    prescaleval = 25000000
    prescaleval /= 4096
    prescaleval /= Freq
    prescaleval -= 1
    prescale = round(prescaleval)
    oldmode = PCA9685_Read(PCA_Model)
    
    newmode = (oldmode&0x7F)|0x10
    PCA9685_Write(PCA_Model,newmode)
    PCA9685_Write(PCA_Pre,prescale)
    PCA9685_Write(PCA_Model,oldmode)
    time.sleep(0.005)
    PCA9685_Write(PCA_Model,oldmode|0xa1)
    
def PCA9685_setAngle(num,angle):
    off = 158 + angle*2.2
    PCA9685_setPWM(num,0,off)

def PCA9685_Init(Freq, Angle):
    off = 0
    
    PCA9685_Write(0,0)
    PCA9685_setFreq(Freq)
   
    off = 103 + Angle*1.14  
    
    PCA9685_setPWM(0,0,158 + 170*2.2 )
    PCA9685_setPWM(1,0,158 + 170*2.2 )
    PCA9685_setPWM(2,0,158 + 120*2.2 )
    PCA9685_setPWM(3,0,158 + 30*2.2 )
    PCA9685_setPWM(4,0,158 + 0*2.2)
    PCA9685_setPWM(5,0,158 + 0*2.2)
    PCA9685_setPWM(6,0,off)
    PCA9685_setPWM(7,0,off)
    PCA9685_setPWM(8,0,off)
    PCA9685_setPWM(9,0,off)
    PCA9685_setPWM(10,0,off)
    PCA9685_setPWM(11,0,off)
    PCA9685_setPWM(12,0,off)
    PCA9685_setPWM(13,0,off)
    PCA9685_setPWM(14,0,off)
    PCA9685_setPWM(15,0,off)
    time.sleep(0.1)

# def Crawl_action(second,times):
#     ctrl_time = second / times
#     Now_angle = [170, 30, 170, 120]
#     Target_angle = [60, 60, 170, 60]

#     for i in range(0,times):
#         PCA9685_setAngle(0,Now_angle[0] + (Target_angle[0] - Now_angle[0]) / times * i)
#         PCA9685_setAngle(1,Now_angle[1] + (Target_angle[1] - Now_angle[1]) / times * i)
#         PCA9685_setAngle(0,Now_angle[2] + (Target_angle[2] - Now_angle[2]) / times * i)
#         PCA9685_setAngle(0,Now_angle[3] + (Target_angle[3] - Now_angle[3]) / times * i)
#         time.sleep(ctrl_time)

def Crawl_action():
    PCA9685_setAngle(0,100) # 伸爪
    PCA9685_setAngle(3,60)
    PCA9685_setAngle(2,60)
    time.sleep(0.5)
    PCA9685_setAngle(0,60) # 向下
    time.sleep(0.5)
    PCA9685_setAngle(2,120) # 闭合爪
    time.sleep(0.5)
    PCA9685_setAngle(0,170) # 向上
    time.sleep(0.5)

def putdown_action():
    PCA9685_setAngle(0,100) # 伸爪
    PCA9685_setAngle(3,30) 
    time.sleep(0.5)
    PCA9685_setAngle(2,60) # 张开爪
    time.sleep(0.5)

def reset_action():
    PCA9685_setAngle(0,170) # 复位
    PCA9685_setAngle(3,30) 
    PCA9685_setAngle(1,170) 
    PCA9685_setAngle(2,120) 
    time.sleep(0.5)


PCA_Addr    = 0x41
LED0_ON_L   = 0x06
LED0_ON_H   = 0x07
LED0_OFF_L  = 0x08
LED0_OFF_H  = 0x09
PCA_Model   = 0x00
PCA_Pre     = 0xFE

class ServoSubscriber(Node):
    def __init__(self):
        super().__init__('Servo_subscriber')
        self.subscription = self.create_subscription(
            String,
            'servo_ctrl',
            self.servo_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.get_logger().info('servo start')

    def servo_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)
        if msg.data == "crawl":
            Crawl_action()
        if msg.data == "putdown":
            putdown_action()
            reset_action()
def signal_handler(signal, frame):
    rclpy.shutdown()
    sys.exit(0)
def main(args=None):
    rclpy.init(args=args)
    PCA9685_Init(50,360)
    signal.signal(signal.SIGINT, signal_handler)
    Servo_subscriber = ServoSubscriber()
    rclpy.spin(Servo_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    Servo_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()