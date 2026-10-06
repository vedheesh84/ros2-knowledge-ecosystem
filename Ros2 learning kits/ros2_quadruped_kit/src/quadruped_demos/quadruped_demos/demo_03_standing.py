#!/usr/bin/env python3
"""
Demo 03: Standing

LEARNING OBJECTIVES:
- Static balance (all feet in contact)
- Center of mass positioning
- PD control for posture

This demo shows the robot maintaining a standing posture.
The robot should stay balanced without walking.
"""

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, String
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist


class StandingDemo(Node):
    """Demonstrates static standing with balance control."""

    def __init__(self):
        super().__init__('demo_03_standing')

        # Publish behavior command
        self.behavior_pub = self.create_publisher(String, '/behavior/command', 10)

        # Publish zero velocity
        self.vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Subscribe to IMU for feedback
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)

        self.roll = 0.0
        self.pitch = 0.0

        # Send stand command
        self.create_timer(0.1, self.demo_loop)
        self.started = False

        self.get_logger().info('Demo 03: Standing started')

    def imu_callback(self, msg: Imu):
        q = msg.orientation
        sinr = 2 * (q.w * q.x + q.y * q.z)
        cosr = 1 - 2 * (q.x * q.x + q.y * q.y)
        self.roll = np.arctan2(sinr, cosr)

        sinp = 2 * (q.w * q.y - q.z * q.x)
        self.pitch = np.arcsin(np.clip(sinp, -1, 1))

    def demo_loop(self):
        # Send stand command
        cmd = String()
        cmd.data = 'stand'
        self.behavior_pub.publish(cmd)

        # Publish zero velocity
        vel = Twist()
        self.vel_pub.publish(vel)

        # Log balance status
        if not self.started:
            self.get_logger().info('Robot should now be standing')
            self.get_logger().info('Watch the roll/pitch to verify balance')
            self.started = True

        self.get_logger().info(
            f'Balance: roll={np.degrees(self.roll):.1f} deg, pitch={np.degrees(self.pitch):.1f} deg',
            throttle_duration_sec=1.0
        )


def main(args=None):
    rclpy.init(args=args)
    node = StandingDemo()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
