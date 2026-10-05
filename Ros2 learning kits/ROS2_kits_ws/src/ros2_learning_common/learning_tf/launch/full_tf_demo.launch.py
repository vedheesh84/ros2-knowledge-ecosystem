#!/usr/bin/env python3
"""TF Demo Launch - All TF nodes together."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    static_tf = Node(
        package='learning_tf',
        executable='static_tf_node',
        name='static_tf',
        output='screen',
    )

    dynamic_tf = Node(
        package='learning_tf',
        executable='dynamic_tf_node',
        name='dynamic_tf',
        output='screen',
    )

    tf_listener = Node(
        package='learning_tf',
        executable='tf_listener_node',
        name='tf_listener',
        output='screen',
    )

    return LaunchDescription([static_tf, dynamic_tf, tf_listener])
