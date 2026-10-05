#!/usr/bin/env python3
"""
Simple Publisher-Subscriber Launch File.

This launch file demonstrates starting a simple publisher and subscriber
pair for basic ROS2 communication.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description with publisher and subscriber nodes."""
    return LaunchDescription([
        # Publisher node
        Node(
            package='cex_pkg',
            executable='simple_publisher.py',
            name='talker',
            output='screen'
        ),
        # Subscriber node
        Node(
            package='cex_pkg',
            executable='simple_subscriber.py',
            name='listener',
            output='screen'
        )
    ])
