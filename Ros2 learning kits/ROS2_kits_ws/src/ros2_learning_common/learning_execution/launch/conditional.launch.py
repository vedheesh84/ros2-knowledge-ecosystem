#!/usr/bin/env python3
"""
Conditional Launch - Enabling/Disabling Nodes at Launch
=========================================================

LEARNING OBJECTIVES:
--------------------
1. How to use launch arguments
2. How to conditionally launch nodes
3. How to build flexible, reusable launch files

LAUNCH ARGUMENTS:
-----------------
Launch arguments let users customize the launch without editing the file.

    ros2 launch package file.launch.py arg_name:=value

They're declared with DeclareLaunchArgument and accessed with LaunchConfiguration.

CONDITIONALS:
-------------
IfCondition and UnlessCondition let you enable/disable nodes based on arguments.

USAGE:
------
    # Launch all nodes (default)
    ros2 launch learning_execution conditional.launch.py

    # Disable node_b
    ros2 launch learning_execution conditional.launch.py enable_b:=false

    # Enable debug mode
    ros2 launch learning_execution conditional.launch.py debug:=true
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    """Generate a launch description with conditional nodes."""

    # =========================================================================
    # DECLARE LAUNCH ARGUMENTS
    # =========================================================================

    # Argument to enable/disable node_a
    declare_enable_a = DeclareLaunchArgument(
        'enable_a',
        default_value='true',
        description='Enable node_a'
    )

    # Argument to enable/disable node_b
    declare_enable_b = DeclareLaunchArgument(
        'enable_b',
        default_value='true',
        description='Enable node_b'
    )

    # Argument for debug mode
    declare_debug = DeclareLaunchArgument(
        'debug',
        default_value='false',
        description='Enable debug logging'
    )

    # =========================================================================
    # GET LAUNCH CONFIGURATIONS
    # =========================================================================

    enable_a = LaunchConfiguration('enable_a')
    enable_b = LaunchConfiguration('enable_b')
    debug = LaunchConfiguration('debug')

    # =========================================================================
    # LOG ACTIONS (helpful for debugging launch files)
    # =========================================================================

    log_config = LogInfo(
        msg=['Launching with: enable_a=', enable_a,
             ', enable_b=', enable_b,
             ', debug=', debug]
    )

    # =========================================================================
    # CONDITIONAL NODES
    # =========================================================================

    node_a = Node(
        package='learning_execution',
        executable='simple_node_a',
        name='node_a',
        output='screen',
        # IfCondition: Only launch if enable_a is 'true'
        condition=IfCondition(enable_a),
    )

    node_b = Node(
        package='learning_execution',
        executable='simple_node_b',
        name='node_b',
        output='screen',
        condition=IfCondition(enable_b),
        remappings=[('/data_in', '/data_out')],
    )

    # Debug node - only launches in debug mode
    debug_node = Node(
        package='learning_core',  # Using graph introspector from learning_core
        executable='graph_introspector_node',
        name='debug_introspector',
        output='screen',
        condition=IfCondition(debug),
    )

    return LaunchDescription([
        # First, declare all arguments
        declare_enable_a,
        declare_enable_b,
        declare_debug,

        # Log what we're doing
        log_config,

        # Then launch nodes (conditionally)
        node_a,
        node_b,
        debug_node,
    ])
