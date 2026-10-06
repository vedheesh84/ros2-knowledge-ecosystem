"""
display.launch.py - Visualize quadruped robot in RViz

This launch file:
1. Loads the URDF via xacro
2. Starts robot_state_publisher (TF from /joint_states)
3. Starts joint_state_publisher_gui (interactive joint control)
4. Starts RViz with preset configuration
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Package paths
    pkg_share = FindPackageShare('quadruped_description').find('quadruped_description')
    urdf_file = os.path.join(pkg_share, 'urdf', 'quadruped.urdf.xacro')
    rviz_config = os.path.join(pkg_share, 'rviz', 'display.rviz')

    # Launch arguments
    use_gui = LaunchConfiguration('use_gui')
    use_rviz = LaunchConfiguration('use_rviz')

    # Robot description from xacro
    robot_description = ParameterValue(
        Command([
            'xacro ', urdf_file,
            ' use_sim:=false',
            ' use_fake_hardware:=true'
        ]),
        value_type=str
    )

    return LaunchDescription([
        # Arguments
        DeclareLaunchArgument(
            'use_gui',
            default_value='true',
            description='Use joint_state_publisher_gui for interactive control'
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Launch RViz for visualization'
        ),

        # Robot State Publisher - publishes TF from /joint_states
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        ),

        # Joint State Publisher GUI - interactive joint control
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            condition=IfCondition(use_gui)
        ),

        # Joint State Publisher (non-GUI fallback)
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            condition=UnlessCondition(use_gui)
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            condition=IfCondition(use_rviz)
        ),
    ])
