#!/usr/bin/env python3
"""Service node that adds two integers received from a client."""

import rclpy
from rclpy.node import Node
from cex_pkg.srv import AddTwoInt


class AddTwoIntSrv(Node):

    def __init__(self) -> None:
        super().__init__('add_two_int_srv')
        self.srv_ = self.create_service(
            AddTwoInt,
            'add_two_int',
            self.add_two_int_callback
        )
        self.get_logger().info('AddTwoIntSrv node started.')

    def add_two_int_callback(self, request: AddTwoInt.Request, response: AddTwoInt.Response) -> AddTwoInt.Response:
        response.sum = request.a + request.b
        self.get_logger().info(f'Received request: a={request.a}, b={request.b}, sum={response.sum}')
        return response


def main(args=None) -> None:
    rclpy.init(args=args)
    node = AddTwoIntSrv()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info('Shutting down AddTwoIntSrv node.')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
