#coding:utf-8
import requests
import json
import pyaudio
import wave
import rclpy
from rclpy.node import Node 
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import sys, select, termios, tty
 
APP_ID = '79219683'
API_KEY = 'A975f0VgjFAo37GWjk8QkBRp'
SECRET_KEY = '9NrWY3DSEMMf1V6D3cATsPiCfq3Fw7DY'

url = "https://aip.baidubce.com/oauth/2.0/token?client_id=A975f0VgjFAo37GWjk8QkBRp&client_secret=9NrWY3DSEMMf1V6D3cATsPiCfq3Fw7DY&grant_type=client_credentials"
payload = json.dumps("")
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
audio = pyaudio.PyAudio()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5 
NUM_RECORDINGS = 10  
WAVE_OUTPUT_FILENAME = "output.wav"
j=0
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()
def get():
        
    url = "https://vop.baidu.com/pro_api"
    
    payload = json.dumps({
        "format": "pcm",
        "rate": 16000,
        "channel": 1,
        "cuid": "Gjx8hLm5HYdMFfd9zQJkgIPSA9VwQ0R8",
        "token": get_access_token(),
        "dev_pid": 80001
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    print(response.text)
def record_audio(filename):
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("录音中...")
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束.")

    stream.stop_stream()
    stream.close()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
def vels(speed,turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)
    
def get_access_token():

    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('speech_cmd_vel')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10) 
        self.publisher_servo = self.create_publisher(String, 'servo_ctrl', 10)    
        speed = 0.2 #默认移动速度 m/s 0.2
        turn  = 0.43 #默认转向速度 rad/s 1
        Omni = 0 #非全向移动模式

        timer_period = 0.1  # seconds 50ms
        self.get_logger().info(vels(speed,turn)) #打印当前速度
        self.timer = self.create_timer(timer_period, self.timer_callback)   
        self.speed= speed
        self.turn = turn
        self.Omni=Omni
        self.x      = 0   #前进后退方向
        self.th     = 0   #转向/横向移动方向
        self.count  = 0   #键值不再范围计数
        self.target_speed = 0 #前进后退目标速度
        self.target_turn  = 0 #转向目标速度
        self.target_HorizonMove = 0 #横向移动目标速度
        self.control_speed = 0 #前进后退实际控制速度
        self.control_turn  = 0 #转向实际控制速度
        self.control_HorizonMove = 0 #横向移动实际控制速度    
    def timer_callback(self):
            try:      
                print(f"第{j+1}录音")
                record_audio(WAVE_OUTPUT_FILENAME)
                response = get()
                print(response)
                err_no=result['err_no']
                if(err_no==0):
                    result=response.text
                    print("识别结果:", result)
                    print()  
                    if '前进' in result:
                        print('1')
                        self.x  = 1
                        self.th = 0
                        self.count = 0
                    if '后退' in result:
                        self.x  = -1
                        self.th = 0
                        self.count = 0
                    if '左转' in result:
                        self.x  = 0
                        self.th = 1
                        self.count = 0
                    if '右转' in result:
                        self.x  = 0
                        self.th = -1
                        self.count = 0
                    #机械臂夹取
                    self.s  = ''  
                    if '夹取'in result:  
                        self.s  ='crawl'
                    if '放下'in result: 
                        self.s  ='putdown'
                    #根据速度与方向计算目标速度
                    self.target_speed = self.speed * self.x
                    self.target_turn  = self.turn * self.th
                    self.target_HorizonMove = self.speed*self.th
                    
                    #平滑控制，计算前进后退实际控制速度
                    if self.target_speed > self.control_speed:
                        self.control_speed = min( self.target_speed, self.control_speed + 0.1 )
                    elif self.target_speed < self.control_speed:
                        self.control_speed = max( self.target_speed, self.control_speed - 0.1 )
                    else:
                        self.control_speed = self.target_speed
                        
                    # print("self.target_speed:%s ",self.target_speed)
                    #平滑控制，计算转向实际控制速度
                    if self.target_turn > self.control_turn:
                        self.control_turn = min( self.target_turn, self.control_turn + 0.5 )
                    elif self.target_turn < self.control_turn:
                        self.control_turn = max( self.target_turn, self.control_turn - 0.5 )
                    else:
                        self.control_turn = self.target_turn

                    #平滑控制，计算横向移动实际控制速度
                    if self.target_HorizonMove > self.control_HorizonMove:
                        self.control_HorizonMove = min( self.target_HorizonMove, self.control_HorizonMove + 0.1 )
                    elif self.target_HorizonMove < self.control_HorizonMove:
                        self.control_HorizonMove = max( self.target_HorizonMove, self.control_HorizonMove - 0.1 )
                    else:
                        self.control_HorizonMove = self.target_HorizonMove
                
                    twist = Twist() #创建ROS速度话题变量
                    string = String()
                    #根据是否全向移动模式，给速度话题变量赋值
                    if self.Omni==0:
                        twist.linear.x  = self.control_speed; twist.linear.y = 0.0;  twist.linear.z = 0.0
                        twist.angular.x = 0.0;             twist.angular.y = 0.0; twist.angular.z = self.control_turn
                    else:
                        twist.linear.x  = self.control_speed; twist.linear.y = self.control_HorizonMove; twist.linear.z = 0.0
                        twist.angular.x = 0.0;             twist.angular.y = 0.0;                  twist.angular.z = 0.0

                    self.publisher_.publish(twist) #ROS发布速度话题
                    if self.s != '':            
                        string.data=self.s
                        self.publisher_servo.publish(string) #ROS发布速度话题
                    

            #运行出现问题则程序终止并打印相关错误信息
            except Exception as e:
                self.get_logger().warn(e)
                twist = Twist()
                twist.linear.x = 0.0;  twist.linear.y = 0.0;  twist.linear.z = 0.0
                twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = 0.0
                self.publisher_.publish(twist)
                audio.terminate()    




def main(args=None):
    rclpy.init(args=args) 
    minimal_publisher = MinimalPublisher() 
    rclpy.spin(minimal_publisher) 
    minimal_publisher.destroy_node()
    audio.terminate() 
    rclpy.shutdown()
 
 
if __name__ == '__main__':
    main()
