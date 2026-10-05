#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    gazebo_pkg_dir = get_package_share_directory('gazebo_ros')


    package_name = 'gazebo_src'
    pkg_share_dir = get_package_share_directory(package_name)
    world_file = os.path.join(pkg_share_dir, 'worlds', 'cafe_world.world')

    
    # Spawn Mobilebot in Gazebo
    spawn_mobilebot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'simple_robot_car'],
    )

    # Launch Gazebo server with the house world
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_pkg_dir, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world_file}.items()
    )

    # Launch Gazebo client
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_pkg_dir, 'launch', 'gzclient.launch.py'))
    )



    # Create and return launch description
    ld = LaunchDescription()

    ld.add_action(gzserver)
    ld.add_action(gzclient)
    ld.add_action(spawn_mobilebot)


    return ld

