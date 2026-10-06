#!/usr/bin/env python3
"""
hardware_bridge.launch.py - Launch serial hardware bridge for Reef Drone AUV
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('reef_drone_hardware')
    default_config = os.path.join(pkg_dir, 'config', 'hardware.yaml')

    port_arg = DeclareLaunchArgument(
        'port',
        default_value='/tmp/ttyAUV_SIM',
        description='Serial port device path or PTY link'
    )

    baud_arg = DeclareLaunchArgument(
        'baudrate',
        default_value='115200',
        description='Serial baud rate'
    )

    return LaunchDescription([
        port_arg,
        baud_arg,
        Node(
            package='reef_drone_hardware',
            executable='flight_bridge_node',
            name='flight_bridge_node',
            output='screen',
            parameters=[
                default_config,
                {
                    'port': LaunchConfiguration('port'),
                    'baudrate': LaunchConfiguration('baudrate')
                }
            ]
        )
    ])
