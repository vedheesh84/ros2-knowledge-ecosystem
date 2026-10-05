#!/usr/bin/env python3
"""
Launch file for visualizing the line_follower_robot URDF in RViz.

This launch starts:
- joint_state_publisher_gui for interactive joint control
- robot_state_publisher for TF broadcasting
- RViz2 for visualization
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Generate launch description for URDF visualization in RViz."""
    # Package share directory
    pkg_name = 'line_follower_robot'
    pkg_share_dir = get_package_share_directory(pkg_name)

    # Path to URDF file
    urdf_file_path = os.path.join(pkg_share_dir, 'urdf', 'line_follower_robot.urdf')

    # Read URDF file content
    with open(urdf_file_path, 'r') as urdf_file:
        robot_description_content = urdf_file.read()

    # Launch argument for enabling GUI
    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Flag to enable joint_state_publisher GUI'
    )

    # Joint State Publisher GUI node
    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        parameters=[{'use_gui': LaunchConfiguration('gui')}]
    )

    # Robot State Publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )

    # RViz node
    rviz_config_file = os.path.join(pkg_share_dir, 'config', 'rviz_line_follower.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else []
    )

    # Return LaunchDescription with all nodes
    return LaunchDescription([
        gui_arg,
        joint_state_publisher_node,
        robot_state_publisher_node,
        rviz_node
    ])
