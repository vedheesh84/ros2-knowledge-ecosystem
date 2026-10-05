from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    """
    Full Multi-Robot CPS Digital Twin Launch Recipe:
    Orchestrates Base Coordinator, Map Merger, Robot 1 (Explorer), and Robot 2 (Manipulator).
    """
    return LaunchDescription([
        Node(
            package='cps_coordination',
            executable='base_coordinator_node',
            name='base_coordinator_node',
            output='screen'
        ),
        Node(
            package='cps_coordination',
            executable='map_merger_node',
            name='map_merger_node',
            output='screen'
        ),
        Node(
            package='cps_coordination',
            executable='health_watchdog_node',
            name='health_watchdog_node',
            output='screen'
        ),
        Node(
            package='cps_coordination',
            executable='cbba_auction_node',
            name='cbba_auction_node_robot1',
            namespace='robot1',
            parameters=[{'robot_id': 'robot1'}],
            output='screen'
        ),
        Node(
            package='cps_coordination',
            executable='cbba_auction_node',
            name='cbba_auction_node_robot2',
            namespace='robot2',
            parameters=[{'robot_id': 'robot2'}],
            output='screen'
        ),
        Node(
            package='cps_telemetry',
            executable='topic_delay_monitor',
            name='topic_delay_monitor',
            output='screen'
        )
    ])
