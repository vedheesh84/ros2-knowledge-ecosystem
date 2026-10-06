import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_desc = get_package_share_directory('arm_description')
    default_model_path = os.path.join(pkg_desc, 'urdf', 'arm.urdf.xacro')
    default_rviz_config = os.path.join(pkg_desc, 'config', 'arm.rviz')

    use_rviz = LaunchConfiguration('use_rviz')
    serial_port = LaunchConfiguration('serial_port')
    baud_rate = LaunchConfiguration('baud_rate')

    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': ParameterValue(
                Command(['xacro ', LaunchConfiguration('model')]),
                value_type=str
            )
        }]
    )

    hardware_bridge_node = Node(
        package='arm_hardware',
        executable='servo_bridge.py',
        name='servo_hardware_bridge',
        parameters=[{
            'serial_port': serial_port,
            'baud_rate': baud_rate,
        }]
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
        arguments=['-d', LaunchConfiguration('rvizconfig')],
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        DeclareLaunchArgument('model', default_value=default_model_path),
        DeclareLaunchArgument('rvizconfig', default_value=default_rviz_config),
        DeclareLaunchArgument('use_rviz', default_value='true', description='Launch RViz for visualization'),
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0', description='Microcontroller serial port'),
        DeclareLaunchArgument('baud_rate', default_value='115200', description='Baud rate for hardware serial'),
        rsp_node,
        hardware_bridge_node,
        kinematics_node,
        gripper_node,
        rviz_node
    ])
