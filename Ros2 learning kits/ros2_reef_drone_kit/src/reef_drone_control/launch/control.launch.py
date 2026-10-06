#!/usr/bin/env python3
"""
control.launch.py - Launch Reef Drone control nodes

This launches the control stack:
- Thruster allocator (always needed)
- One of: depth_controller, heading_controller, velocity_controller, station_keeping
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import LaunchConfigurationEquals
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('reef_drone_control')
    config_file = os.path.join(pkg_dir, 'config', 'control.yaml')

    # Launch arguments
    mode_arg = DeclareLaunchArgument(
        'mode',
        default_value='station_keeping',
        description='Control mode: depth, heading, velocity, station_keeping'
    )

    return LaunchDescription([
        mode_arg,

        # Thruster allocator (always runs)
        Node(
            package='reef_drone_control',
            executable='thruster_allocator',
            name='thruster_allocator',
            output='screen',
            parameters=[config_file]
        ),

        # Station keeping mode
        Node(
            package='reef_drone_control',
            executable='station_keeping',
            name='station_keeping',
            output='screen',
            parameters=[config_file],
            condition=LaunchConfigurationEquals('mode', 'station_keeping')
        ),

        # Depth control mode
        Node(
            package='reef_drone_control',
            executable='depth_controller',
            name='depth_controller',
            output='screen',
            parameters=[config_file],
            condition=LaunchConfigurationEquals('mode', 'depth')
        ),

        # Heading control mode
        Node(
            package='reef_drone_control',
            executable='heading_controller',
            name='heading_controller',
            output='screen',
            parameters=[config_file],
            condition=LaunchConfigurationEquals('mode', 'heading')
        ),

        # Velocity control mode
        Node(
            package='reef_drone_control',
            executable='velocity_controller',
            name='velocity_controller',
            output='screen',
            parameters=[config_file],
            condition=LaunchConfigurationEquals('mode', 'velocity')
        ),
    ])

