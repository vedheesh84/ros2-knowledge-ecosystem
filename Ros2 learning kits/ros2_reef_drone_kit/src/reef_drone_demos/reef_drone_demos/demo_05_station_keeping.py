#!/usr/bin/env python3
"""
Demo 05: Station Keeping

LEARNING OBJECTIVES:
====================
1. Understand 3D position hold
2. See cascaded control (position → velocity → force)
3. Learn about disturbance rejection

WHAT THIS DEMO DOES:
====================
1. Commands the AUV to hold a fixed 3D position
2. Demonstrates position accuracy under perturbation
3. Shows combined depth + heading + position control

CASCADED CONTROL:
=================
Outer loop (Position):
  v_cmd = Kp_pos * (pos_desired - pos_current)

Inner loop (Velocity):
  F = Kp_vel * (v_cmd - v_current) + Ki_vel * integral

This provides:
- Velocity limiting for smooth motion
- Better disturbance rejection
- Easier tuning
"""

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
import transforms3d


class Demo05StationKeeping(Node):
    """Demo 05: Test 3D station keeping."""

    def __init__(self):
        super().__init__('demo_05_station_keeping')

        self.setpoint_pub = self.create_publisher(
            PoseStamped, '/station/setpoint', 10)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)

        self.current_pos = np.zeros(3)

        self.get_logger().info('=== Demo 05: Station Keeping ===')
        self.get_logger().info('')
        self.get_logger().info('This demo commands the AUV to hold fixed 3D positions.')
        self.get_logger().info('Watch position accuracy and disturbance rejection.')
        self.get_logger().info('')

        # Demo positions [x, y, z, heading]
        self.positions = [
            [0.0, 0.0, -5.0, 0.0],       # Start position
            [5.0, 0.0, -5.0, 0.0],       # Move forward
            [5.0, 5.0, -5.0, np.pi/2],   # Move right, face east
            [5.0, 5.0, -10.0, np.pi/2],  # Dive deeper
            [0.0, 0.0, -5.0, 0.0],       # Return home
        ]

        self.timer = self.create_timer(1.0, self.demo_loop)
        self.demo_step = 0
        self.step_start_time = self.get_clock().now()
        self.step_duration = 20.0

    def odom_callback(self, msg: Odometry):
        self.current_pos = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z
        ])

    def demo_loop(self):
        elapsed = (self.get_clock().now() - self.step_start_time).nanoseconds * 1e-9

        if self.demo_step >= len(self.positions):
            self.get_logger().info('Demo complete!')
            self.timer.cancel()
            return

        target = self.positions[self.demo_step]

        # Publish setpoint
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.pose.position.x = target[0]
        msg.pose.position.y = target[1]
        msg.pose.position.z = target[2]
        quat = transforms3d.euler.euler2quat(0, 0, target[3])
        msg.pose.orientation.w = quat[0]
        msg.pose.orientation.x = quat[1]
        msg.pose.orientation.y = quat[2]
        msg.pose.orientation.z = quat[3]
        self.setpoint_pub.publish(msg)

        # Calculate position error
        error = np.linalg.norm(self.current_pos - np.array(target[:3]))
        self.get_logger().info(
            f'Target: [{target[0]:.1f}, {target[1]:.1f}, {target[2]:.1f}] | '
            f'Current: [{self.current_pos[0]:.1f}, {self.current_pos[1]:.1f}, {self.current_pos[2]:.1f}] | '
            f'Error: {error:.2f}m')

        if elapsed >= self.step_duration:
            self.demo_step += 1
            self.step_start_time = self.get_clock().now()
            if self.demo_step < len(self.positions):
                t = self.positions[self.demo_step]
                self.get_logger().info(
                    f'\n>>> New target: [{t[0]:.1f}, {t[1]:.1f}, {t[2]:.1f}]')


def main(args=None):
    rclpy.init(args=args)
    node = Demo05StationKeeping()
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
