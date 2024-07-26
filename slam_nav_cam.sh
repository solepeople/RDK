#!/bin/bash

ros2 launch originbot_bringup originbot.launch.py &
sleep 6
echo "base starting success!"
ros2 launch originbot_navigation cartographer.launch.py &
sleep 20
echo "slam starting success!"
ros2 launch nav2_bringup navigation_launch.py &
sleep 15
echo "nav starting success!"
ros2 launch hobot_usb_cam hobot_usb_cam.launch.py usb_video_device:=/dev/video8 &
sleep 5
ros2 launch websocket websocket.launch.py websocket_image_topic:=/image websocket_only_show_image:=true &
sleep 5
echo "cam starting success!"
wait
exit 0
