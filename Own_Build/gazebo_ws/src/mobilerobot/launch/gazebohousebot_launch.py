#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'mobilerobot'

    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')

    # Paths
    urdf_file = os.path.join(
        get_package_share_directory(pkg_name),
        'urdf',
        'mobilebot.urdf.xacro'
    )
    world_file = os.path.join(
        get_package_share_directory('mobilerobot'),
        'worlds',
        'turtlebot3_house.world'
    )
    gazebo_launch_file = os.path.join(
        get_package_share_directory('gazebo_ros'),
        'launch',
        'gazebo.launch.py'
    )

    # Process xacro
    import xacro
    urdf_xml = xacro.process_file(urdf_file).toxml()
    robot_description = {'robot_description': urdf_xml}

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description, {'use_sim_time': use_sim_time}],
        output='screen'
    )

    # Include Gazebo with house world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch_file),
        launch_arguments={'world': world_file}.items()
    )

    # Spawn mobilebot
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'mobilebot',
            '-x', x_pose,
            '-y', y_pose,
            '-z', '0.01'
        ],
        output='screen'
    )

    # Launch description
    ld = LaunchDescription()

    # Add actions
    ld.add_action(robot_state_publisher)
    ld.add_action(gazebo)
    ld.add_action(spawn_entity)

    return ld