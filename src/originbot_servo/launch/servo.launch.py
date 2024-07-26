import launch
import launch_ros.actions

def generate_launch_description():
    return launch.LaunchDescription([
        launch_ros.actions.Node(
            package='originbot_servo',
            executable='servo_node',
            name='servo_node'),
  ])