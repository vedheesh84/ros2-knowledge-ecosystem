#!/usr/bin/env python3
"""
Demo 04: Heading Control

LEARNING OBJECTIVES:
====================
1. Understand yaw (heading) control
2. See angle wrapping in action
3. Learn about magnetometer-based heading

WHAT THIS DEMO DOES:
====================
1. Commands rotation to various headings
2. Shows smooth transitions through ±180°
3. Demonstrates heading hold under perturbation

ANGLE WRAPPING:
===============
When commanded to turn from 170° to -170°, the robot should:
  - Turn 20° (shortest path)
  - NOT turn 340° (long way around)

This requires proper angle error calculation:
  error = atan2(sin(target - current), cos(target - current))
"""

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class Demo04HeadingControl(Node):
    """Demo 04: Test heading (yaw) controller."""

    def __init__(self):
        super().__init__('demo_04_heading_control')

        self.setpoint_pub = self.create_publisher(
            Float64, '/heading/setpoint', 10)
        self.heading_sub = self.create_subscription(
            Float64, '/heading', self.heading_callback, 10)

        self.current_heading = 0.0

        self.get_logger().info('=== Demo 04: Heading Control ===')
        self.get_logger().info('')
        self.get_logger().info('This demo rotates the AUV to various headings.')
        self.get_logger().info('Watch angle wrapping at ±180°.')
        self.get_logger().info('')

        # Demo sequence (in radians)
        self.headings = [
            0.0,              # North
            np.pi / 2,        # East (90°)
            np.pi,            # South (180°)
            -np.pi / 2,       # West (-90°)
            np.pi * 0.9,      # 162° (near wrap)
            -np.pi * 0.9,     # -162° (test shortest path)
            0.0               # Back to North
        ]

        self.timer = self.create_timer(1.0, self.demo_loop)
        self.demo_step = 0
        self.step_start_time = self.get_clock().now()
        self.step_duration = 10.0

    def heading_callback(self, msg: Float64):
        self.current_heading = msg.data

    def demo_loop(self):
        elapsed = (self.get_clock().now() - self.step_start_time).nanoseconds * 1e-9

        if self.demo_step >= len(self.headings):
            self.get_logger().info('Demo complete!')
            self.timer.cancel()
            return

        target = self.headings[self.demo_step]

        # Publish setpoint
        msg = Float64()
        msg.data = target
        self.setpoint_pub.publish(msg)

        # Log progress
        error = np.arctan2(
            np.sin(target - self.current_heading),
            np.cos(target - self.current_heading)
        )
        self.get_logger().info(
            f'Target: {np.degrees(target):.0f}° | '
            f'Current: {np.degrees(self.current_heading):.0f}° | '
            f'Error: {np.degrees(error):.0f}°')

        if elapsed >= self.step_duration:
            self.demo_step += 1
            self.step_start_time = self.get_clock().now()
            if self.demo_step < len(self.headings):
                self.get_logger().info(
                    f'\n>>> New heading: {np.degrees(self.headings[self.demo_step]):.0f}°')


def main(args=None):
    rclpy.init(args=args)
    node = Demo04HeadingControl()
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
