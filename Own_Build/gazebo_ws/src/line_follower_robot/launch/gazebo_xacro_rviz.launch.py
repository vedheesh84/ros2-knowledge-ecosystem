#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    robot_name = 'line_follower_robot'
    
    # Paths
    package_name = 'line_follower_robot'
    pkg_share_dir = get_package_share_directory(package_name)
    urdf_file = os.path.join(pkg_share_dir, 'urdf', 'line_follower_robot.urdf.xacro')

    gazebo_pkg_dir = get_package_share_directory('gazebo_ros')
    turtlebot3_pkg_dir = get_package_share_directory('turtlebot3_gazebo')
    world_file = os.path.join(turtlebot3_pkg_dir, 'worlds', 'empty_world.world')

    # Use simulation time
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Robot description
    robot_description_content = Command(['xacro', urdf_file])
    robot_description_param = {'robot_description': robot_description_content}

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description_param, {'use_sim_time': use_sim_time}],
        output='screen'
    )

    # Spawn robot in Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', robot_name],
        output='screen'
    )

    # Gazebo server
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg_dir, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world_file}.items()
    )

    # Gazebo client
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg_dir, 'launch', 'gzclient.launch.py')
        )
    )

    # Launch description
    ld = LaunchDescription()
    ld.add_action(robot_state_publisher_node)
    ld.add_action(gzserver)
    ld.add_action(gzclient)
    ld.add_action(spawn_robot)

    return ld
