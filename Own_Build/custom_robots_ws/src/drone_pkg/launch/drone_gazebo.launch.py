#!/usr/bin/env python3
"""Launch Gazebo, spawn the FreeCAD drone, and optionally open RViz."""

import os
from urllib.parse import quote

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetParameter
from launch_ros.parameter_descriptions import ParameterValue


def _abs_mesh_prefix(pkg_share: str) -> str:
  return os.path.join(os.path.abspath(pkg_share), 'meshes') + '/'


def _load_robot_description(pkg_share: str, for_gazebo: bool = False) -> str:
  urdf_path = os.path.join(pkg_share, 'urdf', 'drone.urdf')
  with open(urdf_path, 'r', encoding='utf-8') as urdf_file:
    content = urdf_file.read()
  if for_gazebo:
    return content.replace('package://drone_pkg/meshes/', _abs_mesh_prefix(pkg_share))
  mesh_prefix = 'file://' + quote(_abs_mesh_prefix(pkg_share), safe='/:@')
  return content.replace('package://drone_pkg/meshes/', mesh_prefix)


def generate_launch_description():
  pkg_share = get_package_share_directory('drone_pkg')
  gazebo_ros_share = get_package_share_directory('gazebo_ros')
  rviz_config = os.path.join(pkg_share, 'rviz', 'drone.rviz')

  use_sim_time = LaunchConfiguration('use_sim_time')
  use_rviz = LaunchConfiguration('use_rviz')
  start_controller = LaunchConfiguration('start_controller')
  world = LaunchConfiguration('world')
  spawn_z = LaunchConfiguration('spawn_z')
  entity_name = LaunchConfiguration('entity_name')

  robot_description_rviz = _load_robot_description(pkg_share, for_gazebo=False)
  robot_description_gazebo = _load_robot_description(pkg_share, for_gazebo=True)
  gazebo_urdf_file = '/tmp/drone_pkg_gazebo.urdf'
  with open(gazebo_urdf_file, 'w', encoding='utf-8') as gazebo_urdf:
    gazebo_urdf.write(robot_description_gazebo)

  gazebo_launch = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(os.path.join(gazebo_ros_share, 'launch', 'gazebo.launch.py')),
    launch_arguments={'world': world, 'verbose': 'false'}.items(),
  )

  spawn_drone = Node(
    package='gazebo_ros',
    executable='spawn_entity.py',
    name='spawn_freecad_drone',
    output='screen',
    arguments=[
      '-entity', entity_name,
      '-file', gazebo_urdf_file,
      '-x', '0.0',
      '-y', '0.0',
      '-z', spawn_z,
    ],
    parameters=[{'use_sim_time': use_sim_time}],
  )

  # Fallback world->base_link TF when the manual controller is disabled.
  static_tf = Node(
    package='tf2_ros',
    executable='static_transform_publisher',
    name='world_to_base_link_static',
    output='screen',
    arguments=['0', '0', spawn_z, '0', '0', '0', 'world', 'base_link'],
    parameters=[{'use_sim_time': use_sim_time}],
    condition=UnlessCondition(start_controller),
  )

  robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    name='robot_state_publisher',
    output='screen',
    parameters=[{
      'robot_description': robot_description_rviz,
      'publish_robot_description': True,
      'use_sim_time': use_sim_time,
    }],
  )

  joint_state_publisher = Node(
    package='drone_pkg',
    executable='propeller_spinner.py',
    name='propeller_spinner',
    output='screen',
    parameters=[{
      'use_sim_time': use_sim_time,
    }],
  )

  controller = Node(
    package='drone_pkg',
    executable='manual_drone_controller',
    name='manual_drone_controller',
    output='screen',
    parameters=[{
      'entity_name': entity_name,
      'initial_z': ParameterValue(spawn_z, value_type=float),
      'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
    }],
    condition=IfCondition(start_controller),
  )

  rviz_node = Node(
    package='rviz2',
    executable='rviz2',
    name='rviz2',
    output='screen',
    arguments=['-d', rviz_config],
    parameters=[{'use_sim_time': use_sim_time}],
    condition=IfCondition(use_rviz),
  )

  return LaunchDescription([
    DeclareLaunchArgument('use_sim_time', default_value='true'),
    DeclareLaunchArgument('use_rviz', default_value='true'),
    DeclareLaunchArgument('start_controller', default_value='true'),
    DeclareLaunchArgument('spawn_z', default_value='0.60'),
    DeclareLaunchArgument('entity_name', default_value='drone'),
    DeclareLaunchArgument(
      'world',
      default_value=os.path.join(pkg_share, 'worlds', 'drone_empty.world'),
    ),

    SetParameter(name='use_sim_time', value=use_sim_time),
    gazebo_launch,
    TimerAction(period=4.0, actions=[spawn_drone]),
    # Publish robot TF tree and world->base_link as soon as spawn is underway.
    TimerAction(period=4.5, actions=[robot_state_publisher, joint_state_publisher, static_tf]),
    TimerAction(period=5.0, actions=[controller]),
    GroupAction([TimerAction(period=6.0, actions=[rviz_node])]),
  ])
