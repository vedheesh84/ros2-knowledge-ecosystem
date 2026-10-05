#!/usr/bin/env python3
"""
Simple Node A - Data Producer for Launch Demos
===============================================

LEARNING OBJECTIVES:
--------------------
This node exists to demonstrate launch file concepts:
1. How to start nodes from launch files
2. How remapping changes topic names
3. How parameters can be passed at launch
4. How nodes can be namespaced

WHAT THIS NODE DOES:
--------------------
- Publishes numbered messages to a topic
- The topic name is configurable (for remapping demos)
- The message format is configurable (via parameters)

This node is intentionally simple so you can focus on LAUNCH concepts,
not on what the node does.

USAGE:
------
    # Direct run
    ros2 run learning_execution simple_node_a

    # With remapping
    ros2 run learning_execution simple_node_a --ros-args -r /data_out:=/custom_topic

    # With namespace
    ros2 run learning_execution simple_node_a --ros-args -r __ns:=/robot1
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleNodeA(Node):
    """A simple publisher node for launch file demonstrations."""

    def __init__(self):
        super().__init__('simple_node_a')

        self.get_logger().info('Simple Node A starting...')

        # Declare parameters
        self.declare_parameter('publish_rate', 1.0)
        self.declare_parameter('message_prefix', 'Data from A')

        # Get parameters
        self.publish_rate = self.get_parameter('publish_rate').value
        self.message_prefix = self.get_parameter('message_prefix').value

        # Create publisher
        # Topic name can be remapped at launch time!
        self.publisher = self.create_publisher(String, '/data_out', 10)

        # Create timer
        self.timer = self.create_timer(1.0 / self.publish_rate, self.publish_data)
        self.count = 0

        self.get_logger().info(f'Publishing to /data_out at {self.publish_rate} Hz')
        self.get_logger().info(f'Message prefix: "{self.message_prefix}"')

    def publish_data(self):
        """Publish a numbered message."""
        self.count += 1
        msg = String()
        msg.data = f'{self.message_prefix}: message #{self.count}'
        self.publisher.publish(msg)
        self.get_logger().debug(f'Published: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = SimpleNodeA()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
