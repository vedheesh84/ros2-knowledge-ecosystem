#!/usr/bin/env python3
"""Launch the FreeCAD drone model in RViz."""

import os
from urllib.parse import quote

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _load_robot_description(pkg_share: str) -> str:
  urdf_path = os.path.join(pkg_share, 'urdf', 'drone.urdf')
  with open(urdf_path, 'r', encoding='utf-8') as urdf_file:
    content = urdf_file.read()
  mesh_prefix = 'file://' + quote(os.path.join(os.path.abspath(pkg_share), 'meshes') + '/', safe='/:@')
  return content.replace('package://drone_pkg/meshes/', mesh_prefix)


def generate_launch_description():
  pkg_share = get_package_share_directory('drone_pkg')
  rviz_config = os.path.join(pkg_share, 'rviz', 'drone.rviz')
  use_sim_time = LaunchConfiguration('use_sim_time')

  robot_description = _load_robot_description(pkg_share)

  return LaunchDescription([
    DeclareLaunchArgument('use_sim_time', default_value='false'),

    Node(
      package='tf2_ros',
      executable='static_transform_publisher',
      name='world_to_base_link',
      output='screen',
      arguments=['0', '0', '0.6', '0', '0', '0', 'world', 'base_link'],
    ),
    Node(
      package='robot_state_publisher',
      executable='robot_state_publisher',
      name='robot_state_publisher',
      output='screen',
      parameters=[{
        'robot_description': robot_description,
        'publish_robot_description': True,
        'use_sim_time': use_sim_time,
      }],
    ),
    Node(
      package='drone_pkg',
      executable='propeller_spinner.py',
      name='propeller_spinner',
      output='screen',
      parameters=[{
        'use_sim_time': use_sim_time,
      }],
    ),
    Node(
      package='rviz2',
      executable='rviz2',
      name='rviz2',
      output='screen',
      arguments=['-d', rviz_config],
      parameters=[{'use_sim_time': use_sim_time}],
    ),
  ])
