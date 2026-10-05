#!/usr/bin/env python3
"""Subscriber node that calls AddTwoInt service when receiving even numbers. output is added sum of a and b."""


import rclpy
from rclpy.node import Node
from cex_pkg.msg import NumPair
from cex_pkg.srv import AddTwoInt
"""add_two_int is the service file defined in cex_pkg/srv/AddTwoInt.srv"""


class SubClientAdd(Node):

    def __init__(self) -> None:
        super().__init__('subscriber_client_node')

        # Create service client
        self.client_ = self.create_client(AddTwoInt, 'add_two_int')
        while not self.client_.wait_for_service(timeout_sec=1.0):           # Wait for the service returns true when server is available
            self.get_logger().info('Waiting for add_two_int service...')

        # subscriber - receives a and b from PubTwoNumbers node
        self.subscription_ = self.create_subscription(NumPair,'chatter',self.listener_callback, 10)
        self.get_logger().info('SubClientAdd node started.')

    def listener_callback(self, msg: NumPair) -> None:
        self.get_logger().info(f'Received: a={msg.a}, b={msg.b}')

        # Call service if 'a' is even, since b is always even
        if msg.a % 2 == 0:
            self.get_logger().info(f'Calling service for a={msg.a}, b={msg.b}')
            self.call_add_service(msg.a, msg.b)

    def call_add_service(self, a: int, b: int) -> None:
        """Send async service request to AddTwoInt service."""
        request = AddTwoInt.Request()
        request.a = a
        request.b = b

        future = self.client_.call_async(request)
        future.add_done_callback(self.handle_response)

    def handle_response(self, future) -> None:
        """Handle the service response."""
        try:
            response = future.result()
            self.get_logger().info(f'Service response: sum={response.sum}')
        except Exception as e:
            self.get_logger().error(f'Service call failed: {e}')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SubClientAdd()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info('Shutting down SubClientAdd node.')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
