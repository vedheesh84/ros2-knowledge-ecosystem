#!/usr/bin/env python3
"""
simulation.launch.py - Full Gazebo simulation for Companion Head

LEARNING OBJECTIVES:
====================
1. Understand launch file orchestration
2. Learn Gazebo + ros2_control integration
3. See multi-node system startup

WHAT THIS LAUNCHES:
===================
1. Gazebo with companion_room world
2. Robot state publisher (URDF)
3. Spawn robot in Gazebo
4. Controller manager + joint controllers
5. RViz visualization

USAGE:
======
    ros2 launch companion_head_bringup simulation.launch.py
    ros2 launch companion_head_bringup simulation.launch.py use_rviz:=false
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    # Package directories
    pkg_description = get_package_share_directory('companion_head_description')
    pkg_gazebo = get_package_share_directory('companion_head_gazebo')
    pkg_bringup = get_package_share_directory('companion_head_bringup')

    # Launch arguments
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz'
    )

    use_gui_arg = DeclareLaunchArgument(
        'use_gui',
        default_value='true',
        description='Launch Gazebo GUI'
    )

    # Robot description
    urdf_file = os.path.join(pkg_description, 'urdf', 'companion_head.urdf.xacro')
    robot_description = Command([
        'xacro ', urdf_file,
        ' use_sim:=true',
        ' use_fake_hardware:=false'
    ])

    # World file
    world_file = os.path.join(pkg_gazebo, 'worlds', 'companion_room.world')

    # Robot state publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'publish_frequency': 50.0,
        }]
    )

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={
            'world': world_file,
            'gui': LaunchConfiguration('use_gui'),
        }.items()
    )

    # Spawn robot
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'companion_head',
            '-x', '0',
            '-y', '0',
            '-z', '0.76',  # On top of table
        ],
        output='screen'
    )

    # Load controllers (after spawn)
    load_joint_state_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_broadcaster'],
        output='screen'
    )

    load_joint_trajectory_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_trajectory_controller'],
        output='screen'
    )

    # Delay controller loading until spawn completes
    delay_controllers = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_robot,
            on_exit=[
                TimerAction(
                    period=2.0,
                    actions=[load_joint_state_broadcaster]
                ),
                TimerAction(
                    period=3.0,
                    actions=[load_joint_trajectory_controller]
                ),
            ]
        )
    )

    # RViz
    rviz_config = os.path.join(pkg_bringup, 'rviz', 'simulation.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        condition=IfCondition(LaunchConfiguration('use_rviz'))
    )

    return LaunchDescription([
        use_rviz_arg,
        use_gui_arg,
        robot_state_publisher,
        gazebo,
        TimerAction(period=3.0, actions=[spawn_robot]),
        delay_controllers,
        TimerAction(period=5.0, actions=[rviz]),
    ])
