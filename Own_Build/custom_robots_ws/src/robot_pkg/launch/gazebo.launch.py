#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    pkg_path = get_package_share_directory("robot_pkg")
    rviz_config = os.path.join(pkg_path, "rviz", "mapping.rviz")
    slam_config = os.path.join(pkg_path, "config", "mapper_params_online_async.yaml")
    world_file = os.path.join(pkg_path, "worlds", "mapping_world.world")

    robot_desc = ParameterValue(
        Command([
            "xacro ",
            PathJoinSubstitution([pkg_path, "urdf", "robot_model.urdf.xacro"])
        ]),
        value_type=str
    )

    return LaunchDescription([
        # Spawn robot_state_publisher
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            parameters=[{
                "robot_description": robot_desc,
                "use_sim_time": True
            }],
            output="screen"
        ),

        # Launch Gazebo
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory("gazebo_ros"),
                    "launch",
                    "gazebo.launch.py"
                )
            ),
            launch_arguments={"world": world_file}.items(),
        ),

        # Spawn robot in Gazebo
        Node(
            package="gazebo_ros",
            executable="spawn_entity.py",
            arguments=["-topic", "robot_description", "-entity", "diff_bot"],
            output="screen"
        ),

        # Online SLAM mapping from /scan + odom -> /map
        Node(
            package="slam_toolbox",
            executable="async_slam_toolbox_node",
            name="slam_toolbox",
            parameters=[
                slam_config,
                {"use_sim_time": True}
            ],
            output="screen"
        ),

        # RViz for mapping topics: TF, robot model, /scan, /odom, and /map
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["-d", rviz_config],
            parameters=[{"use_sim_time": True}],
            output="screen"
        ),

        # Teleop Keyboard
        ExecuteProcess(
            cmd=[
                "xterm", "-e",
                "ros2", "run", "teleop_twist_keyboard", "teleop_twist_keyboard"
            ],
            output="screen"
        )
    ])
