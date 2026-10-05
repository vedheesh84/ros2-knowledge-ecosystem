#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    
    pkg_line_follower = get_package_share_directory('line_follower_robot')
    model_path = os.path.join(pkg_line_follower, 'models', 'line_follower_robot.sdf')


    # Launch configuration variables
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')

    # Declare the launch arguments
    declare_x_position_cmd = DeclareLaunchArgument(
        'x_pose', default_value='0.0',
        description='X position of the robot')

    declare_y_position_cmd = DeclareLaunchArgument(
        'y_pose', default_value='0.0',
        description='Y position of the robot')


    # Spawn your robot model into Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'line_follower',
            '-file', model_path,
            '-x', x_pose,
            '-y', y_pose,
            '-z', '0.1'
        ],
        output='screen',
    )

    # Create and populate LaunchDescription
    ld = LaunchDescription()

    # Add actions
    ld.add_action(declare_x_position_cmd)
    ld.add_action(declare_y_position_cmd)
    ld.add_action(spawn_robot)

    return ld
