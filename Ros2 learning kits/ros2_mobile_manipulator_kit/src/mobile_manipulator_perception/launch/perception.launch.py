#!/usr/bin/env python3
"""
Perception Launch File
======================

LEARNING OBJECTIVES:
- Launch camera driver and perception pipeline
- Configure detection parameters
- Understand camera topic remapping

USAGE:
  ros2 launch mobile_manipulator_perception perception.launch.py
  ros2 launch mobile_manipulator_perception perception.launch.py target_color:=blue
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Package directory
    pkg_perception = get_package_share_directory('mobile_manipulator_perception')

    # Config file
    config_file = os.path.join(pkg_perception, 'config', 'perception_params.yaml')

    # Launch configurations
    target_color = LaunchConfiguration('target_color')
    object_width = LaunchConfiguration('object_width')

    return LaunchDescription([
        # ========================================
        # LAUNCH ARGUMENTS
        # ========================================
        DeclareLaunchArgument(
            'target_color',
            default_value='red',
            description='Color to detect (red, green, blue, yellow)'
        ),
        DeclareLaunchArgument(
            'object_width',
            default_value='0.05',
            description='Known object width in meters'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock'
        ),

        # ========================================
        # PERCEPTION NODE
        # ========================================
        Node(
            package='mobile_manipulator_perception',
            executable='perception_node.py',
            name='perception_node',
            output='screen',
            parameters=[
                config_file,
                {
                    'target_color': target_color,
                    'object_width': object_width,
                    'use_sim_time': LaunchConfiguration('use_sim_time'),
                }
            ],
            remappings=[
                ('/camera/image_raw', '/camera/image_raw'),
                ('/camera/camera_info', '/camera/camera_info'),
            ]
        ),
    ])
