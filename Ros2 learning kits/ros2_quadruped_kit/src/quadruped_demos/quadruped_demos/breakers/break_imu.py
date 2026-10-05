#!/usr/bin/env python3
"""
break_imu.py - IMU Failure Injection

Injects faults into IMU data to teach:
- Importance of IMU for balance
- Effects of sensor noise
- Bias drift behavior
"""
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class BreakIMU(Node):
    def __init__(self):
        super().__init__('break_imu')
        self.declare_parameter('mode', 'noise')  # noise, bias, dropout
        self.mode = self.get_parameter('mode').value

        self.sub = self.create_subscription(Imu, '/imu/data', self.imu_callback, 10)
        self.pub = self.create_publisher(Imu, '/imu/data_broken', 10)

        self.get_logger().info(f'Breaking IMU with mode: {self.mode}')

    def imu_callback(self, msg):
        broken = Imu()
        broken.header = msg.header

        if self.mode == 'noise':
            # Add significant noise
            broken.angular_velocity.x = msg.angular_velocity.x + np.random.normal(0, 0.5)
            broken.angular_velocity.y = msg.angular_velocity.y + np.random.normal(0, 0.5)
            broken.angular_velocity.z = msg.angular_velocity.z + np.random.normal(0, 0.5)
        elif self.mode == 'bias':
            # Add growing bias
            t = self.get_clock().now().nanoseconds * 1e-9
            broken.angular_velocity.z = msg.angular_velocity.z + 0.01 * t
        else:
            broken = msg

        self.pub.publish(broken)

def main(args=None):
    rclpy.init(args=args)
    node = BreakIMU()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
