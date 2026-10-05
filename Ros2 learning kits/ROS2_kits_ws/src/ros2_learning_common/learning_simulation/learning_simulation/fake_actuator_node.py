#!/usr/bin/env python3
"""
Fake Actuator Node - Simulating Robot Motion
=============================================

LEARNING OBJECTIVES:
--------------------
1. How to simulate actuator behavior
2. Converting commands to state feedback
3. The same code works in simulation and real hardware!

This node simulates a differential drive robot:
- Subscribes to /cmd_vel (velocity commands)
- Publishes to /odom (simulated odometry)

The key insight: Your control code doesn't change between sim and real!
Only the actuator node changes.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math


class FakeActuatorNode(Node):
    """Simulates a differential drive robot."""

    def __init__(self):
        super().__init__('fake_actuator')
        self.get_logger().info('Fake Actuator Node starting...')

        # State
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_cmd = Twist()
        self.last_time = self.get_clock().now()

        # Subscribe to velocity commands
        self.cmd_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_callback, 10
        )

        # Publish odometry
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)

        # Update at 20 Hz
        self.timer = self.create_timer(0.05, self.update)

        self.get_logger().info('Listening on /cmd_vel, publishing to /odom')
        self.get_logger().info('Send commands: ros2 topic pub /cmd_vel geometry_msgs/Twist ...')

    def cmd_callback(self, msg):
        """Store the latest command."""
        self.last_cmd = msg

    def update(self):
        """Update simulated position based on commands."""
        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        # Simple integration
        vx = self.last_cmd.linear.x
        wz = self.last_cmd.angular.z

        self.theta += wz * dt
        self.x += vx * math.cos(self.theta) * dt
        self.y += vx * math.sin(self.theta) * dt

        # Publish odometry
        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = math.sin(self.theta / 2)
        odom.pose.pose.orientation.w = math.cos(self.theta / 2)
        odom.twist.twist.linear.x = vx
        odom.twist.twist.angular.z = wz

        self.odom_pub.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = FakeActuatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
