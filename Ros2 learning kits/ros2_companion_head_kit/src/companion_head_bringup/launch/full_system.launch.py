import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_bringup = get_package_share_directory('companion_head_bringup')
    
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_bringup, 'launch', 'simulation.launch.py'))
    )
    
    face_detector_node = Node(
        package='companion_head_sensors',
        executable='face_detector',
        name='face_detector'
    )
    
    gaze_controller_node = Node(
        package='companion_head_control',
        executable='gaze_controller',
        name='gaze_controller'
    )
    
    mood_engine_node = Node(
        package='companion_head_behaviors',
        executable='mood_engine',
        name='mood_engine'
    )
    
    renderer_node = Node(
        package='companion_head_expression',
        executable='expression_renderer',
        name='expression_renderer'
    )

    return LaunchDescription([
        sim_launch,
        face_detector_node,
        gaze_controller_node,
        mood_engine_node,
        renderer_node
    ])
