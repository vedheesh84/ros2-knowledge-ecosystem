from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='line_follower_v4_v5_topological',
            executable='tag_detector_node',
            name='tag_detector_node',
            output='screen'
        ),
        Node(
            package='line_follower_v4_v5_topological',
            executable='topological_navigator_node',
            name='topological_navigator_node',
            output='screen'
        )
    ])
