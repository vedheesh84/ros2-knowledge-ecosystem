#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
	urdf_file = os.path.join(
		get_package_share_directory('rviz_tutorial'), 'urdf', 'full_demo.urdf'
	)
	with open(urdf_file, 'r') as infp:
		robot_description = infp.read()

	joint_state_publisher_node = Node(
		package='joint_state_publisher_gui',
		executable='joint_state_publisher_gui',
		name='joint_state_publisher_gui',
		output='screen'
	)			

	robot_state_publisher_node = Node(
		package='robot_state_publisher',
		executable='robot_state_publisher',
		output='screen',
		parameters=[{'robot_description': robot_description}]
	)

	rviz_node = Node(
		package='rviz2',
		executable='rviz2',
		name='rviz2',
		output='screen'
	)

	return LaunchDescription([
		joint_state_publisher_node,
		robot_state_publisher_node,
		rviz_node
	])
