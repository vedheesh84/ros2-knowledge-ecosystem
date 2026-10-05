from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_rviz = LaunchConfiguration("use_rviz")
    model_path = PathJoinSubstitution(
        [FindPackageShare("spider_pkg"), "urdf", "spider.urdf.xacro"]
    )
    rviz_config = PathJoinSubstitution(
        [FindPackageShare("spider_pkg"), "rviz", "spider.rviz"]
    )

    robot_description = {
        "robot_description": ParameterValue(
            Command(["xacro ", model_path]), value_type=str
        )
    }

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_rviz",
                default_value="true",
                description="Start RViz with the spider display config.",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[robot_description],
                output="screen",
            ),
            Node(
                package="spider_pkg",
                executable="spider_gait_node",
                parameters=[
                    {
                        "speed_hz": 0.9,
                        "hip_swing": 0.28,
                        "femur_lift": 0.45,
                        "tibia_lift": 0.55,
                    }
                ],
                output="screen",
            ),
            Node(
                condition=IfCondition(use_rviz),
                package="rviz2",
                executable="rviz2",
                arguments=["-d", rviz_config],
                output="screen",
            ),
        ]
    )
