from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='line_follower_v2_v3_stabilized',
            executable='sensor_array_processor',
            name='sensor_array_processor',
            output='screen'
        ),
        Node(
            package='line_follower_v2_v3_stabilized',
            executable='stabilized_motion_controller',
            name='stabilized_motion_controller',
            output='screen'
        )
    ])
