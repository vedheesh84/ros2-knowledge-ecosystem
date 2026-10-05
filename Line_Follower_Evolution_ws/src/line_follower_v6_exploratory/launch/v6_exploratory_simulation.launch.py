from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='line_follower_v6_exploratory',
            executable='frontier_explorer_node',
            name='frontier_explorer_node',
            output='screen'
        )
    ])
