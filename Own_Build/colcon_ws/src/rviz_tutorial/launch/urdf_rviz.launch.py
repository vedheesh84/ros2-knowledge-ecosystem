#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

def generate_launch_description():

	use_sim_time = LaunchConfiguration('use_sim_time', default='true')

	urdf_file = os.path.join(get_package_share_directory('rviz_tutorial'), 'urdf', 'myfirst.urdf')
	
	with open(urdf_file, 'r') as infp:
		robot_description = infp.read()


	

	robot_state_publisher_node = Node(
		package='robot_state_publisher',
		executable='robot_state_publisher',
		output='screen',
		parameters=[{'use_sim_time': use_sim_time,'robot_description': robot_description}],
		arguments=[urdf_file]
	)

	rviz_node = Node(
		package='rviz2',
		executable='rviz2',
		name='rviz2',
		output='screen'
	)

	return LaunchDescription([
		 DeclareLaunchArgument('use_sim_time',default_value='false',description='Use simulation (Gazebo) clock if true'),
		#joint_state_publisher_node,
		robot_state_publisher_node,
		rviz_node
	])
