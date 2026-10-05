#!/usr/bin/env python3
"""
Mobile Manipulator - Simulation Launch
=======================================

LEARNING OBJECTIVES:
- Understand Gazebo ros2_control integration
- See TimerAction for startup sequencing (critical!)
- Learn controller spawning with gazebo_ros2_control
- Practice simulation vs hardware mode switching

WHAT THIS LAUNCH DOES:
1. Starts robot_state_publisher with URDF (sim_mode=true)
2. Launches Gazebo simulator with world
3. Spawns robot entity in Gazebo
4. Waits for gazebo_ros2_control to create controller_manager
5. Spawns controllers in sequence
6. Opens RViz for visualization

TIMING (TimerAction) - CRITICAL:
  0s:  robot_state_publisher (provides /robot_description)
  2s:  Gazebo (needs robot_description to spawn)
  5s:  Spawn robot entity
  8s:  joint_state_broadcaster
  10s: Motion controllers (diff_drive, arm, gripper)
  12s: RViz

WHY TIMING MATTERS:
- Gazebo needs robot_description topic before spawning
- gazebo_ros2_control creates controller_manager when robot spawns
- Controllers can only spawn after controller_manager exists

USAGE:
  ros2 launch mobile_manipulator_bringup simulation.launch.py
  ros2 launch mobile_manipulator_bringup simulation.launch.py world:=arena.world
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
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
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # ========================================
    # FILE PATHS
    # ========================================
    urdf_file = os.path.join(pkg_description, 'urdf', 'mobile_manipulator.urdf.xacro')
    controllers_file = os.path.join(pkg_description, 'config', 'sim_controllers.yaml')
    rviz_config = os.path.join(pkg_bringup, 'rviz', 'simulation.rviz')

    # ========================================
    # LAUNCH CONFIGURATIONS
    # ========================================
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    world = LaunchConfiguration('world')

    # Process URDF with xacro (simulation mode)
    robot_description = Command(['xacro ', urdf_file, ' sim_mode:=true'])

    return LaunchDescription([
        # ========================================
        # ENVIRONMENT
        # ========================================
        # Add Gazebo model path for custom models
        SetEnvironmentVariable(
            name='GAZEBO_MODEL_PATH',
            value=os.path.join(pkg_description, 'meshes')
        ),

        # ========================================
        # LAUNCH ARGUMENTS
        # ========================================
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock from Gazebo'
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Launch RViz for visualization'
        ),
        DeclareLaunchArgument(
            'world',
            default_value='',
            description='Gazebo world file (empty for default empty world)'
        ),

        # ========================================
        # ROBOT STATE PUBLISHER (t=0s)
        # ========================================
        # Must start first - Gazebo spawn_entity needs robot_description topic
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time,
            }]
        ),

        # ========================================
        # GAZEBO SIMULATOR (t=2s)
        # ========================================
        TimerAction(
            period=2.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource([
                        os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
                    ]),
                    launch_arguments={
                        'world': world,
                        'verbose': 'false',
                    }.items(),
                ),
            ]
        ),

        # ========================================
        # SPAWN ROBOT IN GAZEBO (t=5s)
        # ========================================
        # spawn_entity.py reads from /robot_description topic
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='gazebo_ros',
                    executable='spawn_entity.py',
                    arguments=[
                        '-entity', 'mobile_manipulator',
                        '-topic', 'robot_description',
                        '-x', '0.0',
                        '-y', '0.0',
                        '-z', '0.1',
                    ],
                    output='screen',
                ),
            ]
        ),

        # ========================================
        # JOINT STATE BROADCASTER (t=8s)
        # ========================================
        # Must spawn after gazebo_ros2_control creates controller_manager
        TimerAction(
            period=8.0,
            actions=[
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
        # MOTION CONTROLLERS (t=10s)
        # ========================================
        TimerAction(
            period=10.0,
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
        # RVIZ (t=12s)
        # ========================================
        TimerAction(
            period=12.0,
            actions=[
                Node(
                    package='rviz2',
                    executable='rviz2',
                    name='rviz2',
                    arguments=['-d', rviz_config],
                    parameters=[{'use_sim_time': use_sim_time}],
                    output='screen',
                    condition=IfCondition(use_rviz),
                ),
            ]
        ),
    ])
