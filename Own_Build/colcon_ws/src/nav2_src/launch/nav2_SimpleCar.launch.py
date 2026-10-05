#!/usr/bin/env python3
"""
Navigation2 Simple Car Launch File.

This launch file starts the Navigation2 stack components including
planner, behavior tree navigator, waypoint follower, and lifecycle manager.
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    """Generate launch description for Nav2 simple car navigation."""
    # Package paths
    bringup_dir = get_package_share_directory('nav2_src')
    nav2_params = os.path.join(bringup_dir, 'config', 'nav2_params.yaml')

    # Default map file path using package share directory
    rviz_pkg_dir = get_package_share_directory('rviz_tutorial')
    default_map_file = os.path.join(rviz_pkg_dir, 'maps', 'turtle3_map.save.yaml')

    # Launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    map_yaml_file = LaunchConfiguration('map', default=default_map_file)

    # Declare launch arguments
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_map_yaml = DeclareLaunchArgument(
        'map',
        default_value=default_map_file,
        description='Full path to map yaml file to load'
    )

    # Lifecycle manager node
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': [
                'map_server',
                'amcl',
                'planner_server',
                'controller_server',
                'bt_navigator',
                'waypoint_follower'
            ]
        }],
    )

    # Planner server node
    planner = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}, nav2_params],
    )

    # Behavior Tree Navigator node
    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}, nav2_params],
    )

    # Waypoint Follower node
    waypoint_follower = Node(
        package='nav2_waypoint_follower',
        executable='waypoint_follower',
        name='waypoint_follower',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}, nav2_params],
    )

    # Build launch description
    ld = LaunchDescription()

    # Add launch arguments
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_map_yaml)

    # Add Nav2 nodes
    ld.add_action(planner)
    ld.add_action(bt_navigator)
    ld.add_action(waypoint_follower)
    ld.add_action(lifecycle_manager)

    return ld
