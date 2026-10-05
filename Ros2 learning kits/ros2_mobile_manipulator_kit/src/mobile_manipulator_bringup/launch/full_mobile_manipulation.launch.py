import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_bringup = get_package_share_directory('mobile_manipulator_bringup')
    pkg_arm = get_package_share_directory('mobile_manipulator_arm_control')
    pkg_perception = get_package_share_directory('mobile_manipulator_perception')
    pkg_manipulation = get_package_share_directory('mobile_manipulator_manipulation')

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_bringup, 'launch', 'simulation.launch.py'))
    )

    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_arm, 'launch', 'moveit.launch.py'))
    )

    perception_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_perception, 'launch', 'perception.launch.py'))
    )

    manipulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_manipulation, 'launch', 'manipulation.launch.py'))
    )

    return LaunchDescription([
        sim_launch,
        moveit_launch,
        perception_launch,
        manipulation_launch
    ])
