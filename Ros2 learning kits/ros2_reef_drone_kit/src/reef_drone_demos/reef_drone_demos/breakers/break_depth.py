#!/usr/bin/env python3
"""
break_depth.py - Depth Sensor Failure Injection

LEARNING OBJECTIVES:
====================
1. Understand depth sensor importance
2. See trim/buoyancy compensation issues
3. Learn sensor calibration effects

WHAT THIS BREAKER DOES:
=======================
Simulates depth sensor failures:
  - bias: Constant offset (miscalibration)
  - drift: Growing error over time
  - stuck: Sensor reading frozen

EFFECTS OF DEPTH BIAS:
======================
- AUV thinks it's at wrong depth
- Depth controller tries to compensate
- Actual depth differs from commanded
- Can cause bottom collisions or surfacing

Usage:
  ros2 run reef_drone_demos break_depth --ros-args -p mode:=bias -p bias:=2.0
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class BreakDepth(Node):
    """Injects depth sensor failures."""

    def __init__(self):
        super().__init__('break_depth')

        self.declare_parameter('mode', 'bias')  # bias, drift, stuck
        self.declare_parameter('bias', 2.0)  # m
        self.declare_parameter('drift_rate', 0.1)  # m/s
        self.declare_parameter('stuck_value', 5.0)  # m

        self.mode = self.get_parameter('mode').value
        self.bias = self.get_parameter('bias').value
        self.drift_rate = self.get_parameter('drift_rate').value
        self.stuck_value = self.get_parameter('stuck_value').value

        self.start_time = self.get_clock().now()

        self.sub = self.create_subscription(
            Float64, '/depth', self.depth_callback, 10)
        self.pub = self.create_publisher(
            Float64, '/depth_broken', 10)

        self.get_logger().info(f'Breaking depth sensor with mode: {self.mode}')

    def depth_callback(self, msg: Float64):
        broken = Float64()

        if self.mode == 'bias':
            broken.data = msg.data + self.bias
        elif self.mode == 'drift':
            elapsed = (self.get_clock().now() - self.start_time).nanoseconds * 1e-9
            broken.data = msg.data + self.drift_rate * elapsed
        elif self.mode == 'stuck':
            broken.data = self.stuck_value
        else:
            broken.data = msg.data

        self.pub.publish(broken)


def main(args=None):
    rclpy.init(args=args)
    node = BreakDepth()
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
