#!/usr/bin/env python3
"""
Display Launch - Visualize robot in RViz

LEARNING OBJECTIVES:
- Understand robot_state_publisher
- See joint_state_publisher_gui for testing
- Visualize TF tree in RViz
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_description = get_package_share_directory('mobile_manipulator_description')

    urdf_file = os.path.join(pkg_description, 'urdf', 'mobile_manipulator.urdf.xacro')
    rviz_config = os.path.join(pkg_description, 'rviz', 'display.rviz')

    sim_mode = LaunchConfiguration('sim_mode')
    use_rviz = LaunchConfiguration('use_rviz')
    use_gui = LaunchConfiguration('use_gui')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_file, ' sim_mode:=', sim_mode]),
        value_type=str
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'sim_mode',
            default_value='false',
            description='Enable simulation mode'
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Launch RViz for visualization'
        ),
        DeclareLaunchArgument(
            'use_gui',
            default_value='true',
            description='Launch Joint State Publisher GUI'
        ),

        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}],
        ),

        # Joint State Publisher GUI (for testing)
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            condition=IfCondition(use_gui),
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen',
            condition=IfCondition(use_rviz),
        ),
    ])

