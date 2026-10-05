#!/usr/bin/env python3
"""
A simple ROS 2 subscriber node that listens to the 'chatter' topic for String messages
and logs them to the console.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleSubscriber(Node):

    def __init__(self) -> None:
        super().__init__('simple_subscriber')

        #                              msg type = string, topic = 'chatter', listener callback, queue size = 10
        self.subscription = self.create_subscription(String,'chatter',self.listener_callback,10)

        self.get_logger().info('SimpleSubscriber node has been started.')

    def listener_callback(self, msg: String) -> None:
        #Callback function executed whenever a new message is received.
        self.get_logger().info(f'Received message: "{msg.data}"')


def main(args=None) -> None:
    
    rclpy.init(args=args)

    simple_subscriber = SimpleSubscriber()

    try:
        rclpy.spin(simple_subscriber)
    except KeyboardInterrupt:
        pass
    finally:
        simple_subscriber.get_logger().info('Shutting down SimpleSubscriber node.')
        simple_subscriber.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
