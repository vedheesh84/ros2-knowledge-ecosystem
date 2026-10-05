#!/usr/bin/env python3
"""
Lifecycle Controller Node - Managing Other Nodes' Lifecycles
=============================================================

LEARNING OBJECTIVES:
--------------------
1. How to manage lifecycle nodes externally
2. Using lifecycle service clients
3. Orchestrating multi-node startup sequences

This node demonstrates CONTROLLING another lifecycle node's state transitions.
"""

import rclpy
from rclpy.node import Node
from lifecycle_msgs.srv import ChangeState, GetState
from lifecycle_msgs.msg import Transition
import time


class LifecycleControllerNode(Node):
    """A node that controls lifecycle of other nodes."""

    def __init__(self):
        super().__init__('lifecycle_controller')
        self.get_logger().info('Lifecycle Controller starting...')

        # Create clients for the lifecycle sensor node
        self.change_state_client = self.create_client(
            ChangeState, '/lifecycle_sensor/change_state'
        )
        self.get_state_client = self.create_client(
            GetState, '/lifecycle_sensor/get_state'
        )

        self.get_logger().info('Waiting for lifecycle_sensor node...')

        if not self.change_state_client.wait_for_service(timeout_sec=10.0):
            self.get_logger().error('Lifecycle sensor not available!')
            return

        self.get_logger().info('Connected! Starting lifecycle demo...')
        self.run_lifecycle_demo()

    def change_state(self, transition_id: int, label: str):
        """Request a state transition."""
        request = ChangeState.Request()
        request.transition.id = transition_id

        self.get_logger().info(f'Requesting transition: {label}')
        future = self.change_state_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

        if future.result() and future.result().success:
            self.get_logger().info(f'Transition {label} succeeded!')
            return True
        else:
            self.get_logger().error(f'Transition {label} failed!')
            return False

    def run_lifecycle_demo(self):
        """Demonstrate lifecycle transitions."""
        self.get_logger().info('=' * 50)
        self.get_logger().info('LIFECYCLE DEMO')
        self.get_logger().info('=' * 50)

        # Configure
        self.get_logger().info('\n--- Step 1: Configure ---')
        self.change_state(Transition.TRANSITION_CONFIGURE, 'CONFIGURE')
        time.sleep(2)

        # Activate
        self.get_logger().info('\n--- Step 2: Activate ---')
        self.change_state(Transition.TRANSITION_ACTIVATE, 'ACTIVATE')
        time.sleep(5)  # Let it run for 5 seconds

        # Deactivate
        self.get_logger().info('\n--- Step 3: Deactivate ---')
        self.change_state(Transition.TRANSITION_DEACTIVATE, 'DEACTIVATE')
        time.sleep(2)

        # Cleanup
        self.get_logger().info('\n--- Step 4: Cleanup ---')
        self.change_state(Transition.TRANSITION_CLEANUP, 'CLEANUP')

        self.get_logger().info('\nDemo complete!')


def main(args=None):
    rclpy.init(args=args)
    try:
        node = LifecycleControllerNode()
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
