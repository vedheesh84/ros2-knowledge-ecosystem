from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackagePrefix, FindPackageShare


def generate_launch_description():
    gui = LaunchConfiguration("gui")
    use_rviz = LaunchConfiguration("use_rviz")
    world = LaunchConfiguration("world")

    pkg_share = FindPackageShare("spider_pkg")
    model_path = PathJoinSubstitution([pkg_share, "urdf", "spider.urdf.xacro"])
    default_world = PathJoinSubstitution([pkg_share, "worlds", "spider_map.world"])
    rviz_config = PathJoinSubstitution([pkg_share, "rviz", "spider_mapping.rviz"])
    slam_params = PathJoinSubstitution([pkg_share, "config", "slam_toolbox.yaml"])
    gazebo_launch = PathJoinSubstitution(
        [FindPackageShare("gazebo_ros"), "launch", "gazebo.launch.py"]
    )
    slam_launch = PathJoinSubstitution(
        [FindPackageShare("slam_toolbox"), "launch", "online_async_launch.py"]
    )
    spider_plugin_path = PathJoinSubstitution([FindPackagePrefix("spider_pkg"), "lib"])

    robot_description = {
        "robot_description": ParameterValue(
            Command(["xacro ", model_path, " include_lidar:=true"]),
            value_type=str,
        )
    }

    return LaunchDescription(
        [
            DeclareLaunchArgument("gui", default_value="true"),
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("world", default_value=default_world),
            SetEnvironmentVariable(
                name="GAZEBO_PLUGIN_PATH",
                value=[
                    spider_plugin_path,
                    ":",
                    EnvironmentVariable("GAZEBO_PLUGIN_PATH", default_value=""),
                ],
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(gazebo_launch),
                launch_arguments={"gui": gui, "world": world}.items(),
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="spider_state_publisher",
                parameters=[robot_description, {"use_sim_time": True}],
                output="screen",
            ),
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=[
                    "-topic", "robot_description",
                    "-entity", "spider",
                    "-x", "0.0", "-y", "0.0", "-z", "0.04",
                ],
                output="screen",
            ),
            Node(
                package="spider_pkg",
                executable="spider_gait_node",
                name="spider_gait_node",
                parameters=[
                    {
                        "use_sim_time": True,
                        "speed_hz": 0.9,
                        "hip_swing": 0.30,
                        "femur_lift": 0.25,
                        "tibia_lift": 0.28,
                        "motion_timeout": 0.6,
                    }
                ],
                output="screen",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(slam_launch),
                launch_arguments={
                    "use_sim_time": "true",
                    "slam_params_file": slam_params,
                }.items(),
            ),
            Node(
                condition=IfCondition(use_rviz),
                package="rviz2",
                executable="rviz2",
                arguments=["-d", rviz_config],
                parameters=[{"use_sim_time": True}],
                output="screen",
            ),
        ]
    )
