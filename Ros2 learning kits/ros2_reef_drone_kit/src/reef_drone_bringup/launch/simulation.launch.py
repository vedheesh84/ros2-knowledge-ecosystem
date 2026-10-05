#!/usr/bin/env python3
"""
simulation.launch.py - Launch full Reef Drone simulation

This launches:
- Gazebo with underwater world
- Robot URDF with physics plugins
- Sensor simulators
- State estimation (EKF)
- Control stack
- RViz visualization

Usage:
  ros2 launch reef_drone_bringup simulation.launch.py
  ros2 launch reef_drone_bringup simulation.launch.py use_rviz:=false
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # Package directories
    bringup_dir = get_package_share_directory('reef_drone_bringup')
    description_dir = get_package_share_directory('reef_drone_description')
    gazebo_dir = get_package_share_directory('reef_drone_gazebo')

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

    # Get URDF via xacro (includes Gazebo plugins)
    urdf_file = os.path.join(description_dir, 'urdf', 'reef_drone.urdf.xacro')
    gazebo_xacro = os.path.join(description_dir, 'urdf', 'gazebo.xacro')

    robot_description = Command([
        'xacro ', urdf_file,
        ' gazebo_xacro:=', gazebo_xacro
    ])

    # World file
    world_file = os.path.join(gazebo_dir, 'worlds', 'ocean.world')

    # RViz config
    rviz_config = os.path.join(bringup_dir, 'rviz', 'simulation.rviz')

    return LaunchDescription([
        use_rviz_arg,
        use_gui_arg,

        # Gazebo
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
            ]),
            launch_arguments={
                'world': world_file,
                'gui': LaunchConfiguration('use_gui'),
            }.items(),
        ),

        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True
            }]
        ),

        # Spawn robot in Gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            name='spawn_robot',
            arguments=[
                '-entity', 'reef_drone',
                '-topic', 'robot_description',
                '-x', '0', '-y', '0', '-z', '-5',  # Start at 5m depth
            ],
            output='screen'
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('use_rviz')),
            parameters=[{'use_sim_time': True}]
        ),
    ])
