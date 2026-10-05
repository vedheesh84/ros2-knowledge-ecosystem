#!/usr/bin/env python3

"""
RViz + Robot State Publisher launch file (ROS 2 Humble compatible)
This version correctly passes robot_description as a STRING
"""

import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # CHANGE THIS if your package name is different
    pkg_name = 'robot_pkg'

    # Path to xacro / urdf
    urdf_file = os.path.join(
        get_package_share_directory(pkg_name),
        'urdf',
        'example5.urdf.xacro'
    )

    # Properly typed robot_description (FIX for your error)
    robot_description = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description
        }]
    )

    # Joint State Publisher (for RViz sliders, if no hardware)
    joint_state_publisher = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen'
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        joint_state_publisher,
        robot_state_publisher,
        rviz
    ])

