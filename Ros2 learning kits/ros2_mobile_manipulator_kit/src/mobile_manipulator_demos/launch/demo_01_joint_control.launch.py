#!/usr/bin/env python3
"""
Demo 01: Arm Joint Control
==========================

LEARNING OBJECTIVES:
- Understand ros2_control joint trajectory controller
- See joint state publishing and visualization
- Learn to send joint commands via topic/action
- Practice verifying arm motion in RViz

WHAT THIS DEMO DOES:
1. Launches robot with arm controllers
2. Spawns joint_state_broadcaster + arm_controller
3. Runs demo script that sends joint commands
4. Shows motion in RViz

BUILDS ON:
- ROS2_kits_ws: learning_lifecycle (lifecycle nodes)
- ROS2_kits_ws: learning_execution (launch files)

TRY THIS:
  # In another terminal, send joint command manually:
  ros2 topic pub /arm_controller/joint_trajectory \\
    trajectory_msgs/JointTrajectory \\
    '{joint_names: [joint_1], points: [{positions: [1.0], time_from_start: {sec: 2}}]}' --once

USAGE:
  ros2 launch mobile_manipulator_demos demo_01_joint_control.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_bringup = get_package_share_directory('mobile_manipulator_bringup')
    pkg_demos = get_package_share_directory('mobile_manipulator_demos')

    return LaunchDescription([
        # ========================================
        # LAUNCH ARGUMENTS
        # ========================================
        DeclareLaunchArgument(
            'use_sim',
            default_value='true',
            description='Use simulation (true) or hardware (false)'
        ),

        # ========================================
        # ROBOT BRINGUP
        # ========================================
        # Launches robot_state_publisher, controllers
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(pkg_bringup, 'launch', 'simulation.launch.py')
            ]),
            launch_arguments={
                'use_rviz': 'true',
            }.items(),
        ),

        # ========================================
        # DEMO SCRIPT (t=15s)
        # ========================================
        # Wait for controllers to be ready
        TimerAction(
            period=15.0,
            actions=[
                Node(
                    package='mobile_manipulator_demos',
                    executable='demo_01_joint_control.py',
                    name='demo_01',
                    output='screen',
                    parameters=[{'use_sim_time': True}],
                ),
            ]
        ),
    ])
