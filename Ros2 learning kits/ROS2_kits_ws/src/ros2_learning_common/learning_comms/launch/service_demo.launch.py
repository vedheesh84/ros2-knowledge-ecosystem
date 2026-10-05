#!/usr/bin/env python3
"""
Service Demo Launch File
========================

Launches the service server and client to demonstrate
request-response communication.

USAGE:
------
    ros2 launch learning_comms service_demo.launch.py

WHAT TO OBSERVE:
----------------
1. Server starts and waits for requests
2. Client connects and sends requests
3. Server responds to each request
4. Client receives responses

NOTE:
-----
The client does a quick demo and exits. The server keeps running
so you can make manual calls with:
    ros2 service call /toggle_counter std_srvs/srv/SetBool "data: true"
"""

from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for service demo."""

    # Start server first
    server_node = Node(
        package='learning_comms',
        executable='service_server_node.py',
        name='service_server',
        output='screen',
    )

    # Start client after a delay to ensure server is ready
    client_node = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='learning_comms',
                executable='service_client_node.py',
                name='service_client',
                output='screen',
            )
        ]
    )

    return LaunchDescription([
        server_node,
        client_node,
    ])
