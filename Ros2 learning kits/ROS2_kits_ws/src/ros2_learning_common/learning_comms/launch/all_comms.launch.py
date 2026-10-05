#!/usr/bin/env python3
"""
All Communication Nodes Launch File
====================================

Launches ALL communication demo nodes together.
Use this to see all three patterns (topics, services, actions) running simultaneously.

USAGE:
------
    ros2 launch learning_comms all_comms.launch.py

WHAT TO OBSERVE:
----------------
Watch the output to see:
1. Topic messages flowing (talker → listener)
2. Service requests being handled
3. Action goals executing with feedback

The terminal will be busy! Consider:
- Launching in separate terminals instead
- Using rqt_graph to visualize
"""

from launch import LaunchDescription
from launch.actions import TimerAction, GroupAction
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for all comms nodes."""

    # Group 1: Topic nodes (start immediately)
    topic_nodes = GroupAction([
        Node(
            package='learning_comms',
            executable='talker_node.py',
            name='talker',
            output='screen',
        ),
        Node(
            package='learning_comms',
            executable='listener_node.py',
            name='listener',
            output='screen',
        ),
    ])

    # Group 2: Service nodes (server first)
    service_server = Node(
        package='learning_comms',
        executable='service_server_node.py',
        name='service_server',
        output='screen',
    )

    service_client = TimerAction(
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

    # Group 3: Action nodes (server first, delayed start)
    action_server = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='learning_comms',
                executable='action_server_node.py',
                name='action_server',
                output='screen',
            )
        ]
    )

    action_client = TimerAction(
        period=5.0,
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
        topic_nodes,
        service_server,
        service_client,
        action_server,
        action_client,
    ])
