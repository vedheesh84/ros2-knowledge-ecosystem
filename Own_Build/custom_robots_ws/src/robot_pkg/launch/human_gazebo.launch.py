#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import RegisterEventHandler
from launch.actions import IncludeLaunchDescription
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_path = get_package_share_directory("robot_pkg")
    urdf_file = os.path.join(pkg_path, "urdf", "human_robot.urdf")
    controllers_file = os.path.join(pkg_path, "config", "human_controllers.yaml")

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("gazebo_ros"),
                "launch",
                "gazebo.launch.py",
            )
        )
    )

    spawn_humanoid = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity",
            "human_robot",
            "-file",
            urdf_file,
            "-x",
            "0.0",
            "-y",
            "0.0",
            "-z",
            "0.0",
        ],
        output="screen",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
            "--param-file",
            controllers_file,
        ],
        output="screen",
    )

    human_joint_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "human_joint_controller",
            "--controller-manager",
            "/controller_manager",
            "--param-file",
            controllers_file,
        ],
        output="screen",
    )

    return LaunchDescription([
        gazebo,
        spawn_humanoid,
        RegisterEventHandler(
            OnProcessExit(
                target_action=spawn_humanoid,
                on_exit=[joint_state_broadcaster_spawner],
            )
        ),
        RegisterEventHandler(
            OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[human_joint_controller_spawner],
            )
        ),
    ])
