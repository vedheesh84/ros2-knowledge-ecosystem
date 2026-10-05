"""
simulation.launch.py - Launch quadruped in Gazebo simulation

LEARNING OBJECTIVES:
- Gazebo Harmonic integration with ROS 2
- gz_ros2_control for simulated hardware
- Controller lifecycle and timing

Launch sequence:
1. robot_state_publisher (TF from /joint_states)
2. Gazebo simulator
3. Spawn robot in Gazebo
4. Start controller_manager
5. Load and activate controllers
"""

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Package directories
    pkg_description = get_package_share_directory('quadruped_description')
    pkg_bringup = get_package_share_directory('quadruped_bringup')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Launch arguments
    use_rviz = LaunchConfiguration('use_rviz')
    world = LaunchConfiguration('world')

    # Robot description from xacro
    robot_description = Command([
        'xacro ',
        os.path.join(pkg_description, 'urdf', 'quadruped.urdf.xacro'),
        ' use_sim:=true',
        ' use_fake_hardware:=false',
    ])

    # Controller config
    controller_config = os.path.join(pkg_description, 'config', 'ros2_controllers.yaml')
    rviz_config = os.path.join(pkg_bringup, 'rviz', 'simulation.rviz')

    return LaunchDescription([
        # ==================== ARGUMENTS ====================
        DeclareLaunchArgument(
            'use_rviz',
            default_value='true',
            description='Launch RViz for visualization'
        ),
        DeclareLaunchArgument(
            'world',
            default_value='empty.sdf',
            description='Gazebo world file'
        ),

        # ==================== ROBOT STATE PUBLISHER ====================
        # Publishes TF from /joint_states (before Gazebo starts)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': True,
            }]
        ),

        # ==================== GAZEBO SIMULATOR ====================
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
            ]),
            launch_arguments={
                'gz_args': ['-r -v 4 ', world],
            }.items(),
        ),

        # ==================== SPAWN ROBOT ====================
        # Wait for Gazebo to start, then spawn
        TimerAction(
            period=3.0,
            actions=[
                Node(
                    package='ros_gz_sim',
                    executable='create',
                    output='screen',
                    arguments=[
                        '-name', 'quadruped',
                        '-topic', 'robot_description',
                        '-z', '0.4',  # Start above ground
                    ],
                    parameters=[{'use_sim_time': True}],
                ),
            ],
        ),

        # ==================== CONTROLLER MANAGER ====================
        # Spawned by gz_ros2_control automatically when robot is spawned

        # ==================== LOAD CONTROLLERS ====================
        # Wait for spawn, then load controllers
        TimerAction(
            period=5.0,
            actions=[
                # Joint State Broadcaster (must be first)
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
                    output='screen',
                    parameters=[{'use_sim_time': True}],
                ),
            ],
        ),

        TimerAction(
            period=6.0,
            actions=[
                # Leg Controller (effort-based)
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['leg_controller', '--controller-manager', '/controller_manager'],
                    output='screen',
                    parameters=[{'use_sim_time': True}],
                ),
            ],
        ),

        TimerAction(
            period=6.5,
            actions=[
                # IMU Broadcaster
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['imu_broadcaster', '--controller-manager', '/controller_manager'],
                    output='screen',
                    parameters=[{'use_sim_time': True}],
                ),
            ],
        ),

        # ==================== ROS-GZ BRIDGE ====================
        # Bridge clock and other topics
        TimerAction(
            period=4.0,
            actions=[
                Node(
                    package='ros_gz_bridge',
                    executable='parameter_bridge',
                    arguments=[
                        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                    ],
                    output='screen',
                ),
            ],
        ),

        # ==================== RVIZ ====================
        TimerAction(
            period=7.0,
            actions=[
                Node(
                    package='rviz2',
                    executable='rviz2',
                    name='rviz2',
                    output='screen',
                    arguments=['-d', rviz_config],
                    parameters=[{'use_sim_time': True}],
                    condition=IfCondition(use_rviz),
                ),
            ],
        ),
    ])
