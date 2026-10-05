#!/usr/bin/env python3
"""Publishes two numbers (a, b) on the 'chatter' topic as a NumPair message.
Numpair is a custom message type defined in cex_pkg/msg/NumPair.msg"""


import rclpy
from rclpy.node import Node
from cex_pkg.msg import NumPair


class PubTwoNumbers(Node):

    def __init__(self) -> None:
        super().__init__('publish_two_numbers')

        self.publisher_ = self.create_publisher(NumPair, 'chatter', 10)
        self.timer_period = 1.0
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.a = 50
        self.b = 0
        self.count = 0

        self.get_logger().info('PubTwoNumbers node started.')

    def timer_callback(self) -> None:
        msg = NumPair()
        msg.a = self.a
        msg.b = self.b
        self.publisher_.publish(msg)

        self.get_logger().info(f'Publishing two numbers: a={msg.a}, b={msg.b}')

        self.a += 1
        self.b += 2
        self.count += 1


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PubTwoNumbers()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info('Shutting down PubTwoNumbers node.')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
