#!/usr/bin/env python3
"""Lifecycle Demo Launch - Start sensor and controller."""

from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    sensor = Node(
        package='learning_lifecycle',
        executable='lifecycle_sensor_node',
        name='lifecycle_sensor',
        output='screen',
    )

    controller = TimerAction(
        period=2.0,
        actions=[
            Node(
                package='learning_lifecycle',
                executable='lifecycle_controller_node',
                name='lifecycle_controller',
                output='screen',
            )
        ]
    )

    return LaunchDescription([sensor, controller])
