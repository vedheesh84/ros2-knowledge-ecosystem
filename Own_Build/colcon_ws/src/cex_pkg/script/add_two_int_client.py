#!/usr/bin/env python3
import sys
import rclpy
from rclpy.node import Node
from cex_pkg.srv import AddTwoInt


class AddTwoIntsClient(Node):
    """ROS 2 client node to call AddTwoInt service with two integers."""

    def __init__(self) -> None:
        super().__init__('add_two_ints_client')
        self.client_ = self.create_client(AddTwoInt, 'add_two_int')

        while not self.client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting...')

        self.request_ = AddTwoInt.Request()

    def send_request(self, a: int, b: int):
        """Send async request to the AddTwoInt service."""
        self.request_.a = a
        self.request_.b = b
        return self.client_.call_async(self.request_)


def main(args=None) -> None:
    rclpy.init(args=args)
    client = AddTwoIntsClient()

    if len(sys.argv) != 3:
        client.get_logger().info('Usage: ros2 run <pkg> add_two_ints_client X Y')
    else:
        a, b = int(sys.argv[1]), int(sys.argv[2]) # Get integers from command line
        future = client.send_request(a, b)
        rclpy.spin_until_future_complete(client, future)

        response = future.result()
        if response is not None:
            client.get_logger().info(f'Result: {a} + {b} = {response.sum}')
        else:
            client.get_logger().error('Service call failed or returned None')


    client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
