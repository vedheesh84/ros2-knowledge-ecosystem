#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class WheelPublisher(Node):
    def __init__(self):
        super().__init__('wheel_publisher')

        self.publisher_ = self.create_publisher(JointState, 'joint_states', 10)

        # Publish at 50 Hz
        self.timer = self.create_timer(0.02, self.timer_callback)

        # Internal state
        self.left_pos = 0.0
        self.right_pos = 0.0
        self.wheel_velocity = 4.0  # rad/s (angular velocity)

    def timer_callback(self):
        dt = self.timer.timer_period_ns * 1e-9

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['left_wheel', 'right_wheel']

        # Update positions
        self.left_pos += self.wheel_velocity * dt
        self.right_pos += self.wheel_velocity * dt

        msg.position = [self.left_pos, self.right_pos]
        msg.velocity = [self.wheel_velocity, self.wheel_velocity]

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = WheelPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
