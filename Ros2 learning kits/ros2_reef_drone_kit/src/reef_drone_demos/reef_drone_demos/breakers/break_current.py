#!/usr/bin/env python3
"""
break_current.py - Ocean Current Disturbance Injection

LEARNING OBJECTIVES:
====================
1. Understand external disturbance effects
2. See control system response to currents
3. Learn disturbance rejection limits

WHAT THIS BREAKER DOES:
=======================
Simulates ocean currents by applying external force:
  - constant: Steady current in one direction
  - oscillating: Tide-like oscillating current
  - random: Turbulent current variations

CURRENT EFFECTS:
================
Ocean currents affect:
  - Station keeping: Must actively counter current
  - Navigation: Actual vs ground track differs
  - Energy consumption: Fighting current uses power

Typical ocean currents: 0.1 - 2 m/s

Usage:
  ros2 run reef_drone_demos break_current --ros-args -p mode:=constant -p strength:=0.5
"""

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Wrench


class BreakCurrent(Node):
    """Injects ocean current disturbance."""

    def __init__(self):
        super().__init__('break_current')

        self.declare_parameter('mode', 'constant')  # constant, oscillating, random
        self.declare_parameter('strength', 10.0)  # N (force)
        self.declare_parameter('direction', 0.0)  # rad (0 = +X)
        self.declare_parameter('period', 60.0)  # s (for oscillating)

        self.mode = self.get_parameter('mode').value
        self.strength = self.get_parameter('strength').value
        self.direction = self.get_parameter('direction').value
        self.period = self.get_parameter('period').value

        self.start_time = self.get_clock().now()

        self.pub = self.create_publisher(
            Wrench, '/disturbance/current', 10)

        self.timer = self.create_timer(0.02, self.publish_current)

        self.get_logger().info(
            f'Applying current: mode={self.mode}, strength={self.strength}N')
        self.get_logger().info(
            'Note: Apply this wrench to base_link in Gazebo')

    def publish_current(self):
        wrench = Wrench()

        if self.mode == 'constant':
            fx = self.strength * np.cos(self.direction)
            fy = self.strength * np.sin(self.direction)
        elif self.mode == 'oscillating':
            elapsed = (self.get_clock().now() - self.start_time).nanoseconds * 1e-9
            scale = np.sin(2 * np.pi * elapsed / self.period)
            fx = self.strength * scale * np.cos(self.direction)
            fy = self.strength * scale * np.sin(self.direction)
        elif self.mode == 'random':
            fx = np.random.normal(0, self.strength / 3)
            fy = np.random.normal(0, self.strength / 3)
        else:
            fx = fy = 0.0

        wrench.force.x = fx
        wrench.force.y = fy
        wrench.force.z = 0.0

        self.pub.publish(wrench)


def main(args=None):
    rclpy.init(args=args)
    node = BreakCurrent()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
