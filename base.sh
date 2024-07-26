#!/bin/bash

ros2 run originbot_base originbot_base &
sleep 6
echo "base starting success!"
wait
exit 0
