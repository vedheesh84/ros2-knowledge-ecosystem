from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    robot_name_arg = DeclareLaunchArgument('robot_name', default_value='robot1', description='Name and namespace of explorer robot')
    peer_name_arg = DeclareLaunchArgument('peer_name', default_value='robot2', description='Name of peer robot for collision avoidance')
    
    return LaunchDescription([
        robot_name_arg,
        peer_name_arg,
        Node(
            package='cps_coordination',
            executable='cbba_auction_node',
            name='cbba_auction_node',
            namespace=LaunchConfiguration('robot_name'),
            parameters=[{'robot_id': LaunchConfiguration('robot_name')}],
            output='screen'
        ),
        Node(
            package='cps_coordination',
            executable='peer_collision_avoidance',
            name='peer_collision_avoidance',
            namespace=LaunchConfiguration('robot_name'),
            parameters=[{
                'robot_id': LaunchConfiguration('robot_name'),
                'peer_id': LaunchConfiguration('peer_name'),
                'safety_distance_m': 0.8
            }],
            output='screen'
        )
    ])
