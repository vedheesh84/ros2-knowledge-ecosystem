from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node

def generate_launch_description():
    """
    Master Evolution Selector Launch Recipe:
    Allows user to switch between V1, V2-V3, V4-V5, and V6 via launch argument 'version:=v1|v2_v3|v4_v5|v6'.
    """
    version_arg = DeclareLaunchArgument('version', default_value='v2_v3')
    
    return LaunchDescription([
        version_arg,
        Node(
            package='line_follower_v1_reactive',
            executable='reactive_threshold_node',
            condition=IfCondition(PythonExpression(["'", LaunchConfiguration('version'), "' == 'v1'"])),
            output='screen'
        ),
        Node(
            package='line_follower_v2_v3_stabilized',
            executable='stabilized_motion_controller',
            condition=IfCondition(PythonExpression(["'", LaunchConfiguration('version'), "' == 'v2_v3'"])),
            output='screen'
        ),
        Node(
            package='line_follower_v4_v5_topological',
            executable='topological_navigator_node',
            condition=IfCondition(PythonExpression(["'", LaunchConfiguration('version'), "' == 'v4_v5'"])),
            output='screen'
        ),
        Node(
            package='line_follower_v6_exploratory',
            executable='frontier_explorer_node',
            condition=IfCondition(PythonExpression(["'", LaunchConfiguration('version'), "' == 'v6'"])),
            output='screen'
        )
    ])
