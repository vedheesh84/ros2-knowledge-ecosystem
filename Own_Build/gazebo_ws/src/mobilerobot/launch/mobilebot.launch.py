#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    urdf_file = os.path.join(
        get_package_share_directory('mobilerobot'),
        'urdf',
        'mobilebot.urdf.xacro'
    )
    xacro_result = xacro.process_file(urdf_file)
    urdf_xml = xacro_result.toxml() if hasattr(xacro_result, 'toxml') else str(xacro_result)
    robot_description = {'robot_description': urdf_xml}

    rviz_config_file = os.path.join(
        get_package_share_directory('mobilerobot'),
        'rviz',
        'mobilrob.rviz'  # Use the actual RViz config file
    )

    return LaunchDescription([
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            parameters=[{'use_sim_time': False}]
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[
                robot_description,
                {'use_sim_time': True}
            ]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'world', 'base_link'],
            output='screen',
            parameters=[{'use_sim_time': False}]
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file],
            parameters=[{'use_sim_time': False}]
        ),
    ])