#!/usr/bin/env python3
"""
break_imu.py - IMU Failure Injection

LEARNING OBJECTIVES:
====================
1. Understand IMU importance for balance
2. See gyro bias effects on orientation
3. Learn accelerometer noise effects

WHAT THIS BREAKER DOES:
=======================
Simulates IMU failures:
  - noise: Add significant noise
  - gyro_bias: Growing gyroscope bias
  - dropout: Intermittent measurements

IMU BIAS EFFECTS:
=================
Gyroscope bias causes:
  - Orientation drift over time
  - Error grows as ∫bias dt
  - 1°/s bias = 60°/min drift!

Accelerometer bias causes:
  - Velocity integration error
  - Position drift (double integration)

Usage:
  ros2 run reef_drone_demos break_imu --ros-args -p mode:=gyro_bias
"""

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu


class BreakIMU(Node):
    """Injects IMU failures."""

    def __init__(self):
        super().__init__('break_imu')

        self.declare_parameter('mode', 'noise')  # noise, gyro_bias, dropout
        self.declare_parameter('noise_stddev', 0.5)  # rad/s or m/s²
        self.declare_parameter('bias_rate', 0.01)  # rad/s per second

        self.mode = self.get_parameter('mode').value
        self.noise_stddev = self.get_parameter('noise_stddev').value
        self.bias_rate = self.get_parameter('bias_rate').value

        self.start_time = self.get_clock().now()

        self.sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)
        self.pub = self.create_publisher(
            Imu, '/imu/data_broken', 10)

        self.get_logger().info(f'Breaking IMU with mode: {self.mode}')

    def imu_callback(self, msg: Imu):
        if self.mode == 'dropout':
            if np.random.random() < 0.3:
                return

        broken = Imu()
        broken.header = msg.header
        broken.orientation = msg.orientation
        broken.angular_velocity = msg.angular_velocity
        broken.linear_acceleration = msg.linear_acceleration

        if self.mode == 'noise':
            broken.angular_velocity.x += np.random.normal(0, self.noise_stddev)
            broken.angular_velocity.y += np.random.normal(0, self.noise_stddev)
            broken.angular_velocity.z += np.random.normal(0, self.noise_stddev)
        elif self.mode == 'gyro_bias':
            elapsed = (self.get_clock().now() - self.start_time).nanoseconds * 1e-9
            bias = self.bias_rate * elapsed
            broken.angular_velocity.z += bias

        self.pub.publish(broken)


def main(args=None):
    rclpy.init(args=args)
    node = BreakIMU()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
