#!/usr/bin/env python3
"""
Noisy Node - Demonstrating All Logging Levels
==============================================

LEARNING OBJECTIVES:
--------------------
1. ROS2 logging levels (DEBUG, INFO, WARN, ERROR, FATAL)
2. When to use each level
3. Controlling log output

LOGGING LEVELS:
---------------
    DEBUG  - Detailed diagnostic info (disabled by default)
    INFO   - Normal operation messages
    WARN   - Something unexpected but not fatal
    ERROR  - Something failed but node continues
    FATAL  - Critical failure, node may crash

USAGE:
------
    # Normal run (INFO and above)
    ros2 run learning_debugging noisy_node

    # With DEBUG enabled
    ros2 run learning_debugging noisy_node --ros-args --log-level debug
"""

import rclpy
from rclpy.node import Node
import random


class NoisyNode(Node):
    """Demonstrates all logging levels."""

    def __init__(self):
        super().__init__('noisy_node')

        self.get_logger().info('=' * 50)
        self.get_logger().info('NOISY NODE - Logging Demo')
        self.get_logger().info('=' * 50)

        self.timer = self.create_timer(2.0, self.demonstrate_logging)
        self.count = 0

    def demonstrate_logging(self):
        """Show different log levels."""
        self.count += 1

        # DEBUG - detailed diagnostic (hidden by default)
        self.get_logger().debug(f'Debug: Iteration {self.count}, memory ok')

        # INFO - normal operation
        self.get_logger().info(f'Info: Processing iteration {self.count}')

        # Randomly show warnings and errors for demo
        r = random.random()

        if r < 0.3:
            # WARN - unexpected but not critical
            self.get_logger().warn('Warning: Sensor reading slightly off')

        if r < 0.1:
            # ERROR - something failed
            self.get_logger().error('Error: Failed to connect to service (retrying)')

        # FATAL would typically precede a crash
        # self.get_logger().fatal('Fatal: Unrecoverable error!')


def main(args=None):
    rclpy.init(args=args)
    node = NoisyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
