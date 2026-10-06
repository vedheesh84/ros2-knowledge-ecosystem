#!/usr/bin/env python3
"""
full_system.launch.py - Launch complete AUV system

This launches:
- simulation.launch.py (Gazebo + robot)
- Sensor simulators
- State estimation (EKF)
- Control stack
- Navigation

Usage:
  ros2 launch reef_drone_bringup full_system.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # Package directories
    bringup_dir = get_package_share_directory('reef_drone_bringup')
    sensors_dir = get_package_share_directory('reef_drone_sensors')
    estimation_dir = get_package_share_directory('reef_drone_estimation')
    control_dir = get_package_share_directory('reef_drone_control')
    nav_dir = get_package_share_directory('reef_drone_nav')

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz visualization'
    )

    use_gui_arg = DeclareLaunchArgument(
        'use_gui',
        default_value='true',
        description='Launch Gazebo GUI'
    )

    return LaunchDescription([
        use_rviz_arg,
        use_gui_arg,

        # Simulation (Gazebo + robot)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(bringup_dir, 'launch', 'simulation.launch.py')
            ]),
            launch_arguments={
                'use_rviz': LaunchConfiguration('use_rviz'),
                'use_gui': LaunchConfiguration('use_gui'),
            }.items(),
        ),

        # Sensors
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(sensors_dir, 'launch', 'sensors.launch.py')
            ]),
        ),

        # Estimation
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(estimation_dir, 'launch', 'estimation.launch.py')
            ]),
        ),

        # Control
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(control_dir, 'launch', 'control.launch.py')
            ]),
        ),

        # Navigation
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(nav_dir, 'launch', 'nav.launch.py')
            ]),
        ),
    ])
