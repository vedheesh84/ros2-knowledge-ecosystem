#!/usr/bin/env python3

import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Package name
    pkg_name = "robot_pkg"

    # Paths
    pkg_path = get_package_share_directory(pkg_name)
    urdf_file = os.path.join(pkg_path, "urdf", "cat.urdf")

    gazebo_pkg = get_package_share_directory("gazebo_ros")
    world = os.path.join(gazebo_pkg, "worlds", "empty.world")

    # Read URDF
    with open(urdf_file, "r") as infp:
        robot_desc = infp.read()

    # Robot State Publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{
            "robot_description": robot_desc,
            "use_sim_time": True
        }]
    )

    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, "launch", "gazebo.launch.py")
        ),
        launch_arguments={"world": world}.items()
    )

    # Spawn Robot in Gazebo
    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "cat_robot",
            "-topic", "robot_description",
            "-x", "0",
            "-y", "0",
            "-z", "0.3"
        ],
        output="screen"
    )

    # Joint State Publisher GUI (optional sliders)
    joint_state_publisher = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        output="screen"
    )

    # Teleop Keyboard
    teleop_keyboard = ExecuteProcess(
        cmd=[
            "xterm", "-e",
            "ros2", "run", "teleop_twist_keyboard", "teleop_twist_keyboard"
        ],
        output="screen"
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        joint_state_publisher,
        teleop_keyboard,
    ])
