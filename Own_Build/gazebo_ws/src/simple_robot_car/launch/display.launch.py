#!/usr/bin/env python3
"""
Display Launch File for Simple Robot Car.

This launch file starts Gazebo simulation with the simple robot car,
along with robot_state_publisher and RViz for visualization.
"""

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Generate launch description for simple robot car display."""
    # Package directories
    pkg_simple = get_package_share_directory('simple_robot_car')
    pkg_gazebo = get_package_share_directory('gazebo_ros')

    # URDF file path
    urdf_file = os.path.join(pkg_simple, 'urdf', 'simple_robot_car.urdf')

    # Read URDF content properly using context manager
    with open(urdf_file, 'r') as f:
        robot_description_content = f.read()

    return LaunchDescription([
        # Start Gazebo
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_gazebo, 'launch', 'gazebo.launch.py')
            )
        ),

        # Publish robot_description
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description_content}]
        ),

        # RViz2 visualization
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen'
        ),

        # Spawn robot in Gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name='spawn_entity',
            output='screen',
            arguments=['-topic', 'robot_description', '-entity', 'simple_robot_car']
        )
    ])
