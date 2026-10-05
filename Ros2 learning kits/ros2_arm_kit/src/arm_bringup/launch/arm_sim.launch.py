import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_desc = get_package_share_directory('arm_description')
    default_model_path = os.path.join(pkg_desc, 'urdf', 'arm.urdf.xacro')
    default_rviz_config = os.path.join(pkg_desc, 'config', 'arm.rviz')

    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}]
    )

    mock_hw_node = Node(
        package='arm_hardware',
        executable='mock_hardware_node.py',
        name='mock_arm_hardware'
    )

    kinematics_node = Node(
        package='arm_kinematics',
        executable='kinematics_service_node',
        name='arm_kinematics'
    )

    gripper_node = Node(
        package='arm_manipulation',
        executable='gripper_action_server',
        name='gripper_controller'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rvizconfig')]
    )

    return LaunchDescription([
        DeclareLaunchArgument('model', default_value=default_model_path),
        DeclareLaunchArgument('rvizconfig', default_value=default_rviz_config),
        rsp_node,
        mock_hw_node,
        kinematics_node,
        gripper_node,
        rviz_node
    ])
