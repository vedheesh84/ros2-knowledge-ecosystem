#!/usr/bin/env python3
"""
Action Demo Launch File
=======================

Launches the action server and client to demonstrate
long-running task communication with feedback.

USAGE:
------
    ros2 launch learning_comms action_demo.launch.py

WHAT TO OBSERVE:
----------------
1. Server starts and waits for goals
2. Client sends a goal (count to 10)
3. Server sends feedback at each count
4. Client receives feedback and logs progress
5. Server sends final result
6. Client receives result and logs it

TRY THIS:
---------
After the demo, send your own goals:
    ros2 action send_goal /count_to_number learning_comms/action/CountToNumber \
        "{target_number: 5, delay_between_counts: 1.0}" --feedback
"""

from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for action demo."""

    # Start server first
    server_node = Node(
        package='learning_comms',
        executable='action_server_node.py',
        name='action_server',
        output='screen',
    )

    # Start client after a delay to ensure server is ready
    client_node = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='learning_comms',
                executable='action_client_node.py',
                name='action_client',
                output='screen',
            )
        ]
    )

    return LaunchDescription([
        server_node,
        client_node,
    ])
