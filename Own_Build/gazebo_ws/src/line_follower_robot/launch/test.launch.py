#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription

def generate_launch_description():
    pkg_name = 'line_follower_robot'
    pkg_share_dir = get_package_share_directory(pkg_name)
    sdf_file = os.path.join(pkg_share_dir, 'models', 'line_follower_robot.sdf')

    # Spawn SDF model in Gazebo
    spawn_sdf_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-file', sdf_file, '-entity', 'line_follower_robot'],
        output='screen'
    )

    # Launch Gazebo server (default empty world)
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gzserver.launch.py')
        )
    )

    # Launch Gazebo client
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gzclient.launch.py')
        )
    )

    ld = LaunchDescription()
    ld.add_action(gzserver)
    ld.add_action(gzclient)
    ld.add_action(spawn_sdf_node)

    return ld
