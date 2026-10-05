#!/usr/bin/env python3
"""Demo 02: Leg Kinematics - Forward/Inverse kinematics visualization."""
import rclpy
from rclpy.node import Node

class LegKinematicsDemo(Node):
    def __init__(self):
        super().__init__('demo_02_leg_kinematics')
        self.get_logger().info('Demo 02: Leg Kinematics - Visualize FK/IK')

def main(args=None):
    rclpy.init(args=args)
    node = LegKinematicsDemo()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
