#!/usr/bin/env python3
"""Keyboard teleop for the CAD mobile robot.

Run in a SECOND terminal while cad_launch.py is running:

  ros2 launch cad_description cad_teleop.launch.py

Controls (teleop_twist_keyboard):
  i / ,  = forward / backward
  j / l  = turn left / right
  u / o  = forward + left / forward + right
  k      = stop
  q / z  = increase / decrease speed
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
  cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')

  return LaunchDescription([
    DeclareLaunchArgument(
      'cmd_vel_topic',
      default_value='/cmd_vel',
      description='Topic to publish Twist commands',
    ),

    Node(
      package='teleop_twist_keyboard',
      executable='teleop_twist_keyboard',
      name='teleop_twist_keyboard',
      output='screen',
      remappings=[('/cmd_vel', cmd_vel_topic)],
      parameters=[{
        'speed': 0.5,
        'turn': 1.0,
      }],
    ),
  ])
