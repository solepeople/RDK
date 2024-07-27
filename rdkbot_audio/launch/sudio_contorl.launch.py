# Copyright (c) 2022，Horizon Robotics.
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

import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python import get_package_share_directory


def generate_launch_description():
    return LaunchDescription([
        # 启动智能语音识别pkg
        DeclareLaunchArgument(
            'audio_config_path',
            default_value='/root/rdkbot/src/originbot_audio/config',
            description='hobot audio config path'),
        DeclareLaunchArgument(
            'audio_pub_topic_name',
            default_value='/audio_smart',
            description='hobot audio publish topic name'),
        # 启动音频采集pkg
        Node(
            package='hobot_audio',
            executable='hobot_audio',
            output='screen',
            parameters=[
                {"config_path": LaunchConfiguration('audio_config_path')},
                {"audio_pub_topic_name": LaunchConfiguration(
                    'audio_pub_topic_name')}
            ],
            arguments=['--ros-args', '--log-level', 'warn']
        ),
        # 启动语音控制pkg
        Node(
            package='audio_control',
            executable='audio_control',
            output='screen',
            parameters=[
                {"ai_msg_sub_topic_name": "/audio_smart"},
                {"twist_pub_topic_name": "/cmd_vel"},
                {"motion_duration_seconds": 0}
            ],
            arguments=['--ros-args', '--log-level', 'error']
        )
    ])
    