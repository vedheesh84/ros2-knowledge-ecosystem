import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_desc = get_package_share_directory('drone_description')
    default_model = os.path.join(pkg_desc, 'urdf', 'drone.urdf.xacro')
    default_rviz = os.path.join(pkg_desc, 'config', 'drone.rviz')

    use_rviz = LaunchConfiguration('use_rviz')
    use_jsp_gui = LaunchConfiguration('use_jsp_gui')
    model = LaunchConfiguration('model')

    robot_desc = ParameterValue(Command(['xacro ', model]), value_type=str)

    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc}]
    )

    jsp_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        condition=IfCondition(use_jsp_gui)
    )

    jsp_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        condition=UnlessCondition(use_jsp_gui)
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', default_rviz] if os.path.exists(default_rviz) else [],
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        DeclareLaunchArgument('model', default_value=default_model, description='Path to robot xacro'),
        DeclareLaunchArgument('use_rviz', default_value='false', description='Whether to launch RViz2'),
        DeclareLaunchArgument('use_jsp_gui', default_value='false', description='Whether to launch joint_state_publisher GUI'),
        rsp_node,
        jsp_gui_node,
        jsp_node,
        rviz_node
    ])
