import rclpy
from rclpy.node import Node 
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import sys, select, termios, tty
 
 
msg = """
Control Your Robot!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
space key, k : force stop
anything else : stop smoothly
b : switch to OmniMode/CommonMode
CTRL-C to quit
"""

#键值对应移动/转向方向
moveBindings = {
        'i':( 1, 0),
        'o':( 1,-1.5),
        'j':( 0, 1),
        'l':( 0,-1),
        'u':( 1, 1.5),
        ',':(-1, 0),
        '.':(-1, 1),
        'm':(-1,-1),
           }

#键值对应速度增量
speedBindings={
        'q':(1.1,1.1),
        'z':(0.9,0.9),
        'w':(1.1,1),
        'x':(0.9,1),
        'e':(1,  1.1),
        'c':(1,  0.9),
          }
settings = termios.tcgetattr(sys.stdin) #获取键值初始化，读取终端相关属性
#获取键值函数
def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

#以字符串格式返回当前速度
def vels(speed,turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)
 

class MinimalPublisher(Node):
 
    def __init__(self):
        super().__init__('send_cmd_vel')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10) 
        self.publisher_servo = self.create_publisher(String, 'servo_ctrl', 10)    
       
        speed = 0.2 #默认移动速度 m/s 0.2
        turn  = 0.43 #默认转向速度 rad/s 1
        Omni = 0 #非全向移动模式

        timer_period = 0.1  # seconds 50ms
        self.get_logger().info(msg) #打印控制说明
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
            key = getKey() #获取键值
            if key!='':
                self.get_logger().info(key) #打印控制说明
            #切换是否为全向移动模式，全向轮/麦轮小车可以加入全向移动模式
            if key=='b':               
                self.Omni=~self.Omni
                if self.Omni: 
                    print("Switch to OmniMode")
                    moveBindings['.']=[-1,-1]
                    moveBindings['m']=[-1, 1]
                else:
                    print("Switch to CommonMode")
                    moveBindings['.']=[-1, 1]
                    moveBindings['m']=[-1,-1]
            
            #判断键值是否在移动/转向方向键值内
            if key in moveBindings.keys():
                self.x  = moveBindings[key][0]
                self.th = moveBindings[key][1]
                self.count = 0
            #机械臂夹取
            self.s  = ''   #机械臂控制
            if key=='y':  
                self.s  ='crawl'
            if key=='t':  
                self.s  ='putdown'
               
            #判断键值是否在速度增量键值内
            elif key in speedBindings.keys():
                self.speed = self.speed * speedBindings[key][0]
                self.turn  = self.turn  * speedBindings[key][1]
                self.count = 0
                self.get_logger().info(vels(self.speed,self.turn)) #速度发生变化，打印出来
            #空键值/'k',相关变量置0
            elif key == ' ' or key == 'k' :
                self.x  = 0
                self.th = 0
                self.control_speed = 0
                self.control_turn  = 0
            #长期识别到不明键值，相关变量置0
            else:
                self.count = self.count + 1
                if self.count > 4:
                    self.x  = 0
                    self.th = 0
                if (key == '\x03'):  #ctrl+c
                    rclpy.shutdown()

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

        #程序结束前发布速度为0的速度话题
        # finally:
        #     twist = Twist()
        #     twist.linear.x = 0.0;  twist.linear.y = 0.0;  twist.linear.z = 0.0
        #     twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = 0.0
        #     self.publisher_.publish(twist)

        #程序结束前设置终端相关属性
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        
         
def main(args=None):
    rclpy.init(args=args) 
    minimal_publisher = MinimalPublisher() 
    rclpy.spin(minimal_publisher) 
    minimal_publisher.destroy_node()
    rclpy.shutdown()
 
 
if __name__ == '__main__':
    main()