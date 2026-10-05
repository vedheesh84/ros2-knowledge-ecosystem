#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Get the share directory of gazebo_ros package
    gazebo_pkg_dir = get_package_share_directory('gazebo_ros')
    
    # Path to empty world
    empty_world_path = os.path.join('/usr/share/gazebo-11/worlds', 'empty.world')

    # Include the Gazebo server (gzserver) launch
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg_dir, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': empty_world_path}.items()
    )

    # Include the Gazebo client (gzclient) launch
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg_dir, 'launch', 'gzclient.launch.py')
        )
    )

    # Create launch description and add actions
    ld = LaunchDescription()
    ld.add_action(gzserver)
    ld.add_action(gzclient)

    return ld
