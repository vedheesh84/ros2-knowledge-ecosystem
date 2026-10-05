#!/usr/bin/env python3
# Copyright 2019 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# 
# Author: Darby Lim

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, ThisLaunchFileDir, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    use_rviz = LaunchConfiguration('use_rviz', default='true')
    resolution = LaunchConfiguration('resolution', default='0.05')
    publish_period_sec = LaunchConfiguration('publish_period_sec', default='1.0')

    # Directories
    pkg_mobilerobot = get_package_share_directory('mobilerobot')
    cartographer_config_dir = LaunchConfiguration('cartographer_config_dir', default=os.path.join(pkg_mobilerobot, 'config'))
    configuration_basename = LaunchConfiguration('configuration_basename', default='mobilerobot_lds_2d.lua')
    rviz_config_dir = os.path.join(pkg_mobilerobot, 'rviz', 'mobilebot_cartographer.rviz')
    robot_description_file = os.path.join(pkg_mobilerobot, 'urdf', 'mobilebot.urdf.xacro')

    # Nodes
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': ParameterValue(Command(['xacro ', robot_description_file]), value_type=str)
        }]
    )

    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'mobilebot'],
        output='screen'
    )

    # Cartographer node with remappings
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            '-configuration_directory', cartographer_config_dir,
            '-configuration_basename', configuration_basename
        ],
        remappings=[
            ('/scan', '/gazebo_ros_ray_sensor/out'),
            ('/imu', '/imu/data')
        ]
    )

    # Occupancy grid node
    occupancy_grid_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([ThisLaunchFileDir(), '/occupancy_grid.launch.py']),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'resolution': resolution,
            'publish_period_sec': publish_period_sec
        }.items()
    )

    # RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(use_rviz),
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation time'),
        DeclareLaunchArgument('use_rviz', default_value='true', description='Launch RViz'),
        DeclareLaunchArgument('cartographer_config_dir', default_value=cartographer_config_dir),
        DeclareLaunchArgument('configuration_basename', default_value=configuration_basename),
        DeclareLaunchArgument('resolution', default_value=resolution),
        DeclareLaunchArgument('publish_period_sec', default_value=publish_period_sec),

        robot_state_publisher_node,
        spawn_entity_node,
        cartographer_node,
        occupancy_grid_node,
        rviz_node,
    ])
