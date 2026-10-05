#!/usr/bin/env python3
"""
Graph Introspector Launch File
==============================

Launches the graph_introspector_node to explore the ROS2 graph.

LEARNING OBJECTIVES:
--------------------
1. See a slightly more complex launch file
2. Understand how multiple nodes can be launched together
3. Learn about launch file documentation

USAGE:
------
    # Launch just the introspector
    ros2 launch learning_core introspect.launch.py

    # In another terminal, start other nodes and watch them appear!
    ros2 run learning_core hello_node

TIP:
----
The introspector publishes to /graph_info. You can:
    ros2 topic echo /graph_info
to see the full graph report!
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for graph introspector."""

    graph_introspector = Node(
        package='learning_core',
        executable='graph_introspector_node',
        name='graph_introspector',
        output='screen',
    )

    return LaunchDescription([
        graph_introspector,
    ])
