#!/usr/bin/env python3
"""
Mobile Manipulator - Hardware Launch
=====================================

LEARNING OBJECTIVES:
- Understand ros2_control with real hardware
- See multi-hardware-interface coordination
- Learn controller lifecycle sequencing
- Practice debugging hardware connections

WHAT THIS LAUNCH DOES:
1. Starts robot_state_publisher with URDF (sim_mode=false)
2. Launches ros2_control controller_manager with hardware plugins
3. Spawns controllers in sequence:
   - joint_state_broadcaster (publishes /joint_states)
   - diff_drive_controller (mobile base)
   - arm_controller (manipulator)
   - gripper_controller (gripper)
4. Opens RViz for visualization

HARDWARE REQUIREMENTS:
- Arduino Mega on /dev/ttyACM0 (base) with encoder feedback
- Arduino Uno on /dev/ttyACM1 (arm) with servo control
- LiDAR on /dev/ttyUSB0 (optional)

USAGE:
  ros2 launch mobile_manipulator_bringup hardware.launch.py
  ros2 launch mobile_manipulator_bringup hardware.launch.py base_port:=/dev/ttyACM0 arm_port:=/dev/ttyACM1
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
    RegisterEventHandler,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    Command,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # ========================================
    # PACKAGE DIRECTORIES
    # ========================================
    pkg_description = get_package_share_directory('mobile_manipulator_description')
    pkg_bringup = get_package_share_directory('mobile_manipulator_bringup')

    # ========================================
    # FILE PATHS
    # ========================================
    urdf_file = os.path.join(pkg_description, 'urdf', 'mobile_manipulator.urdf.xacro')
    controllers_file = os.path.join(pkg_description, 'config', 'ros2_controllers.yaml')
    rviz_config = os.path.join(pkg_bringup, 'rviz', 'hardware.rviz')

    # ========================================
    # LAUNCH CONFIGURATIONS
    # ========================================
    use_rviz = LaunchConfiguration('use_rviz')
    base_port = LaunchConfiguration('base_port')
    arm_port = LaunchConfiguration('arm_port')

    # Process URDF with xacro (hardware mode)
    robot_description = Command([
        'xacro ', urdf_file,
        ' sim_mode:=false',
        ' base_serial_port:=', base_port,
        ' arm_serial_port:=', arm_port,
    ])

    return LaunchDescription([
        # ========================================
        # LAUNCH ARGUMENTS
        # ========================================
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Launch RViz for visualization'
        ),
        DeclareLaunchArgument(
            'base_port',
            default_value='/dev/ttyACM0',
            description='Serial port for mobile base Arduino'
        ),
        DeclareLaunchArgument(
            'arm_port',
            default_value='/dev/ttyACM1',
            description='Serial port for arm Arduino'
        ),

        # ========================================
        # ROBOT STATE PUBLISHER (t=0s)
        # ========================================
        # Publishes TF from URDF joint states
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

        # ========================================
        # ROS2_CONTROL CONTROLLER MANAGER (t=0s)
        # ========================================
        # Loads hardware interfaces from URDF ros2_control tags
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[
                {'robot_description': robot_description},
                controllers_file,
            ],
            output='screen',
        ),

        # ========================================
        # CONTROLLER SPAWNERS (t=2s)
        # ========================================
        # Give controller_manager time to initialize
        TimerAction(
            period=2.0,
            actions=[
                # Joint state broadcaster - MUST be first
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=[
                        'joint_state_broadcaster',
                        '--controller-manager', '/controller_manager'
                    ],
                    output='screen',
                ),
            ]
        ),

        # ========================================
        # MOTION CONTROLLERS (t=4s)
        # ========================================
        TimerAction(
            period=4.0,
            actions=[
                # Diff drive controller for mobile base
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=[
                        'diff_drive_controller',
                        '--controller-manager', '/controller_manager'
                    ],
                    output='screen',
                ),
                # Arm trajectory controller
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=[
                        'arm_controller',
                        '--controller-manager', '/controller_manager'
                    ],
                    output='screen',
                ),
                # Gripper position controller
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=[
                        'gripper_controller',
                        '--controller-manager', '/controller_manager'
                    ],
                    output='screen',
                ),
            ]
        ),

        # ========================================
        # RVIZ (t=6s)
        # ========================================
        TimerAction(
            period=6.0,
            actions=[
                Node(
                    package='rviz2',
                    executable='rviz2',
                    name='rviz2',
                    arguments=['-d', rviz_config],
                    output='screen',
                    condition=IfCondition(use_rviz),
                ),
            ]
        ),
    ])
