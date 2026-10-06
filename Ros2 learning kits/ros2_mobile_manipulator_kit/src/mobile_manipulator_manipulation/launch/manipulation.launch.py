#!/usr/bin/env python3
"""
Manipulation Launch File
========================

LEARNING OBJECTIVES:
- Launch pick-place state machine
- Configure manipulation parameters
- Set up perception integration

USAGE:
  ros2 launch mobile_manipulator_manipulation manipulation.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # ========================================
        # LAUNCH ARGUMENTS
        # ========================================
        DeclareLaunchArgument(
            'place_x',
            default_value='0.25',
            description='Place position X'
        ),
        DeclareLaunchArgument(
            'place_y',
            default_value='0.15',
            description='Place position Y'
        ),
        DeclareLaunchArgument(
            'place_z',
            default_value='0.05',
            description='Place position Z'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock'
        ),

        # ========================================
        # MANIPULATION NODE
        # ========================================
        Node(
            package='mobile_manipulator_manipulation',
            executable='manipulation_node.py',
            name='manipulation_node',
            output='screen',
            parameters=[{
                'place_x': LaunchConfiguration('place_x'),
                'place_y': LaunchConfiguration('place_y'),
                'place_z': LaunchConfiguration('place_z'),
                'use_sim_time': LaunchConfiguration('use_sim_time'),
            }]
        ),
    ])
