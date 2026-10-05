#!/usr/bin/env python3
"""MoveTurtle node that publishes velocity commands as twist msg to control a turtle in turtlesim."""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
"""
twist - message type used for controlling robots velocities
linear: Vector3   x, y, z linear speeds
angular: Vector3  x, y, z angular speeds - rpy, roll pitch yaw
"""


class MoveTurtle(Node):
    def __init__(self) -> None:
        super().__init__('move_turtle')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10) # topic turtle1/cmd_vel is a pre-existing topic in turtlesim
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info('MoveTurtle node started.')

    def timer_callback(self) -> None:
        msg = Twist()
        msg.linear.x = 2.0
        msg.linear.y = 1.0
        msg.angular.z = 1.0
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing velocity command.')


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MoveTurtle()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info('Shutting down MoveTurtle node.')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
