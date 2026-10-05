#!/usr/bin/env python3

from launch import LaunchDescription #a list of nodes in the launch file are generated like generate interface for custom datatype
from launch_ros.actions import Node #tells where the listed node is
from launch.actions import TimerAction #timer - here its uded for delay but there are other actions

#| Action Class               | Purpose                                                  |
#| -------------------------- | -------------------------------------------------------- |
#| `Node`                     | Launch a ROS node with specified package and executable. |
#| `TimerAction`              | Run other actions after a delay or periodically.         |
#| `ExecuteProcess`           | Run an arbitrary executable or script.                   |
#| `RegisterEventHandler`     | Set up event-driven handlers (e.g., on process exit).    |
#| `Shutdown`                 | Request the launch system to shut down.                  |
#| `SetEnvironmentVariable`   | Set env vars for child processes.                        |
#| `LogInfo` / `LogError`     | Log messages during launch execution.                    |
#| `OpaqueFunction`           | Run arbitrary Python code during launch.                 |
#| `IncludeLaunchDescription` | Include another launch file into the current launch.     |


#
def generate_launch_description():
    # Node 1: Publisher - publishing two ints
    publisher_node = Node(
        package='cex_pkg',
        executable='pub_two_num.py',
        name='publisher',
        output='screen'
    )

    # Node 2: Service Server - add two ints
    service_server_node = Node(
        package='cex_pkg',
        executable='add_two_int.py',
        name='service_server',
        output='screen'
    )

    # Node 3: Subscriber Client (delayed start)
    SCN_action = Node(
                package='cex_pkg',
                executable='sub_client_add.py',
                name='subscriber_client',
                output='screen'
            )
    
    
    subscriber_client_node = TimerAction(
        period=3.0,  # Delay in seconds (adjust if needed)
        actions=[SCN_action]
    )
    

    return LaunchDescription([
        publisher_node,
        service_server_node,
        subscriber_client_node
    ])
