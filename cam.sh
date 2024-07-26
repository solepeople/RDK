#!/bin/bash
ros2 launch hobot_usb_cam hobot_usb_cam.launch.py usb_video_device:=/dev/video8 &
sleep 5
ros2 launch websocket websocket.launch.py websocket_image_topic:=/image websocket_only_show_image:=true &
sleep 5
echo "cam starting success!"
wait
exit 0
