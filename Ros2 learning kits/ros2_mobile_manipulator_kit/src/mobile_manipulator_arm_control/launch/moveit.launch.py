#!/usr/bin/env python3
"""
MoveIt2 Launch File
===================

LEARNING OBJECTIVES:
- Understand MoveIt2 node architecture
- See move_group configuration
- Learn planning scene setup
- Practice MoveIt parameters

WHAT THIS LAUNCH DOES:
1. Loads robot description (URDF) and SRDF
2. Starts move_group node (MoveIt brain)
3. Configures planning pipeline
4. Sets up controller integration

PREREQUISITES:
- robot_state_publisher running
- Controllers spawned and active
- Joint states being published

USAGE:
  # After bringup (hardware or simulation)
  ros2 launch mobile_manipulator_arm_control moveit.launch.py
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
import yaml


def load_yaml(package_name: str, file_name: str):
    """Load YAML file from package share directory."""
    package_path = get_package_share_directory(package_name)
    file_path = os.path.join(package_path, file_name)
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def generate_launch_description():
    # ========================================
    # PACKAGE DIRECTORIES
    # ========================================
    pkg_description = get_package_share_directory('mobile_manipulator_description')
    pkg_arm_control = get_package_share_directory('mobile_manipulator_arm_control')

    # ========================================
    # FILE PATHS
    # ========================================
    urdf_file = os.path.join(pkg_description, 'urdf', 'mobile_manipulator.urdf.xacro')
    srdf_file = os.path.join(pkg_arm_control, 'config', 'mobile_manipulator.srdf')

    # ========================================
    # LAUNCH CONFIGURATIONS
    # ========================================
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')

    # ========================================
    # ROBOT DESCRIPTION
    # ========================================
    # Process URDF with xacro
    robot_description = Command(['xacro ', urdf_file, ' sim_mode:=true'])

    # Load SRDF
    with open(srdf_file, 'r') as f:
        robot_description_semantic = f.read()

    # ========================================
    # MOVEIT CONFIGURATION
    # ========================================
    # Kinematics
    kinematics_yaml = load_yaml(
        'mobile_manipulator_arm_control', 'config/kinematics.yaml'
    )

    # Joint limits
    joint_limits_yaml = load_yaml(
        'mobile_manipulator_arm_control', 'config/joint_limits.yaml'
    )

    # Controllers
    moveit_controllers_yaml = load_yaml(
        'mobile_manipulator_arm_control', 'config/moveit_controllers.yaml'
    )

    # Planning pipeline (OMPL)
    planning_pipeline_config = {
        'default_planning_pipeline': 'ompl',
        'planning_pipelines': ['ompl'],
        'ompl': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters': 'default_planner_request_adapters/AddTimeOptimalParameterization '
                               'default_planner_request_adapters/ResolveConstraintFrames '
                               'default_planner_request_adapters/FixWorkspaceBounds '
                               'default_planner_request_adapters/FixStartStateBounds '
                               'default_planner_request_adapters/FixStartStateCollision '
                               'default_planner_request_adapters/FixStartStatePathConstraints',
            'start_state_max_bounds_error': 0.1,
        }
    }

    # Trajectory execution
    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01,
    }

    # Planning scene
    planning_scene_monitor_parameters = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True,
    }

    # ========================================
    # MOVE_GROUP PARAMETERS
    # ========================================
    move_group_params = {
        'robot_description': robot_description,
        'robot_description_semantic': robot_description_semantic,
        'robot_description_kinematics': kinematics_yaml,
        'robot_description_planning': joint_limits_yaml,
        'use_sim_time': use_sim_time,
    }
    move_group_params.update(planning_pipeline_config)
    move_group_params.update(trajectory_execution)
    move_group_params.update(planning_scene_monitor_parameters)
    move_group_params.update(moveit_controllers_yaml)

    return LaunchDescription([
        # ========================================
        # LAUNCH ARGUMENTS
        # ========================================
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock'
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='false',
            description='Launch RViz with MoveIt plugin'
        ),

        # ========================================
        # MOVE_GROUP NODE
        # ========================================
        # The "brain" of MoveIt - handles planning and execution
        Node(
            package='moveit_ros_move_group',
            executable='move_group',
            name='move_group',
            output='screen',
            parameters=[move_group_params],
        ),

        # ========================================
        # RVIZ (optional)
        # ========================================
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            condition=IfCondition(use_rviz),
        ),
    ])
