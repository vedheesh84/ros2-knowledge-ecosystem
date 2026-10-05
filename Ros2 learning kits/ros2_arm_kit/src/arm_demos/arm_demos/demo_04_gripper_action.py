#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

class Demo04GripperAction(Node):
    """Demo 04: Parallel Gripper Actuation & Validation."""
    def __init__(self):
        super().__init__('demo_04_gripper_action')
        self.pub = self.create_publisher(Float32, '/gripper/command', 10)
        self.sub = self.create_subscription(String, '/gripper/status', self.cb, 10)
        self.state = 0
        self.timer = self.create_timer(2.5, self.toggle_gripper)
        self.get_logger().info('Demo 04: Testing Parallel Gripper Open / Close commands.')

    def toggle_gripper(self):
        msg = Float32()
        if self.state % 2 == 0:
            msg.data = 1.0  # Open
            self.get_logger().info('Commanding: GRIPPER OPEN')
        else:
            msg.data = 0.0  # Close
            self.get_logger().info('Commanding: GRIPPER CLOSE')
        self.pub.publish(msg)
        self.state += 1

    def cb(self, msg: String):
        self.get_logger().info(f'Gripper Feedback: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = Demo04GripperAction()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
