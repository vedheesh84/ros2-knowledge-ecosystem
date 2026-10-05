#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Demo06PickPlace(Node):
    """Demo 06: Autonomous Tabletop Pick-and-Place State Machine Monitor."""
    def __init__(self):
        super().__init__('demo_06_pick_place')
        self.sub = self.create_subscription(String, '/arm/state', self.cb, 10)
        self.get_logger().info('Demo 06: Monitoring Tabletop Autonomous Pick-and-Place State Machine.')

    def cb(self, msg: String):
        self.get_logger().info(f'State Machine Transition: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = Demo06PickPlace()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
