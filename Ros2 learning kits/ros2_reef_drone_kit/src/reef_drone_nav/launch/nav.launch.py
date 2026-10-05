#!/usr/bin/env python3
"""
nav.launch.py - Launch AUV navigation stack
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('reef_drone_nav')
    config_file = os.path.join(pkg_dir, 'config', 'nav.yaml')

    return LaunchDescription([
        Node(
            package='reef_drone_nav',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[config_file]
        ),
        Node(
            package='reef_drone_nav',
            executable='mission_executor',
            name='mission_executor',
            output='screen',
            parameters=[config_file]
        ),
    ])
