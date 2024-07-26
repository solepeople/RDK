#!/bin/bash
ros2 launch originbot_bringup originbot.launch.py &
sleep 6
echo "base starting success!"
export CAM_TYPE=usb
ros2 launch dnn_node_example dnn_node_example.launch.py dnn_example_config_file:=../config/yolov5.json dnn_example_image_width:=672 dnn_example_image_height:=672 &
sleep 10
ros2 launch websocket websocket.launch.py websocket_image_topic:=/image websocket_only_show_image:=true &
sleep 5
echo "yolo starting success!"
wait
exit 0
