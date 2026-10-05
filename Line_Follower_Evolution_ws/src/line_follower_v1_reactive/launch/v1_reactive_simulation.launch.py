from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='line_follower_v1_reactive',
            executable='simulated_track_sensor',
            name='simulated_track_sensor',
            output='screen'
        ),
        Node(
            package='line_follower_v1_reactive',
            executable='reactive_threshold_node',
            name='reactive_threshold_node',
            output='screen'
        )
    ])
