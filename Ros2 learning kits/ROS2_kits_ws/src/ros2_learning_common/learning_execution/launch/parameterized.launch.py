#!/usr/bin/env python3
"""
Parameterized Launch - Passing Parameters to Nodes
===================================================

LEARNING OBJECTIVES:
--------------------
1. How to pass parameters from launch files
2. How to load parameters from YAML files
3. How to combine CLI arguments with parameters

PARAMETER PASSING METHODS:
--------------------------
1. Inline in Node():     parameters=[{'param': 'value'}]
2. From YAML file:       parameters=['/path/to/file.yaml']
3. From launch argument: parameters=[{'param': LaunchConfiguration('arg')}]

USAGE:
------
    # Use defaults
    ros2 launch learning_execution parameterized.launch.py

    # Override rate
    ros2 launch learning_execution parameterized.launch.py rate:=5.0

    # Use custom config
    ros2 launch learning_execution parameterized.launch.py \
        config_file:=/path/to/custom.yaml
"""

import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate a launch description with parameterized nodes."""

    # Get package share directory
    pkg_share = get_package_share_directory('learning_execution')
    default_config = os.path.join(pkg_share, 'config', 'node_a_params.yaml')

    # =========================================================================
    # DECLARE LAUNCH ARGUMENTS
    # =========================================================================

    declare_rate = DeclareLaunchArgument(
        'rate',
        default_value='1.0',
        description='Publishing rate in Hz'
    )

    declare_prefix = DeclareLaunchArgument(
        'prefix',
        default_value='Parameterized data',
        description='Message prefix'
    )

    declare_config = DeclareLaunchArgument(
        'config_file',
        default_value=default_config,
        description='Path to parameter YAML file'
    )

    # =========================================================================
    # GET CONFIGURATIONS
    # =========================================================================

    rate = LaunchConfiguration('rate')
    prefix = LaunchConfiguration('prefix')
    config_file = LaunchConfiguration('config_file')

    # =========================================================================
    # NODES WITH PARAMETERS
    # =========================================================================

    # Method 1: Inline parameters with launch arguments
    node_a_inline = Node(
        package='learning_execution',
        executable='simple_node_a',
        name='node_a_inline',
        output='screen',
        # Inline parameters - values can come from launch arguments
        parameters=[{
            'publish_rate': rate,
            'message_prefix': prefix,
        }],
    )

    # Method 2: Parameters from YAML file
    node_a_yaml = Node(
        package='learning_execution',
        executable='simple_node_a',
        name='node_a_yaml',
        output='screen',
        # Parameters from file
        parameters=[config_file],
        # You can also OVERRIDE file params with inline params:
        # parameters=[config_file, {'message_prefix': 'Override!'}],
    )

    # Subscriber to receive from both
    node_b = Node(
        package='learning_execution',
        executable='simple_node_b',
        name='node_b',
        output='screen',
        remappings=[('/data_in', '/data_out')],
    )

    return LaunchDescription([
        declare_rate,
        declare_prefix,
        declare_config,
        node_a_inline,
        node_a_yaml,
        node_b,
    ])
