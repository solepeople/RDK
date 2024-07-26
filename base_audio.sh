#!/bin/bash

ros2 launch originbot_bringup originbot.launch.py &
sleep 6
echo "base starting success!"
ros2 launch originbot_audio sudio_contorl.launch.py &
echo "audio starting success!"
wait
exit 0
