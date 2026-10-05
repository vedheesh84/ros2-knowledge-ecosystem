#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class BreakCommDrop(Node):
    """Breaker: Simulates inter-agent network packet drop and isolated flight fallback."""
    def __init__(self):
        super().__init__('break_comm_drop')
        self.timer = self.create_timer(2.0, self.simulate_drop)
        self.get_logger().warn('BREAKER: Simulating packet drop for follower drone_2.')

    def simulate_drop(self):
        self.get_logger().error('[drone_2] Heartbeat timeout from Leader! Entering autonomous hovering hold.')

def main(args=None):
    rclpy.init(args=args)
    node = BreakCommDrop()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
