import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.parameter_descriptions import ParameterValue

def create_drone_group(drone_id, init_x, init_y, init_z, model_path):
    robot_desc = ParameterValue(Command(['xacro ', model_path]), value_type=str)
    return GroupAction([
        PushRosNamespace(drone_id),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{
                'robot_description': robot_desc,
                'frame_prefix': f'{drone_id}/'
            }]
        ),
        Node(
            package='swarm_control',
            executable='flight_controller_node',
            name='flight_controller',
            parameters=[{
                'drone_id': drone_id,
                'initial_x': init_x,
                'initial_y': init_y,
                'initial_z': init_z
            }]
        )
    ])

def generate_launch_description():
    pkg_desc = get_package_share_directory('drone_description')
    pkg_bringup = get_package_share_directory('drone_bringup')
    default_model = os.path.join(pkg_desc, 'urdf', 'drone.urdf.xacro')
    default_rviz = os.path.join(pkg_bringup, 'config', 'swarm.rviz')

    use_rviz = LaunchConfiguration('use_rviz')

    drone_0 = create_drone_group('drone_0', 0.0, 0.0, 0.0, default_model)
    drone_1 = create_drone_group('drone_1', -1.0, 1.0, 0.0, default_model)
    drone_2 = create_drone_group('drone_2', -1.0, -1.0, 0.0, default_model)

    formation_mgr = Node(
        package='swarm_formation',
        executable='formation_manager_node',
        name='formation_manager'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', default_rviz] if os.path.exists(default_rviz) else [],
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_rviz', default_value='false', description='Whether to launch RViz2'),
        drone_0,
        drone_1,
        drone_2,
        formation_mgr,
        rviz_node
    ])
