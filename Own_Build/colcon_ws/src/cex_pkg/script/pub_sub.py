#!/usr/bin/env python3
"""A ROS 2 node that publishes and subscribes to the same 'chatter' topic."""


import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimplePubSub(Node):

    def __init__(self) -> None:
        super().__init__('simple_pub_sub')

        # Publisher
        self.publisher_ = self.create_publisher(String, 'chatter', 10)

        # Timer for periodic publishing
        self.timer_period = 1.0
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        # Subscription
        self.subscription_ = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10
        )

        self.count = 0
        self.get_logger().info('SimplePubSub node started.')

    def timer_callback(self) -> None:
        msg = String()
        msg.data = f'Instance: {self.count}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1

    def listener_callback(self, msg: String) -> None:
        self.get_logger().info(f'Received: "{msg.data}"')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SimplePubSub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info('Shutting down SimplePubSub node.')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
