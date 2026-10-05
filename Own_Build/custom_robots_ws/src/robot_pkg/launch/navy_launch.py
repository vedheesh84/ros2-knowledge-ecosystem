#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_path = get_package_share_directory("robot_pkg")
    gazebo_pkg = get_package_share_directory("gazebo_ros")

    xacro_file = os.path.join(pkg_path, "urdf", "navy.urdf.xacro")
    rviz_config = os.path.join(pkg_path, "rviz", "navy.rviz")
    world = os.path.join(gazebo_pkg, "worlds", "empty.world")

    robot_description = ParameterValue(
        Command(["xacro ", xacro_file]),
        value_type=str,
    )

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
            "robot_description": robot_description,
            "use_sim_time": True,
        }],
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        output="screen",
        parameters=[{"use_sim_time": True}],
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
            "-entity", "navy",
            "-topic", "robot_description",
            "-x", "0",
            "-y", "0",
            "-z", "0.01",
            "-timeout", "60",
        ],
        output="screen",
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
        parameters=[{"use_sim_time": True}],
        output="screen",
    )

    return LaunchDescription([
        cleanup_gazebo,
        TimerAction(period=1.5, actions=[gazebo, joint_state_publisher, robot_state_publisher, rviz]),
        TimerAction(period=6.0, actions=[spawn_entity]),
    ])
