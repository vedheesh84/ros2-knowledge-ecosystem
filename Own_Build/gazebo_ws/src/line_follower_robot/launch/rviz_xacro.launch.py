#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.descriptions import ParameterValue
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument


def generate_launch_description():
    # Package and Xacro paths
    pkg_name = 'line_follower_robot'
    pkg_share_dir = get_package_share_directory(pkg_name)
    xacro_file = os.path.join(pkg_share_dir, 'urdf', 'line_follower_robot.urdf.xacro')

    # Convert Xacro to URDF string
    robot_description_content = ParameterValue(
        Command(['xacro ', xacro_file]), 
        value_type=str
    )
    robot_description = {'robot_description': robot_description_content}

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
        output='screen',
        parameters=[robot_description]
    )
    

    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    # Launch description
    ld = LaunchDescription()
    ld.add_action(gui_arg)
    ld.add_action(joint_state_publisher_node)
    ld.add_action(robot_state_publisher_node)
    ld.add_action(rviz_node)

    return ld


		

	


		
	