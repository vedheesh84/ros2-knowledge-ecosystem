from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    serial_port = LaunchConfiguration('serial_port')
    baud_rate = LaunchConfiguration('baud_rate')
    drone_id = LaunchConfiguration('drone_id')

    bridge_node = Node(
        package='drone_hardware',
        executable='flight_controller_bridge',
        name='flight_controller_bridge',
        parameters=[{
            'serial_port': serial_port,
            'baud_rate': baud_rate,
            'drone_id': drone_id,
        }]
    )

    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyACM0', description='Serial port path'),
        DeclareLaunchArgument('baud_rate', default_value='115200', description='Baud rate'),
        DeclareLaunchArgument('drone_id', default_value='drone_0', description='Drone identifier'),
        bridge_node
    ])
