#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.conditions import IfCondition
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_path = get_package_share_directory("robot_pkg")
    gazebo_pkg = get_package_share_directory("gazebo_ros")
    nav2_bringup_dir = get_package_share_directory("nav2_bringup")

    xacro_file = os.path.join(pkg_path, "urdf", "navy.urdf.xacro")
    rviz_config = os.path.join(pkg_path, "rviz", "navy_navigation.rviz")
    nav2_params = os.path.join(pkg_path, "config", "navy_nav2_params.yaml")
    map_file = os.path.join(pkg_path, "maps", "my_map.yaml")
    world_file = os.path.join(pkg_path, "worlds", "warehouse_world.world")
    use_rviz = LaunchConfiguration("use_rviz")

    # Robot spawn pose (must match AMCL initial_pose in navy_nav2_params.yaml)
    spawn_x = "0"
    spawn_y = "-6"
    spawn_z = "0.01"

    robot_description = ParameterValue(
        Command(["xacro ", xacro_file]),
        value_type=str,
    )

    cleanup = ExecuteProcess(
        cmd=[
            "bash", "-c",
            "pkill -9 gzserver 2>/dev/null || true; "
            "pkill -9 gzclient 2>/dev/null || true; "
            "pkill -f component_container_isolated 2>/dev/null || true",
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

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, "launch", "gazebo.launch.py")
        ),
        launch_arguments={"world": world_file}.items(),
    )

    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-entity", "navy",
            "-topic", "robot_description",
            "-x", spawn_x,
            "-y", spawn_y,
            "-z", spawn_z,
            "-timeout", "60",
        ],
        output="screen",
    )

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, "launch", "bringup_launch.py")
        ),
        launch_arguments={
            "slam": "False",
            "map": map_file,
            "use_sim_time": "true",
            "params_file": nav2_params,
            "autostart": "true",
            # Separate processes avoid lifecycle race in the component container
            "use_composition": "False",
            "use_respawn": "True",
        }.items(),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
        parameters=[{"use_sim_time": True}],
        output="screen",
        condition=IfCondition(use_rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "use_rviz",
            default_value="false",
            description="Launch RViz2 if true",
        ),
        cleanup,
        TimerAction(period=2.0, actions=[gazebo, robot_state_publisher]),
        TimerAction(period=10.0, actions=[spawn_entity]),
        # Wait for Gazebo + robot sensors before starting Nav2
        TimerAction(period=20.0, actions=[nav2_bringup]),
        TimerAction(period=25.0, actions=[rviz]),
    ])
