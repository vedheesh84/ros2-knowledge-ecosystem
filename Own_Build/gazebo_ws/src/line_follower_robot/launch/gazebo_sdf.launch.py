#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, TextSubstitution, PathJoinSubstitution
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # ------------------------
    # Launch arguments
    # ------------------------
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='empty_world',
        description='Gazebo world to load (from gazebo_ros worlds folder)'
    )

    robot_name_arg = DeclareLaunchArgument(
        'robot_name',
        default_value='line_follower_robot',
        description='Name of the robot entity in Gazebo'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # ------------------------
    # Paths
    # ------------------------
    pkg_share = get_package_share_directory('line_follower_robot')
    sdf_file = os.path.join(pkg_share, 'models', 'line_follower_robot.sdf')

    gazebo_ros_pkg = get_package_share_directory('gazebo_ros')
    gazebo_world = PathJoinSubstitution([
        gazebo_ros_pkg,
        'worlds',
        LaunchConfiguration('world'),
        TextSubstitution(text='.world')
    ])

    # ------------------------
    # Read SDF content for RViz
    # ------------------------
    # robot_state_publisher needs URDF string; SDF can be visualized in RViz if converted to URDF (optional)
    urdf_path = os.path.join(pkg_share, 'urdf', 'line_follower_robot.urdf')
    with open(urdf_path, 'r') as f:
        robot_description_content = f.read()
    robot_description = {'robot_description': robot_description_content}

    # ------------------------
    # Nodes
    # ------------------------
    # Robot State Publisher (for TFs)
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description, {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    # RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    # Spawn SDF in Gazebo
    spawn_sdf_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-file', sdf_file,
                   '-entity', LaunchConfiguration('robot_name')],
        output='screen'
    )

    # Gazebo server
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': gazebo_world}.items()
    )

    # Gazebo client
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_pkg, 'launch', 'gzclient.launch.py')
        )
    )

    # ------------------------
    # Launch Description
    # ------------------------
    ld = LaunchDescription()
    ld.add_action(world_arg)
    ld.add_action(robot_name_arg)
    ld.add_action(use_sim_time_arg)
    ld.add_action(gzserver)
    ld.add_action(gzclient)
    ld.add_action(rsp_node)
    ld.add_action(rviz_node)
    ld.add_action(spawn_sdf_node)

    return ld
