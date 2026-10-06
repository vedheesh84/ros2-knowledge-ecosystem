#!/usr/bin/env python3
"""Demo 07: Disturbance Recovery - Push recovery behavior."""
import rclpy
from rclpy.node import Node

class DisturbanceDemo(Node):
    def __init__(self):
        super().__init__('demo_07_disturbance')
        self.get_logger().info('Demo 07: Disturbance Recovery')
        self.get_logger().info('Push the robot (in simulation or real) to test recovery')

def main(args=None):
    rclpy.init(args=args)
    node = DisturbanceDemo()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
