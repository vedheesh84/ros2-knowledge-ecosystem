#!/usr/bin/env python3
"""
A simple ROS 2 publisher node that publishes incrementing messages
of type String, to the 'chatter' topic every second.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimplePublisher(Node):
    
    def __init__(self) -> None:
        super().__init__('simple_publisher')

        #                        msg type = string, topic = 'chatter', queue size = 10
        self.publisher_ = self.create_publisher(String, 'chatter', 10)

        # Timer: triggers callback every 1.0 seconds
        self.timer_period = 1.0
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.count = 0
        self.get_logger().info('SimplePublisher node has been started.')

    def timer_callback(self) -> None:
        #Callback executed (every self.timer_period seconds).
        msg = String()
        msg.data = f'Instance: {self.count}'
        self.publisher_.publish(msg)

        # Log message efficiently without repeated string concatenation
        self.get_logger().info(f'Published message: "{msg.data}"')

        self.count += 1


def main(args=None) -> None:
    
    rclpy.init(args=args)

    simple_publisher = SimplePublisher()

    try:
        rclpy.spin(simple_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        simple_publisher.get_logger().info('Shutting down SimplePublisher node.')
        simple_publisher.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
