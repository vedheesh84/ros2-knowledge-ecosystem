#!/usr/bin/env python3
"""Launch the complete integrated robot system."""

from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    # Start sensors first
    sensor_fusion = Node(
        package='learning_integration',
        executable='sensor_fusion_node',
        output='screen',
    )

    # Start executor
    command_executor = Node(
        package='learning_integration',
        executable='command_executor_node',
        output='screen',
    )

    # Start brain after others are ready
    robot_brain = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='learning_integration',
                executable='robot_brain_node',
                output='screen',
            )
        ]
    )

    return LaunchDescription([
        sensor_fusion,
        command_executor,
        robot_brain,
    ])
