#!/usr/bin/env python3
"""
Multi-Robot Namespaced Launch - Scaling Across Namespaces
==========================================================

Demonstrates launching multiple instances of the same node
under distinct namespaces to prevent topic and node collisions.

USAGE:
------
    ros2 launch learning_execution multi_robot.launch.py

WHAT TO OBSERVE:
----------------
1. Two simple_node_a instances run simultaneously:
   - /robot_1/simple_node_a
   - /robot_2/simple_node_a
2. Their telemetry topics are isolated under namespaces:
   - /robot_1/output_data
   - /robot_2/output_data
"""

from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    """Generate launch description for multi-robot namespace demo."""
    # Robot 1 Group
    robot_1_group = GroupAction([
        PushRosNamespace('robot_1'),
        Node(
            package='learning_execution',
            executable='simple_node_a',
            name='simple_node_a',
            output='screen',
            remappings=[
                ('/data_out', 'output_data'),
            ],
            parameters=[{'message_prefix': 'Robot 1 Telemetry'}],
        ),
    ])

    # Robot 2 Group
    robot_2_group = GroupAction([
        PushRosNamespace('robot_2'),
        Node(
            package='learning_execution',
            executable='simple_node_a',
            name='simple_node_a',
            output='screen',
            remappings=[
                ('/data_out', 'output_data'),
            ],
            parameters=[{'message_prefix': 'Robot 2 Telemetry'}],
        ),
    ])

    return LaunchDescription([
        robot_1_group,
        robot_2_group,
    ])
