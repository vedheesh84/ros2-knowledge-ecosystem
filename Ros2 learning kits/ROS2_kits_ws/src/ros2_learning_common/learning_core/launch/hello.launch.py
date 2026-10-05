#!/usr/bin/env python3
"""
Hello Node Launch File
======================

This launch file starts the hello_node - the simplest ROS2 node.

LEARNING OBJECTIVES:
--------------------
1. Understand the basic structure of a Python launch file
2. See how to start a single node with ros2 launch
3. Learn about launch file arguments (even for simple cases)

LAUNCH FILE ANATOMY:
--------------------
Every Python launch file needs:
1. A function called generate_launch_description()
2. That function must return a LaunchDescription object
3. The LaunchDescription contains "actions" (things to do)

USAGE:
------
    ros2 launch learning_core hello.launch.py

WHY USE LAUNCH FOR A SINGLE NODE?
----------------------------------
You could just use:  ros2 run learning_core hello_node

But launch files let you:
- Pass parameters consistently
- Document the intended usage
- Build more complex launches incrementally
"""

# =============================================================================
# IMPORTS
# =============================================================================
# These imports are standard for most launch files

from launch import LaunchDescription
from launch_ros.actions import Node


# =============================================================================
# LAUNCH DESCRIPTION GENERATOR
# =============================================================================

def generate_launch_description():
    """
    Generate the launch description for hello_node.

    This function is called by the ros2 launch system.
    It must return a LaunchDescription object.

    Returns:
        LaunchDescription: The launch configuration
    """

    # =========================================================================
    # CREATE NODE ACTION
    # =========================================================================
    # Node() creates a launch action that starts a ROS2 node
    #
    # Required parameters:
    #   package: The ROS2 package containing the node
    #   executable: The name from setup.py entry_points
    #
    # Optional parameters:
    #   name: Override the node name (default is from code)
    #   output: Where to send stdout ('screen', 'log', 'both')
    #   parameters: List of parameter files or dicts
    #   remappings: List of topic/service remappings

    hello_node = Node(
        package='learning_core',
        executable='hello_node',
        name='hello_node',           # Could rename here if needed
        output='screen',             # Show output in terminal
    )

    # =========================================================================
    # RETURN LAUNCH DESCRIPTION
    # =========================================================================
    # LaunchDescription takes a list of actions to execute

    return LaunchDescription([
        hello_node,
    ])
