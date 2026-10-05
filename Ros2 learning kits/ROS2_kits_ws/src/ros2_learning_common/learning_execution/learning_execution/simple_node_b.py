#!/usr/bin/env python3
"""
Simple Node B - Data Consumer for Launch Demos
===============================================

LEARNING OBJECTIVES:
--------------------
This node exists to demonstrate launch file concepts:
1. How remapping connects nodes dynamically
2. How the SAME nodes can be wired differently at launch
3. The separation between code and configuration

WHAT THIS NODE DOES:
--------------------
- Subscribes to a topic and logs received messages
- The topic name is configurable (for remapping demos)

KEY INSIGHT:
------------
Node A publishes to /data_out
Node B subscribes to /data_in

They DON'T match by default!

But with remapping, we can connect them:
    ros2 run learning_execution simple_node_b --ros-args -r /data_in:=/data_out

This is the power of remapping: change connections WITHOUT changing code!

USAGE:
------
    # Direct run (won't receive anything unless something publishes to /data_in)
    ros2 run learning_execution simple_node_b

    # With remapping to connect to Node A
    ros2 run learning_execution simple_node_b --ros-args -r /data_in:=/data_out
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimpleNodeB(Node):
    """A simple subscriber node for launch file demonstrations."""

    def __init__(self):
        super().__init__('simple_node_b')

        self.get_logger().info('Simple Node B starting...')

        # Declare parameters
        self.declare_parameter('log_level', 'info')

        # Create subscriber
        # Topic name can be remapped at launch time!
        self.subscription = self.create_subscription(
            String,
            '/data_in',  # Default topic - can be remapped
            self.data_callback,
            10
        )

        self.messages_received = 0

        self.get_logger().info('Subscribing to /data_in')
        self.get_logger().info('Hint: Remap to connect to Node A: -r /data_in:=/data_out')

    def data_callback(self, msg):
        """Process received messages."""
        self.messages_received += 1
        self.get_logger().info(f'Received #{self.messages_received}: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = SimpleNodeB()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.get_logger().info(f'Total messages received: {node.messages_received}')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
