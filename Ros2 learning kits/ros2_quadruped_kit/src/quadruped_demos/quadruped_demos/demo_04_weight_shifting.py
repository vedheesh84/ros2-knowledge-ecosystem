#!/usr/bin/env python3
"""Demo 04: Weight Shifting - Body movement while maintaining balance."""
import rclpy
from rclpy.node import Node

class WeightShiftingDemo(Node):
    def __init__(self):
        super().__init__('demo_04_weight_shifting')
        self.get_logger().info('Demo 04: Weight Shifting - Dynamic balance demo')

def main(args=None):
    rclpy.init(args=args)
    node = WeightShiftingDemo()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
