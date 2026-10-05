#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Demo04DynamicFormation(Node):
    """Demo 04: Dynamically Switching Swarm Formations."""
    def __init__(self):
        super().__init__('demo_04_dynamic_formation')
        self.pub = self.create_publisher(String, '/swarm/formation_mode', 10)
        self.modes = ['V_SHAPE', 'LINE', 'CIRCLE']
        self.idx = 0
        self.timer = self.create_timer(5.0, self.cycle_mode)
        self.get_logger().info('Demo 04: Cycling swarm formation modes (V_SHAPE -> LINE -> CIRCLE).')

    def cycle_mode(self):
        mode = self.modes[self.idx % len(self.modes)]
        msg = String()
        msg.data = mode
        self.pub.publish(msg)
        self.get_logger().info(f'Swarm Mode Triggered: {mode}')
        self.idx += 1

def main(args=None):
    rclpy.init(args=args)
    node = Demo04DynamicFormation()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
