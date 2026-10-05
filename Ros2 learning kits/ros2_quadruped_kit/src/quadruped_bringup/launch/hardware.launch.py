"""
hardware.launch.py - Launch quadruped on real hardware

LEARNING OBJECTIVES:
- Real hardware vs simulation differences
- Controller lifecycle management
- Safety considerations for real robot

Launch sequence:
1. robot_state_publisher (TF)
2. controller_manager with real hardware plugin
3. Load and activate controllers
4. Optional RViz for monitoring
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Package directories
    pkg_description = get_package_share_directory('quadruped_description')
    pkg_bringup = get_package_share_directory('quadruped_bringup')

    # Launch arguments
    use_rviz = LaunchConfiguration('use_rviz')
    use_fake_hardware = LaunchConfiguration('use_fake_hardware')

    # Robot description from xacro
    robot_description = Command([
        'xacro ',
        os.path.join(pkg_description, 'urdf', 'quadruped.urdf.xacro'),
        ' use_sim:=false',
        ' use_fake_hardware:=', use_fake_hardware,
    ])

    # Controller config
    controller_config = os.path.join(pkg_description, 'config', 'ros2_controllers.yaml')
    rviz_config = os.path.join(pkg_bringup, 'rviz', 'hardware.rviz')

    return LaunchDescription([
        # ==================== ARGUMENTS ====================
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Launch RViz for monitoring'
        ),
        DeclareLaunchArgument(
            'use_fake_hardware',
            default_value='true',
            description='Use mock hardware (safe for testing)'
        ),

        # ==================== ROBOT STATE PUBLISHER ====================
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        ),

        # ==================== CONTROLLER MANAGER ====================
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[
                {'robot_description': robot_description},
                controller_config,
            ],
            output='screen',
        ),

        # ==================== LOAD CONTROLLERS ====================
        # Joint State Broadcaster (first)
        TimerAction(
            period=2.0,
            actions=[
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
                    output='screen',
                ),
            ],
        ),

        # Leg Controller
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['leg_controller', '--controller-manager', '/controller_manager'],
                    output='screen',
                ),
            ],
        ),

        # IMU Broadcaster
        TimerAction(
            period=3.5,
            actions=[
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['imu_broadcaster', '--controller-manager', '/controller_manager'],
                    output='screen',
                ),
            ],
        ),

        # ==================== RVIZ ====================
        TimerAction(
            period=4.0,
            actions=[
                Node(
                    package='rviz2',
                    executable='rviz2',
                    name='rviz2',
                    output='screen',
                    arguments=['-d', rviz_config],
                    condition=IfCondition(use_rviz),
                ),
            ],
        ),
    ])
