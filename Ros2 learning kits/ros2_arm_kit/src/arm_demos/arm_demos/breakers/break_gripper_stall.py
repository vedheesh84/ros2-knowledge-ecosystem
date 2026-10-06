#!/usr/bin/env python3
"""
Breaker: Gripper Stall & Obstruction Fault Injection
====================================================
Simulates missed grasp or motor stall condition by requesting an over-travel
or obstructed grasp position on /gripper/command and verifying timeout/stall feedback.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

class BreakGripperStall(Node):
    def __init__(self):
        super().__init__('break_gripper_stall')
        self.pub = self.create_publisher(Float32, '/gripper/command', 10)
        self.sub = self.create_subscription(String, '/gripper/status', self.feedback_callback, 10)
        self.timer = self.create_timer(2.0, self.inject_stall_command)
        self.get_logger().warn('BREAKER: Injected Gripper Stall fault - commanding negative / clamped position.')

    def inject_stall_command(self):
        msg = Float32()
        msg.data = -0.5 # Invalid over-closed position triggering clamp/stall behavior
        self.pub.publish(msg)
        self.get_logger().info('Commanded out-of-range gripper travel: -0.5 (expect clamp to 0.0)')

    def feedback_callback(self, msg: String):
        self.get_logger().info(f'Gripper Response to Fault: {msg.data}')

def main(args=None):
    rclpy.init(args=args)
    node = BreakGripperStall()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
