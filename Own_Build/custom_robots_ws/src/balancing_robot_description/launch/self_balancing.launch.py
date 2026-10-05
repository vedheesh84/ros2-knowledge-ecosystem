import tempfile
#!/usr/bin/env python3
"""Launch Gazebo + RViz with the FreeCAD self-balancing robot.

Terminal 1 — simulation:
  ros2 launch balancing_robot_description self_balancing.launch.py

Terminal 2 — keyboard teleop (click this terminal before pressing keys):
  ros2 run teleop_twist_keyboard teleop_twist_keyboard

Teleop keys: i=forward, ,=back, j/l=turn, k=stop, q/z=speed
"""

import os
from urllib.parse import quote

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
  DeclareLaunchArgument,
  ExecuteProcess,
  GroupAction,
  IncludeLaunchDescription,
  RegisterEventHandler,
  TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node, SetParameter


def _abs_mesh_prefix(pkg_share: str) -> str:
  return os.path.join(os.path.abspath(pkg_share), 'meshes') + '/'


def _load_robot_description(pkg_share: str, for_gazebo: bool = False) -> str:
  urdf_path = os.path.join(pkg_share, 'urdf', 'selfbalance.urdf')
  with open(urdf_path, 'r', encoding='utf-8') as urdf_file:
    content = urdf_file.read()
  if for_gazebo:
    return content.replace(
      'package://balancing_robot_description/meshes/',
      _abs_mesh_prefix(pkg_share),
    )
  mesh_prefix = 'file://' + quote(_abs_mesh_prefix(pkg_share), safe='/:@')
  return content.replace('package://balancing_robot_description/meshes/', mesh_prefix)


def _robot_state_publisher(robot_description: str, use_sim_time) -> Node:
  return Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    name='robot_state_publisher',
    output='screen',
    parameters=[{
      'robot_description': robot_description,
      'publish_robot_description': True,
      'use_sim_time': use_sim_time,
    }],
  )


def generate_launch_description():
  pkg_share = get_package_share_directory('balancing_robot_description')
  rviz_config = os.path.join(pkg_share, 'rviz', 'self_balancing.rviz')
  gazebo_ros_share = get_package_share_directory('gazebo_ros')

  robot_description_rviz = _load_robot_description(pkg_share, for_gazebo=False)
  robot_description_gazebo = _load_robot_description(pkg_share, for_gazebo=True)

  gazebo_urdf_file = os.path.join(tempfile.gettempdir(), 'selfbalance_gazebo.urdf')
  with open(gazebo_urdf_file, 'w', encoding='utf-8') as gazebo_urdf:
    gazebo_urdf.write(robot_description_gazebo)

  use_sim_time = LaunchConfiguration('use_sim_time')
  use_rviz = LaunchConfiguration('use_rviz')
  use_gazebo = LaunchConfiguration('use_gazebo')
  world = LaunchConfiguration('world')
  spawn_z = LaunchConfiguration('spawn_z')

  rviz_only = PythonExpression([
    "'", use_rviz, "' == 'true' and '", use_gazebo, "' != 'true'",
  ])

  cleanup_gazebo = ExecuteProcess(
    cmd=['bash', '-c',
         'pkill -9 -x gzserver 2>/dev/null || true; '
         'pkill -9 -x gzclient 2>/dev/null || true; '
         'pkill -9 -f "/lib/robot_state_publisher/robot_state_publisher" 2>/dev/null || true; '
         'sleep 1; true'],
    output='log',
  )

  gazebo_launch = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(gazebo_ros_share, 'launch', 'gazebo.launch.py'),
    ),
    launch_arguments={'world': world, 'verbose': 'false'}.items(),
  )

  spawn_robot = Node(
    package='gazebo_ros',
    executable='spawn_entity.py',
    name='spawn_selfbalance',
    output='screen',
    arguments=[
      '-entity', 'selfbalance',
      '-file', gazebo_urdf_file,
      '-x', '0.0', '-y', '0.0', '-z', spawn_z,
    ],
    parameters=[{'use_sim_time': use_sim_time}],
  )

  robot_state_publisher = _robot_state_publisher(robot_description_rviz, use_sim_time)

  rviz_node = Node(
    package='rviz2',
    executable='rviz2',
    name='rviz2',
    output='screen',
    arguments=['-d', rviz_config],
    parameters=[{'use_sim_time': use_sim_time}],
  )

  gazebo_stack = GroupAction([
    cleanup_gazebo,
    RegisterEventHandler(
      OnProcessExit(
        target_action=cleanup_gazebo,
        on_exit=[
          TimerAction(period=1.0, actions=[gazebo_launch]),
          TimerAction(period=6.0, actions=[spawn_robot]),
          TimerAction(period=8.0, actions=[robot_state_publisher]),
          TimerAction(
            period=10.0,
            actions=[rviz_node],
            condition=IfCondition(use_rviz),
          ),
        ],
      ),
    ),
  ])

  rviz_stack = GroupAction([
    robot_state_publisher,
    Node(
      package='joint_state_publisher_gui',
      executable='joint_state_publisher_gui',
      name='joint_state_publisher_gui',
      output='screen',
    ),
    rviz_node,
  ])

  return LaunchDescription([
    DeclareLaunchArgument('use_sim_time', default_value='true'),
    DeclareLaunchArgument('use_rviz', default_value='true'),
    DeclareLaunchArgument('use_gazebo', default_value='true'),
    DeclareLaunchArgument(
      'world',
      default_value=os.path.join(gazebo_ros_share, 'worlds', 'empty.world'),
    ),
    DeclareLaunchArgument('spawn_z', default_value='0.0'),

    SetParameter(name='use_sim_time', value=use_sim_time),

    GroupAction([gazebo_stack], condition=IfCondition(use_gazebo)),
    GroupAction([rviz_stack], condition=IfCondition(rviz_only)),
  ])
