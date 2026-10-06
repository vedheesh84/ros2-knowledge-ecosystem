from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    """
    Master Evolution Selector Launch Recipe:
    Allows user to switch between V1, V2-V3, V4-V5, and V6 via launch argument 'version:=v1|v2_v3|v4_v5|v6'.
    Launches complete sensory and motion control stacks for each generation.
    """
    version_arg = DeclareLaunchArgument(
        'version',
        default_value='v2_v3',
        description='Evolutionary Generation: v1 (reactive), v2_v3 (stabilized), v4_v5 (topological), or v6 (exploratory)'
    )
    
    # 1. Generation 1 (V1 Reactive Tracker)
    launch_v1 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('line_follower_v1_reactive'), 'launch', 'v1_reactive_simulation.launch.py'])
        ),
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('version'), "' == 'v1'"]))
    )
    
    # 2. Generation 2 (V2-V3 Stabilized Physical Dynamics)
    launch_v2_v3 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('line_follower_v2_v3_stabilized'), 'launch', 'v2_v3_stabilized_simulation.launch.py'])
        ),
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('version'), "' == 'v2_v3'"]))
    )
    
    # 3. Generation 3 (V4-V5 Symbolic Topological Navigation)
    launch_v4_v5 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('line_follower_v4_v5_topological'), 'launch', 'v4_v5_topological_simulation.launch.py'])
        ),
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('version'), "' == 'v4_v5'"]))
    )
    
    # 4. Generation 4 (V6 Unconstrained Spatial SLAM & Exploration)
    launch_v6 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('line_follower_v6_exploratory'), 'launch', 'v6_exploratory_simulation.launch.py'])
        ),
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('version'), "' == 'v6'"]))
    )
    
    return LaunchDescription([
        version_arg,
        launch_v1,
        launch_v2_v3,
        launch_v4_v5,
        launch_v6
    ])
