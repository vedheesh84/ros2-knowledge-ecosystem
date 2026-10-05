#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='learning_debugging', executable='noisy_node', output='screen'),
        Node(package='learning_debugging', executable='faulty_node', output='screen'),
    ])
