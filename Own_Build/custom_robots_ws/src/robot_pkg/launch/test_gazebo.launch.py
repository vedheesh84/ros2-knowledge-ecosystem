#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription


def generate_launch_description():
    # ==============================
    # 1. Paths
    # ==============================
    pkg_path = get_package_share_directory('robot_pkg')
    xacro_file = os.path.join(pkg_path, 'urdf', 'gazebo_urdf.xacro')
    rviz_file = os.path.join(pkg_path, 'rviz', 'car_model.rviz')

    # ==============================
    # 2. Launch argument for model (optional)
    # ==============================
    model_arg = DeclareLaunchArgument(
        'model',
        default_value=xacro_file,
        description='Full path to robot urdf file'
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # ==============================
    # 3. Robot State Publisher
    # ==============================
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': Command(['xacro ', LaunchConfiguration('model')]),
            'use_sim_time': True
        }],
        output='screen'
    )

    # ==============================
    # 4. Gazebo Launch
    # ==============================
    # Launch Gazebo with empty world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={'world': ''}.items()
    )

    # ==============================
    # 5. Spawn robot in Gazebo
    # ==============================
    spawn_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'my_robot'
        ],
        output='screen'
    )

    # ==============================
    # 6. RViz2
    # ==============================
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_file],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # ==============================
    # 7. Launch Description
    # ==============================
    return LaunchDescription([
        model_arg,
        joint_state_publisher_node,
        rsp_node,
        gazebo,
        spawn_node,
        rviz_node
    ])
