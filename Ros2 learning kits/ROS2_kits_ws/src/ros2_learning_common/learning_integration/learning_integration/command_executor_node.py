#!/usr/bin/env python3
"""
Command Executor Node - Action Execution Service
=================================================

Provides a service for executing robot commands.
Demonstrates the command pattern in robotics.
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
import time


class CommandExecutorNode(Node):
    """Executes commands via service interface."""

    def __init__(self):
        super().__init__('command_executor')
        self.get_logger().info('Command Executor Node starting...')

        # Service for command execution
        self.service = self.create_service(
            Trigger, '/execute_command', self.execute_callback
        )

        self.execution_count = 0
        self.get_logger().info('Service /execute_command ready')

    def execute_callback(self, request, response):
        """Execute a command."""
        self.execution_count += 1
        self.get_logger().info(f'Executing command #{self.execution_count}')

        # Simulate execution time
        time.sleep(0.5)

        response.success = True
        response.message = f'Command #{self.execution_count} executed successfully'
        return response


def main(args=None):
    rclpy.init(args=args)
    node = CommandExecutorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
