#!/usr/bin/env python3
"""
display.launch.py - Visualize Reef Drone AUV in RViz

This launch file displays the robot model without any physics simulation.
Use this for:
- Verifying URDF correctness
- Checking TF tree structure
- Visualizing sensor positions
- Testing thruster orientations

Usage:
  ros2 launch reef_drone_description display.launch.py
  ros2 launch reef_drone_description display.launch.py use_gui:=false
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Get package directory
    pkg_dir = get_package_share_directory('reef_drone_description')

    # Launch arguments
    use_gui_arg = DeclareLaunchArgument(
        'use_gui',
        default_value='true',
        description='Use joint_state_publisher_gui for interactive control'
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz for visualization'
    )

    # Get URDF via xacro
    urdf_file = os.path.join(pkg_dir, 'urdf', 'reef_drone.urdf.xacro')
    robot_description = Command(['xacro ', urdf_file])

    # Robot state publisher - publishes TF based on URDF
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False
        }]
    )

    # Joint state publisher GUI - interactive joint control
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('use_gui'))
    )

    # Joint state publisher - non-interactive
    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        condition=UnlessCondition(LaunchConfiguration('use_gui'))
    )

    # RViz
    rviz_config = os.path.join(pkg_dir, 'rviz', 'display.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        condition=IfCondition(LaunchConfiguration('use_rviz'))
    )

    return LaunchDescription([
        use_gui_arg,
        use_rviz_arg,
        robot_state_publisher,
        joint_state_publisher_gui,
        joint_state_publisher,
        rviz,
    ])
