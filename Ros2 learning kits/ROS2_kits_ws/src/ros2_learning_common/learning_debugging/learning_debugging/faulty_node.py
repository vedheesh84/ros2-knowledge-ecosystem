#!/usr/bin/env python3
"""
Faulty Node - Debugging Practice
=================================

LEARNING OBJECTIVES:
--------------------
This node has INTENTIONAL BUGS for you to find and fix!
It demonstrates common ROS2 debugging scenarios.

YOUR MISSION:
-------------
1. Run the node
2. Observe the problems
3. Use ROS2 tools to diagnose
4. Find the bugs (don't look at the source first!)

DEBUGGING TOOLS:
----------------
    ros2 node list          - Is the node running?
    ros2 topic list         - What topics exist?
    ros2 topic echo /topic  - What's being published?
    ros2 topic hz /topic    - What's the rate?
    rqt_graph               - Visualize connections
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import random


class FaultyNode(Node):
    """A node with intentional bugs for debugging practice."""

    def __init__(self):
        super().__init__('faulty_node')
        self.get_logger().info('Faulty Node starting...')
        self.get_logger().info('Something is wrong with this node!')
        self.get_logger().info('Use ROS2 tools to find the bugs!')

        # BUG 1: Publishing to wrong topic name
        # Expected: /data_output
        # Actual: /data_outptu (typo!)
        self.publisher = self.create_publisher(String, '/data_outptu', 10)

        # BUG 2: Subscribing but callback has issues
        self.subscription = self.create_subscription(
            String, '/data_input', self.buggy_callback, 10
        )

        # Timer publishes, but...
        self.timer = self.create_timer(1.0, self.publish_data)

        # BUG 3: This counter never increments properly
        self.counter = 0

    def publish_data(self):
        """Publish data (or try to...)."""
        msg = String()
        # BUG 4: Counter is always 0!
        msg.data = f'Message #{self.counter}'
        self.publisher.publish(msg)

        # Forgot to increment!
        # self.counter += 1

    def buggy_callback(self, msg):
        """Process incoming data (with bugs)."""
        # BUG 5: Logging at wrong level (debug, not visible by default)
        self.get_logger().debug(f'Received: {msg.data}')

        # BUG 6: Exception on certain input
        if 'crash' in msg.data.lower():
            raise ValueError('Intentional crash for debugging practice!')


def main(args=None):
    rclpy.init(args=args)
    node = FaultyNode()
    try:
        rclpy.spin(node)
    except Exception as e:
        node.get_logger().error(f'Node crashed: {e}')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
