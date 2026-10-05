from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os

def generate_launch_description():
    # Paths
    pkg_share = os.path.join(
        os.getenv("COLCON_PREFIX_PATH").split(":")[0], "share", "mobilerobot"
    )
    params_file = os.path.join(pkg_share, "config", "nav2_params.yaml")
    rviz_config_file = os.path.join(
        "/opt/ros/humble/share/nav2_bringup/rviz", "nav2_default_view.rviz"
    )
    map_file = os.path.join(pkg_share, "map", "map.yaml")

    # Launch arguments
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    return LaunchDescription([
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation (Gazebo) clock if true"
        ),

        # Map server
        Node(
            package="nav2_map_server",
            executable="map_server",
            name="map_server",
            output="screen",
            parameters=[{"use_sim_time": use_sim_time},
                        {"yaml_filename": map_file}]
        ),

        # AMCL for localization
        Node(
            package="nav2_amcl",
            executable="amcl",
            name="amcl",
            output="screen",
            parameters=[params_file, {"use_sim_time": use_sim_time}]
        ),

        # Planner server
        Node(
            package="nav2_planner",
            executable="planner_server",
            name="planner_server",
            output="screen",
            parameters=[params_file, {"use_sim_time": use_sim_time}]
        ),

        # Controller server
        Node(
            package="nav2_controller",
            executable="controller_server",
            name="controller_server",
            output="screen",
            parameters=[params_file, {"use_sim_time": use_sim_time}]
        ),

        # Behavior Tree Navigator
        Node(
            package="nav2_bt_navigator",
            executable="bt_navigator",
            name="bt_navigator",
            output="screen",
            parameters=[params_file, {"use_sim_time": use_sim_time}]
        ),

        # Waypoint follower
        Node(
            package="nav2_waypoint_follower",
            executable="waypoint_follower",
            name="waypoint_follower",
            output="screen",
            parameters=[params_file, {"use_sim_time": use_sim_time}]
        ),

        # Lifecycle manager
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_navigation",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                "autostart": True,
                "node_names": [
                    "controller_server",
                    "planner_server",
                    "bt_navigator",
                    "waypoint_follower",
                    "map_server",
                    "amcl"
                ]
            }]
        ),

        # Robot state publisher (you need to provide your URDF or xacro)
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"use_sim_time": use_sim_time}],
            arguments=[os.path.join(pkg_share, "urdf", "mobilerobot.urdf")]
        ),

        # RViz2
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            output="screen",
            arguments=["-d", rviz_config_file]
        ),
    ])
