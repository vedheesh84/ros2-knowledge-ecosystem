#!/usr/bin/env python3
"""
sensors.launch.py - Launch all Reef Drone sensors

This launches the simulated sensor nodes that process
Gazebo ground truth into realistic sensor measurements.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('reef_drone_sensors')
    config_file = os.path.join(pkg_dir, 'config', 'sensors.yaml')

    return LaunchDescription([
        # DVL Simulator
        Node(
            package='reef_drone_sensors',
            executable='dvl_simulator',
            name='dvl_simulator',
            output='screen',
            parameters=[config_file]
        ),

        # Depth Sensor
        Node(
            package='reef_drone_sensors',
            executable='depth_sensor',
            name='depth_sensor',
            output='screen',
            parameters=[config_file]
        ),

        # Magnetometer
        Node(
            package='reef_drone_sensors',
            executable='magnetometer',
            name='magnetometer',
            output='screen',
            parameters=[config_file]
        ),
    ])
