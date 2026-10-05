#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='learning_simulation', executable='sim_time_node', output='screen'),
        Node(package='learning_simulation', executable='fake_actuator_node', output='screen'),
    ])
