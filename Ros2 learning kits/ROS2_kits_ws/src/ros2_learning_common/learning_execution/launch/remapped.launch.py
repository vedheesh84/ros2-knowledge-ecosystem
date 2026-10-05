#!/usr/bin/env python3
"""
Remapped Topics Launch - Connecting Nodes via Remapping
========================================================

LEARNING OBJECTIVES:
--------------------
1. How to use remappings to connect topics
2. Why remapping enables code reuse
3. The power of configuration over code changes

WHAT IS REMAPPING?
------------------
Remapping changes topic/service names AT RUNTIME without changing code.

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                         WITHOUT REMAPPING                               │
    │                                                                         │
    │   Node A ─────▶ /data_out                /data_in ◀───── Node B        │
    │                                                                         │
    │   Topics don't match! No communication.                                │
    └─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                          WITH REMAPPING                                 │
    │                                                                         │
    │   Node A ─────▶ /data_out ═══════════════════════ ◀───── Node B        │
    │                               (remapped)                                │
    │                                                                         │
    │   /data_in remapped to /data_out → They connect!                       │
    └─────────────────────────────────────────────────────────────────────────┘

USAGE:
------
    ros2 launch learning_execution remapped.launch.py

WHAT TO OBSERVE:
----------------
1. Node B receives messages from Node A
2. The remapping happens in the launch file, not the code
3. Same nodes, different configuration = different behavior
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate a launch description with remapped topics."""

    # Node A publishes to /data_out (unchanged)
    node_a = Node(
        package='learning_execution',
        executable='simple_node_a',
        name='node_a',
        output='screen',
    )

    # Node B subscribes to /data_in, but we REMAP it to /data_out
    node_b = Node(
        package='learning_execution',
        executable='simple_node_b',
        name='node_b',
        output='screen',
        # REMAPPINGS: List of (from, to) tuples
        # This says: whenever the code uses /data_in, actually use /data_out
        remappings=[
            ('/data_in', '/data_out'),
        ],
    )

    return LaunchDescription([
        node_a,
        node_b,
    ])
