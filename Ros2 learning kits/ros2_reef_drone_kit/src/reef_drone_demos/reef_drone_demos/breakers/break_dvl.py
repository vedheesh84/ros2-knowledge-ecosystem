#!/usr/bin/env python3
"""
break_dvl.py - DVL Failure Injection

LEARNING OBJECTIVES:
====================
1. Understand DVL importance for navigation
2. See dead reckoning drift without DVL
3. Learn sensor fusion degradation

WHAT THIS BREAKER DOES:
=======================
Simulates DVL failures:
  - noise: Add significant noise to velocity
  - dropout: Intermittent loss of measurements
  - bias: Constant velocity bias

WITHOUT DVL:
============
When DVL fails, the AUV must rely on:
  - IMU integration (drifts rapidly)
  - Model-based velocity estimation
  - Surface GPS fixes (if available)

Dead reckoning error grows ~1% of distance traveled.

Usage:
  ros2 run reef_drone_demos break_dvl --ros-args -p mode:=dropout -p dropout_prob:=0.5
"""

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistWithCovarianceStamped


class BreakDVL(Node):
    """Injects DVL failures."""

    def __init__(self):
        super().__init__('break_dvl')

        self.declare_parameter('mode', 'noise')  # noise, dropout, bias
        self.declare_parameter('noise_stddev', 0.5)  # m/s
        self.declare_parameter('dropout_prob', 0.3)
        self.declare_parameter('bias_x', 0.1)  # m/s

        self.mode = self.get_parameter('mode').value
        self.noise_stddev = self.get_parameter('noise_stddev').value
        self.dropout_prob = self.get_parameter('dropout_prob').value
        self.bias_x = self.get_parameter('bias_x').value

        self.sub = self.create_subscription(
            TwistWithCovarianceStamped, '/dvl/velocity',
            self.dvl_callback, 10)
        self.pub = self.create_publisher(
            TwistWithCovarianceStamped, '/dvl/velocity_broken', 10)

        self.get_logger().info(f'Breaking DVL with mode: {self.mode}')

    def dvl_callback(self, msg: TwistWithCovarianceStamped):
        if self.mode == 'dropout':
            if np.random.random() < self.dropout_prob:
                return  # Don't publish

        broken = TwistWithCovarianceStamped()
        broken.header = msg.header
        broken.twist = msg.twist

        if self.mode == 'noise':
            broken.twist.twist.linear.x += np.random.normal(0, self.noise_stddev)
            broken.twist.twist.linear.y += np.random.normal(0, self.noise_stddev)
            broken.twist.twist.linear.z += np.random.normal(0, self.noise_stddev)
        elif self.mode == 'bias':
            broken.twist.twist.linear.x += self.bias_x

        self.pub.publish(broken)


def main(args=None):
    rclpy.init(args=args)
    node = BreakDVL()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
