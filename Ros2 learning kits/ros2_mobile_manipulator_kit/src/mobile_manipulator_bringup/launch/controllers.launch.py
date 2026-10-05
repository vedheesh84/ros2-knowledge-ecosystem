#!/usr/bin/env python3
"""
Mobile Manipulator - Controller Spawning
=========================================

LEARNING OBJECTIVES:
- Understand controller spawning independently
- See how to switch controller configurations
- Learn controller lifecycle (inactive → active)
- Practice debugging controller issues

WHAT THIS LAUNCH DOES:
1. Spawns joint_state_broadcaster
2. Spawns diff_drive_controller (mobile base)
3. Spawns arm_controller (manipulator)
4. Spawns gripper_controller (gripper)

PREREQUISITE:
- ros2_control_node OR gazebo_ros2_control must be running
- controller_manager service must be available

USAGE:
  # After starting hardware.launch.py or simulation.launch.py
  ros2 launch mobile_manipulator_bringup controllers.launch.py

  # Check controller status
  ros2 control list_controllers
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # ========================================
    # LAUNCH CONFIGURATIONS
    # ========================================
    controller_manager_name = LaunchConfiguration('controller_manager')

    return LaunchDescription([
        # ========================================
        # LAUNCH ARGUMENTS
        # ========================================
        DeclareLaunchArgument(
            'controller_manager',
            default_value='/controller_manager',
            description='Controller manager namespace'
        ),

        # ========================================
        # JOINT STATE BROADCASTER (t=0s)
        # ========================================
        # Must be first - provides /joint_states for other nodes
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=[
                'joint_state_broadcaster',
                '--controller-manager', controller_manager_name
            ],
            output='screen',
        ),

        # ========================================
        # MOTION CONTROLLERS (t=2s)
        # ========================================
        # Wait for joint_state_broadcaster to be active
        TimerAction(
            period=2.0,
            actions=[
                # Mobile base controller
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=[
                        'diff_drive_controller',
                        '--controller-manager', controller_manager_name
                    ],
                    output='screen',
                ),
                # Arm trajectory controller
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=[
                        'arm_controller',
                        '--controller-manager', controller_manager_name
                    ],
                    output='screen',
                ),
                # Gripper controller
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=[
                        'gripper_controller',
                        '--controller-manager', controller_manager_name
                    ],
                    output='screen',
                ),
            ]
        ),
    ])
