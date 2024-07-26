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
wait
exit 0
