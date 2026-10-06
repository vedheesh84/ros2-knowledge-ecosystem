#!/usr/bin/env python3
"""
Demo 03: Depth Hold

LEARNING OBJECTIVES:
====================
1. Understand PID depth control
2. See integral term eliminate steady-state error
3. Observe effect of buoyancy on control

WHAT THIS DEMO DOES:
====================
1. Commands the AUV to hold at various depths
2. Shows PID controller behavior
3. Demonstrates disturbance rejection

PID TUNING:
===========
Proportional (Kp): Response strength to error
  - Too low: Sluggish, large error
  - Too high: Oscillation

Integral (Ki): Eliminates steady-state error
  - Important for buoyancy compensation
  - Too high: Overshoot, windup

Derivative (Kd): Damps oscillations
  - Responds to rate of change
  - Too high: Noise sensitivity

Usage:
  ros2 run reef_drone_demos demo_03_depth_hold
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class Demo03DepthHold(Node):
    """Demo 03: Test PID depth controller."""

    def __init__(self):
        super().__init__('demo_03_depth_hold')

        self.setpoint_pub = self.create_publisher(
            Float64, '/depth/setpoint', 10)
        self.depth_sub = self.create_subscription(
            Float64, '/depth', self.depth_callback, 10)

        self.current_depth = 0.0

        self.get_logger().info('=== Demo 03: Depth Hold ===')
        self.get_logger().info('')
        self.get_logger().info('This demo commands the depth controller to hold at')
        self.get_logger().info('various depths. Watch the PID response.')
        self.get_logger().info('')

        # Run demo sequence
        self.timer = self.create_timer(1.0, self.demo_loop)
        self.demo_step = 0
        self.step_start_time = self.get_clock().now()
        self.depths = [5.0, 10.0, 7.0, 15.0, 5.0]
        self.step_duration = 15.0  # seconds per depth

    def depth_callback(self, msg: Float64):
        self.current_depth = msg.data

    def demo_loop(self):
        """Progress through demo steps."""
        elapsed = (self.get_clock().now() - self.step_start_time).nanoseconds * 1e-9

        if self.demo_step >= len(self.depths):
            self.get_logger().info('Demo complete!')
            self.timer.cancel()
            return

        target = self.depths[self.demo_step]

        # Publish setpoint
        msg = Float64()
        msg.data = target
        self.setpoint_pub.publish(msg)

        # Log progress
        error = target - self.current_depth
        self.get_logger().info(
            f'Target: {target:.1f}m | Current: {self.current_depth:.2f}m | '
            f'Error: {error:.2f}m')

        if elapsed >= self.step_duration:
            self.demo_step += 1
            self.step_start_time = self.get_clock().now()
            if self.demo_step < len(self.depths):
                self.get_logger().info(
                    f'\n>>> Moving to depth: {self.depths[self.demo_step]}m')


def main(args=None):
    rclpy.init(args=args)
    node = Demo03DepthHold()
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
