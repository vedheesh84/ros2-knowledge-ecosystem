#!/usr/bin/env python3
"""
estimation.launch.py - Launch AUV state estimation

Launches the EKF node that fuses IMU, DVL, depth, and magnetometer.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('reef_drone_estimation')
    config_file = os.path.join(pkg_dir, 'config', 'ekf.yaml')

    return LaunchDescription([
        Node(
            package='reef_drone_estimation',
            executable='auv_ekf',
            name='auv_ekf',
            output='screen',
            parameters=[config_file]
        ),
    ])
