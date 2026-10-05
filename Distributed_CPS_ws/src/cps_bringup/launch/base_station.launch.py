from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='cps_coordination',
            executable='base_coordinator_node',
            name='base_coordinator_node',
            output='screen',
            parameters=[{'mission_mode': 'AUTONOMOUS_COORDINATION'}]
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
            package='cps_telemetry',
            executable='prometheus_ros_exporter',
            name='prometheus_ros_exporter',
            output='screen'
        )
    ])
