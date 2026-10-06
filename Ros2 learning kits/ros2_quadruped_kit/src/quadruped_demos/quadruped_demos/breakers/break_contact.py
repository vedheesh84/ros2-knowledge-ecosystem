#!/usr/bin/env python3
"""
break_contact.py - Contact Detection Failure

Injects faults into contact detection to teach:
- Importance of accurate contact for gait
- Effects of false positives/negatives
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool

class BreakContact(Node):
    def __init__(self):
        super().__init__('break_contact')
        self.declare_parameter('leg', 'FL')
        self.declare_parameter('mode', 'stuck_on')  # stuck_on, stuck_off, random

        self.leg = self.get_parameter('leg').value
        self.mode = self.get_parameter('mode').value

        self.pub = self.create_publisher(Bool, f'/contact/{self.leg}', 10)
        self.create_timer(0.01, self.inject_fault)

        self.get_logger().info(f'Breaking contact for {self.leg} with mode: {self.mode}')

    def inject_fault(self):
        msg = Bool()
        if self.mode == 'stuck_on':
            msg.data = True
        elif self.mode == 'stuck_off':
            msg.data = False
        else:
            import random
            msg.data = random.random() > 0.5
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = BreakContact()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
