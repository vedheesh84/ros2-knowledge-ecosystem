#!/usr/bin/env python3
"""
Demo 06: Waypoint Navigation

LEARNING OBJECTIVES:
====================
1. Understand 3D waypoint following
2. See line-of-sight guidance
3. Learn waypoint sequencing

WHAT THIS DEMO DOES:
====================
1. Sends a sequence of 3D waypoints
2. AUV navigates through each waypoint
3. Demonstrates autonomous point-to-point motion

NAVIGATION STRATEGY:
====================
Line-of-Sight Guidance:
1. Vector from current position to waypoint
2. Heading command toward waypoint
3. Velocity command proportional to distance
4. Switch to next waypoint when within tolerance
"""

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Pose
from nav_msgs.msg import Odometry
import transforms3d


class Demo06WaypointNav(Node):
    """Demo 06: Test waypoint navigation."""

    def __init__(self):
        super().__init__('demo_06_waypoint_nav')

        self.waypoint_pub = self.create_publisher(
            PoseArray, '/waypoints', 10)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)

        self.current_pos = np.zeros(3)

        self.get_logger().info('=== Demo 06: Waypoint Navigation ===')
        self.get_logger().info('')
        self.get_logger().info('This demo sends a sequence of waypoints for the AUV')
        self.get_logger().info('to follow autonomously.')
        self.get_logger().info('')

        # Square pattern at -10m depth
        self.waypoints = [
            [0.0, 0.0, -10.0, 0.0],
            [10.0, 0.0, -10.0, 0.0],
            [10.0, 10.0, -10.0, np.pi/2],
            [0.0, 10.0, -10.0, np.pi],
            [0.0, 0.0, -10.0, -np.pi/2],
        ]

        # Publish waypoints
        self.timer = self.create_timer(2.0, self.publish_waypoints)
        self.status_timer = self.create_timer(1.0, self.print_status)

    def odom_callback(self, msg: Odometry):
        self.current_pos = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z
        ])

    def publish_waypoints(self):
        """Publish waypoint list."""
        msg = PoseArray()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'

        for wp in self.waypoints:
            pose = Pose()
            pose.position.x = wp[0]
            pose.position.y = wp[1]
            pose.position.z = wp[2]
            quat = transforms3d.euler.euler2quat(0, 0, wp[3])
            pose.orientation.w = quat[0]
            pose.orientation.x = quat[1]
            pose.orientation.y = quat[2]
            pose.orientation.z = quat[3]
            msg.poses.append(pose)

        self.waypoint_pub.publish(msg)

    def print_status(self):
        """Print navigation status."""
        self.get_logger().info(
            f'Position: [{self.current_pos[0]:.1f}, {self.current_pos[1]:.1f}, '
            f'{self.current_pos[2]:.1f}]')


def main(args=None):
    rclpy.init(args=args)
    node = Demo06WaypointNav()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
