#!/usr/bin/env python3
"""
Separate Processes Launch - Basic Multi-Node Launch
====================================================

LEARNING OBJECTIVES:
--------------------
1. How to launch multiple nodes from one file
2. Understanding that each Node() creates a SEPARATE PROCESS
3. Basic launch file structure

This is the SIMPLEST multi-node launch file.
Each node runs in its own process.

USAGE:
------
    ros2 launch learning_execution separate_processes.launch.py

WHAT TO OBSERVE:
----------------
1. Both nodes start with their own PIDs
2. They communicate via network (DDS)
3. BUT: They don't connect! (Different topic names)

This demonstrates the PROBLEM that remapping solves!
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate a launch description with separate process nodes."""

    # Node A publishes to /data_out
    node_a = Node(
        package='learning_execution',
        executable='simple_node_a',
        name='node_a',
        output='screen',
    )

    # Node B subscribes to /data_in
    # PROBLEM: /data_in != /data_out, so no communication!
    node_b = Node(
        package='learning_execution',
        executable='simple_node_b',
        name='node_b',
        output='screen',
    )

    return LaunchDescription([
        node_a,
        node_b,
    ])
