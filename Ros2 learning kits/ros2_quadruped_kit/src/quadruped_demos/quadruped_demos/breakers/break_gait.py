#!/usr/bin/env python3
"""
break_gait.py - Gait Timing Failure

Injects timing faults to teach:
- Importance of gait phase coordination
- Effects of timing jitter
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class BreakGait(Node):
    def __init__(self):
        super().__init__('break_gait')
        self.declare_parameter('mode', 'phase_offset')  # phase_offset, duty_wrong
        self.mode = self.get_parameter('mode').value

        self.sub = self.create_subscription(
            Float64MultiArray, '/gait/contact_schedule', self.schedule_callback, 10)
        self.pub = self.create_publisher(
            Float64MultiArray, '/gait/contact_schedule_broken', 10)

        self.get_logger().info(f'Breaking gait with mode: {self.mode}')

    def schedule_callback(self, msg):
        broken = Float64MultiArray()
        if self.mode == 'phase_offset':
            # Swap front and rear timing
            broken.data = [msg.data[2], msg.data[3], msg.data[0], msg.data[1]]
        else:
            broken.data = list(msg.data)
        self.pub.publish(broken)

def main(args=None):
    rclpy.init(args=args)
    node = BreakGait()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
