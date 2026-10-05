from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace

def generate_launch_description():
    robot_name_arg = DeclareLaunchArgument('robot_name', default_value='robot1')
    
    return LaunchDescription([
        robot_name_arg,
        Node(
            package='cps_coordination',
            executable='cbba_auction_node',
            name='cbba_auction_node',
            namespace=LaunchConfiguration('robot_name'),
            parameters=[{'robot_id': 'robot1'}],
            output='screen'
        ),
        Node(
            package='cps_coordination',
            executable='peer_collision_avoidance',
            name='peer_collision_avoidance',
            namespace=LaunchConfiguration('robot_name'),
            parameters=[{'robot_id': 'robot1', 'peer_id': 'robot2'}],
            output='screen'
        )
    ])
