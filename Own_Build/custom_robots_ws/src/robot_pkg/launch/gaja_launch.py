#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_path = get_package_share_directory("robot_pkg")
    urdf_file = os.path.join(pkg_path, "urdf", "gaja.urdf")

    gazebo_pkg = get_package_share_directory("gazebo_ros")
    world = os.path.join(gazebo_pkg, "worlds", "empty.world")

    with open(urdf_file, "r") as infp:
        robot_desc = infp.read()

    # Stop leftover Gazebo from a previous session (avoids port 11345 conflict)
    cleanup_gazebo = ExecuteProcess(
        cmd=[
            "bash", "-c",
            "pkill -9 gzserver 2>/dev/null || true; "
            "pkill -9 gzclient 2>/dev/null || true",
        ],
        output="screen",
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_desc,
            "use_sim_time": True,
        }],
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, "launch", "gazebo.launch.py")
        ),
        launch_arguments={"world": world}.items(),
    )

    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "gaja",
            "-topic", "robot_description",
            "-x", "0",
            "-y", "0",
            "-z", "0.05",
            "-timeout", "60",
        ],
        output="screen",
    )

    return LaunchDescription([
        cleanup_gazebo,
        TimerAction(period=1.5, actions=[gazebo, robot_state_publisher]),
        TimerAction(period=6.0, actions=[spawn_entity]),
    ])
