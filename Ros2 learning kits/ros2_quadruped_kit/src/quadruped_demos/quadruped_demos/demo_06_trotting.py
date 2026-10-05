#!/usr/bin/env python3
"""Demo 06: Trotting - Diagonal gait for faster locomotion."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class TrottingDemo(Node):
    def __init__(self):
        super().__init__('demo_06_trotting')
        self.vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.behavior_pub = self.create_publisher(String, '/behavior/command', 10)
        self.create_timer(0.1, self.demo_loop)
        self.get_logger().info('Demo 06: Trotting - Fast locomotion demo')

    def demo_loop(self):
        cmd = String()
        cmd.data = 'trot'
        self.behavior_pub.publish(cmd)
        vel = Twist()
        vel.linear.x = 0.5
        self.vel_pub.publish(vel)

def main(args=None):
    rclpy.init(args=args)
    node = TrottingDemo()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
