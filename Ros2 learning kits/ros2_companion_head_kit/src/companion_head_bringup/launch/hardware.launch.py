#!/usr/bin/env python3
"""
hardware.launch.py - Hardware Bringup Launch for Companion Head
==============================================================

Launches the physical (or pseudo-hardware emulated) Companion Head system:
1. Robot State Publisher with URDF (use_sim:=false, use_fake_hardware:=false, serial_port configured)
2. Controller Manager (ros2_control_node)
3. Spawns joint_state_broadcaster and joint_trajectory_controller
4. Optional RViz visualization
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_description = get_package_share_directory('companion_head_description')
    pkg_bringup = get_package_share_directory('companion_head_bringup')

    urdf_file = os.path.join(pkg_description, 'urdf', 'companion_head.urdf.xacro')
    controllers_file = os.path.join(pkg_description, 'config', 'ros2_controllers.yaml')
    rviz_config = os.path.join(pkg_bringup, 'rviz', 'simulation.rviz')

    serial_port = LaunchConfiguration('serial_port')
    use_fake_hardware = LaunchConfiguration('use_fake_hardware')
    use_rviz = LaunchConfiguration('use_rviz')

    robot_description = ParameterValue(
        Command([
            'xacro ', urdf_file,
            ' use_sim:=false',
            ' use_fake_hardware:=', use_fake_hardware,
            ' serial_port:=', serial_port
        ]),
        value_type=str
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'serial_port',
            default_value='/dev/ttyUSB0',
            description='Serial port for Arduino / microcontroller hardware interface'
        ),
        DeclareLaunchArgument(
            'use_fake_hardware',
            default_value='false',
            description='Use mock hardware interfaces'
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='false',
            description='Launch RViz for visualization'
        ),

        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': False,
            }]
        ),

        # ros2_control Controller Manager
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[
                {'robot_description': robot_description},
                controllers_file,
            ],
            output='screen',
        ),

        # Joint State Broadcaster Spawner
        TimerAction(
            period=2.0,
            actions=[
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
                    output='screen',
                ),
            ],
        ),

        # Joint Trajectory Controller Spawner
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['joint_trajectory_controller', '--controller-manager', '/controller_manager'],
                    output='screen',
                ),
            ],
        ),

        # Optional RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            condition=IfCondition(use_rviz),
            output='screen'
        ),
    ])
