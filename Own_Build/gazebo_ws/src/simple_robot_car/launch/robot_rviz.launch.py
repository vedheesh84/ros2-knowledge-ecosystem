import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_simple = get_package_share_directory('simple_robot_car')
    urdf_file = os.path.join(pkg_simple, 'urdf', 'simple_robot_car.urdf')

    return LaunchDescription([
        # Publish robot_description FIRST
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_file).read()}]
        ),

        # Then launch RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen'
            # optional: arguments=['-d', 'path/to/display.rviz']
        ),
    ])
