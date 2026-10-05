#!/usr/bin/env python3
"""
Composed Node Launch - Single Process Multi-Node
=================================================

LEARNING OBJECTIVES:
--------------------
1. Understanding composition vs separate processes
2. When to use composition for performance
3. The tradeoffs of composition

COMPOSITION BENEFITS:
---------------------
- Lower latency (no network serialization)
- Zero-copy message passing (for compatible types)
- Fewer system resources
- Simpler deployment (one process)

COMPOSITION TRADEOFFS:
----------------------
- One crash kills all nodes
- Harder to debug (shared state)
- All nodes must be in Python (for this approach)

USAGE:
------
    ros2 launch learning_execution composed.launch.py

WHAT TO OBSERVE:
----------------
1. Only ONE process appears (check with: ps aux | grep composed)
2. Three "nodes" but one process
3. Watch for fast communication
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate a launch description for the composed node."""

    # This launches our composed_node executable
    # which internally creates multiple nodes in one process
    composed = Node(
        package='learning_execution',
        executable='composed_node',
        name='composed_demo',
        output='screen',
    )

    return LaunchDescription([
        composed,
    ])
