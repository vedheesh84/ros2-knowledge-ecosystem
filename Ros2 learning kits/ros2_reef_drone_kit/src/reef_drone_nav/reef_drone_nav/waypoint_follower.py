#!/usr/bin/env python3
"""
waypoint_follower.py - 3D Waypoint Navigation for AUV

3D WAYPOINT NAVIGATION:
=======================
Unlike ground robots that plan in 2D, AUVs navigate in full 3D space.

WAYPOINT STRUCTURE:
-------------------
Each waypoint specifies:
  - Position: (x, y, z) in world frame
  - Heading: yaw angle (optional)
  - Tolerance: how close is "reached"
  - Hold time: how long to stay

LINE-OF-SIGHT GUIDANCE:
=======================
Simple but effective approach:

1. Compute vector from current position to waypoint
2. Set desired heading toward waypoint
3. Set desired velocity proportional to distance
4. When within tolerance, switch to next waypoint

PURE PURSUIT (Alternative):
===========================
More sophisticated:
1. Find lookahead point on path
2. Compute arc to reach lookahead
3. Follow arc with curvature constraint

For this kit, we use simple line-of-sight.

Topics:
  Subscribe: /odom (nav_msgs/Odometry)
  Subscribe: /waypoints (geometry_msgs/PoseArray) - list of waypoints
  Publish: /station/setpoint (geometry_msgs/PoseStamped)
"""

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, PoseArray
from nav_msgs.msg import Odometry
import transforms3d


class WaypointFollower(Node):
    """Follows a sequence of 3D waypoints."""

    def __init__(self):
        super().__init__('waypoint_follower')

        # Parameters
        self.declare_parameter('position_tolerance', 0.5)  # m
        self.declare_parameter('heading_tolerance', 0.1)   # rad (~6°)
        self.declare_parameter('approach_velocity', 0.3)   # m/s
        self.declare_parameter('hold_time', 2.0)           # s

        self.position_tolerance = self.get_parameter('position_tolerance').value
        self.heading_tolerance = self.get_parameter('heading_tolerance').value
        self.approach_velocity = self.get_parameter('approach_velocity').value
        self.hold_time = self.get_parameter('hold_time').value

        # State
        self.waypoints = []
        self.current_waypoint_idx = 0
        self.current_position = np.zeros(3)
        self.current_heading = 0.0
        self.hold_start_time = None

        # Subscribers
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.waypoint_sub = self.create_subscription(
            PoseArray, '/waypoints', self.waypoints_callback, 10)

        # Publisher
        self.setpoint_pub = self.create_publisher(
            PoseStamped, '/station/setpoint', 10)

        # Navigation loop timer (10 Hz)
        self.timer = self.create_timer(0.1, self.navigation_loop)

        self.get_logger().info('Waypoint Follower started')

    def odom_callback(self, msg: Odometry):
        """Update current pose from odometry."""
        self.current_position = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z
        ])
        q = msg.pose.pose.orientation
        _, _, self.current_heading = transforms3d.euler.quat2euler(
            [q.w, q.x, q.y, q.z])

    def waypoints_callback(self, msg: PoseArray):
        """Receive new waypoint list."""
        self.waypoints = []
        for pose in msg.poses:
            wp = {
                'position': np.array([
                    pose.position.x,
                    pose.position.y,
                    pose.position.z
                ]),
                'heading': transforms3d.euler.quat2euler([
                    pose.orientation.w,
                    pose.orientation.x,
                    pose.orientation.y,
                    pose.orientation.z
                ])[2]
            }
            self.waypoints.append(wp)

        self.current_waypoint_idx = 0
        self.hold_start_time = None
        self.get_logger().info(f'Received {len(self.waypoints)} waypoints')

    def navigation_loop(self):
        """Main navigation logic."""
        if not self.waypoints:
            return

        if self.current_waypoint_idx >= len(self.waypoints):
            self.get_logger().info('All waypoints completed!')
            return

        # Get current target
        target = self.waypoints[self.current_waypoint_idx]
        target_pos = target['position']
        target_heading = target['heading']

        # Calculate distance to waypoint
        error = target_pos - self.current_position
        distance = np.linalg.norm(error)

        # Calculate heading error
        heading_error = self._wrap_angle(target_heading - self.current_heading)

        # Check if waypoint reached
        if distance < self.position_tolerance:
            if self.hold_start_time is None:
                self.hold_start_time = self.get_clock().now()
                self.get_logger().info(
                    f'Waypoint {self.current_waypoint_idx + 1} reached, holding...')

            # Check if hold time elapsed
            hold_elapsed = (self.get_clock().now() - self.hold_start_time).nanoseconds * 1e-9
            if hold_elapsed >= self.hold_time:
                self.current_waypoint_idx += 1
                self.hold_start_time = None
                self.get_logger().info(
                    f'Moving to waypoint {self.current_waypoint_idx + 1}')
        else:
            self.hold_start_time = None

        # Publish setpoint
        setpoint = PoseStamped()
        setpoint.header.stamp = self.get_clock().now().to_msg()
        setpoint.header.frame_id = 'odom'
        setpoint.pose.position.x = target_pos[0]
        setpoint.pose.position.y = target_pos[1]
        setpoint.pose.position.z = target_pos[2]

        # Convert heading to quaternion
        quat = transforms3d.euler.euler2quat(0, 0, target_heading)
        setpoint.pose.orientation.w = quat[0]
        setpoint.pose.orientation.x = quat[1]
        setpoint.pose.orientation.y = quat[2]
        setpoint.pose.orientation.z = quat[3]

        self.setpoint_pub.publish(setpoint)

    def _wrap_angle(self, angle: float) -> float:
        """Wrap angle to [-π, π]."""
        return np.arctan2(np.sin(angle), np.cos(angle))


def main(args=None):
    rclpy.init(args=args)
    node = WaypointFollower()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException, Exception):
        pass
    finally:
        try:
            node.destroy_node()
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
