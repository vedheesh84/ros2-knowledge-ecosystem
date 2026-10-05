#!/usr/bin/env python3
"""
Publish-Subscribe Demo Launch File
===================================

Launches the talker and listener nodes together to demonstrate
topic-based communication.

USAGE:
------
    ros2 launch learning_comms pubsub_demo.launch.py

WHAT TO OBSERVE:
----------------
1. Talker publishes to /chatter
2. Listener receives from /chatter
3. Messages flow automatically
4. Try killing one node - the other continues!
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for pub-sub demo."""

    talker_node = Node(
        package='learning_comms',
        executable='talker_node.py',
        name='talker',
        output='screen',
    )

    listener_node = Node(
        package='learning_comms',
        executable='listener_node.py',
        name='listener',
        output='screen',
    )

    return LaunchDescription([
        talker_node,
        listener_node,
    ])
