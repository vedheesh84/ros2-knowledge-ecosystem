#!/usr/bin/env python3
"""
All Core Nodes Launch File
==========================

Launches ALL nodes in the learning_core package together.

LEARNING OBJECTIVES:
--------------------
1. See how multiple nodes are launched together
2. Understand launch file arguments (DeclareLaunchArgument)
3. Learn about conditional launching (IfCondition)
4. See how to load parameters from a YAML file

USAGE:
------
    # Launch all nodes with defaults
    ros2 launch learning_core all_core.launch.py

    # Disable specific nodes
    ros2 launch learning_core all_core.launch.py launch_hello:=false

    # Load custom parameters
    ros2 launch learning_core all_core.launch.py \
        params_file:=/path/to/custom_params.yaml

WHAT GETS LAUNCHED:
-------------------
- hello_node (optional, default: true)
- graph_introspector_node (optional, default: true)
- parameter_echo_node (always)
"""

import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for all core nodes."""

    # =========================================================================
    # FIND PACKAGE PATHS
    # =========================================================================
    # get_package_share_directory() finds where the package was installed
    # This is where config files, launch files, etc. live after colcon build

    pkg_share = get_package_share_directory('learning_core')

    # Path to default parameter file
    default_params_file = os.path.join(pkg_share, 'config', 'example_params.yaml')

    # =========================================================================
    # DECLARE LAUNCH ARGUMENTS
    # =========================================================================
    # Launch arguments are like function parameters - they let users
    # customize the launch without editing the file.
    #
    # DeclareLaunchArgument(name, default_value, description)
    # - name: The argument name (used in CLI as name:=value)
    # - default_value: Used if not specified
    # - description: Help text

    # Argument to toggle hello_node
    declare_launch_hello = DeclareLaunchArgument(
        'launch_hello',
        default_value='true',
        description='Whether to launch hello_node'
    )

    # Argument to toggle graph introspector
    declare_launch_introspect = DeclareLaunchArgument(
        'launch_introspect',
        default_value='true',
        description='Whether to launch graph_introspector_node'
    )

    # Argument for parameter file
    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Path to parameter YAML file for parameter_echo_node'
    )

    # =========================================================================
    # GET LAUNCH CONFIGURATION VALUES
    # =========================================================================
    # LaunchConfiguration() retrieves the value of a declared argument
    # These are SUBSTITUTIONS - they're evaluated at launch time, not now

    launch_hello = LaunchConfiguration('launch_hello')
    launch_introspect = LaunchConfiguration('launch_introspect')
    params_file = LaunchConfiguration('params_file')

    # =========================================================================
    # CREATE NODE ACTIONS
    # =========================================================================

    # Hello node (conditional)
    hello_node = Node(
        package='learning_core',
        executable='hello_node',
        name='hello_node',
        output='screen',
        # IfCondition evaluates the launch argument at runtime
        condition=IfCondition(launch_hello),
    )

    # Graph introspector (conditional)
    graph_introspector = Node(
        package='learning_core',
        executable='graph_introspector_node',
        name='graph_introspector',
        output='screen',
        condition=IfCondition(launch_introspect),
    )

    # Parameter echo node (always launched)
    parameter_echo = Node(
        package='learning_core',
        executable='parameter_echo_node',
        name='parameter_echo',
        output='screen',
        # Load parameters from file
        # The params_file substitution will be resolved at launch time
        parameters=[params_file],
    )

    # =========================================================================
    # RETURN LAUNCH DESCRIPTION
    # =========================================================================
    # Order matters! Declare arguments before using them in nodes

    return LaunchDescription([
        # First, declare all arguments
        declare_launch_hello,
        declare_launch_introspect,
        declare_params_file,

        # Then, add all node actions
        hello_node,
        graph_introspector,
        parameter_echo,
    ])
