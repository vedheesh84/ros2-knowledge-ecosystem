#!/usr/bin/env python3
"""
RViz Simple Car Launch File.

This launch file starts the robot state publisher and RViz for visualizing
a simple car robot model defined in URDF/XACRO format.
"""

import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    """Generate launch description for RViz simple car visualization."""
    # Launch configuration
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Package paths
    package_name = 'rviz_tutorial'
    pkg_share_dir = get_package_share_directory(package_name)

    # URDF file path
    urdf_file_name = 'robot.urdf.xacro'
    urdf_path = os.path.join(pkg_share_dir, 'urdf', urdf_file_name)

    # Robot description parameter
    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_path]), value_type=str
    )
    robot_description_param = {'robot_description': robot_description_content}

    # RViz config file path
    rviz_config_file = os.path.join(pkg_share_dir, 'config', 'tb3_cartographer.rviz')

    # Robot State Publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description_param, {'use_sim_time': use_sim_time}]
    )

    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )

    # Build launch description
    ld = LaunchDescription()

    # Declare launch arguments
    ld.add_action(DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    ))

    # Add nodes
    ld.add_action(robot_state_publisher_node)
    ld.add_action(rviz_node)

    return ld
