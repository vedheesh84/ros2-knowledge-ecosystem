#!/usr/bin/env python3
"""
Robot State Publisher Launch

LEARNING OBJECTIVES:
- Understand URDF->TF publishing
- See xacro processing at launch time
- Learn parameter passing in launch files
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_description = get_package_share_directory('mobile_manipulator_description')
    urdf_file = os.path.join(pkg_description, 'urdf', 'mobile_manipulator.urdf.xacro')

    sim_mode = LaunchConfiguration('sim_mode')
    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_file, ' sim_mode:=', sim_mode]),
        value_type=str
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'sim_mode',
            default_value='false',
            description='Enable simulation mode (uses Gazebo plugins)'
        ),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock'
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[
                {'robot_description': robot_description},
                {'use_sim_time': use_sim_time},
            ],
        ),
    ])
