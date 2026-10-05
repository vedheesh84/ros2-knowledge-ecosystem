#!/usr/bin/env python3
"""
Lifecycle Sensor Node - Managed State Transitions
==================================================

LEARNING OBJECTIVES:
--------------------
1. Understand lifecycle node states (unconfigured, inactive, active, finalized)
2. Implement transition callbacks (on_configure, on_activate, etc.)
3. Learn why deterministic startup matters for robots

LIFECYCLE STATES:
-----------------
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    LIFECYCLE STATE MACHINE                              │
    │                                                                         │
    │   ┌──────────────┐                                                      │
    │   │ unconfigured │ ──configure──▶ ┌────────────┐                       │
    │   └──────────────┘                │  inactive  │                       │
    │          ▲                        └────────────┘                       │
    │          │                              │                               │
    │       cleanup                      activate                             │
    │          │                              │                               │
    │          │                              ▼                               │
    │   ┌──────────────┐                ┌────────────┐                       │
    │   │  finalized   │ ◀──shutdown──  │   active   │                       │
    │   └──────────────┘                └────────────┘                       │
    │                                         │                               │
    │                                    deactivate                           │
    │                                         ▼                               │
    │                                   back to inactive                      │
    └─────────────────────────────────────────────────────────────────────────┘

USAGE:
------
    # Start the node
    ros2 run learning_lifecycle lifecycle_sensor_node

    # Transition via CLI
    ros2 lifecycle set /lifecycle_sensor configure
    ros2 lifecycle set /lifecycle_sensor activate
    ros2 lifecycle set /lifecycle_sensor deactivate
    ros2 lifecycle set /lifecycle_sensor cleanup
"""

import rclpy
from rclpy.lifecycle import Node as LifecycleNode
from rclpy.lifecycle import State, TransitionCallbackReturn
from std_msgs.msg import String
import random


class LifecycleSensorNode(LifecycleNode):
    """A sensor node with managed lifecycle states."""

    def __init__(self):
        super().__init__('lifecycle_sensor')
        self.get_logger().info('Lifecycle Sensor Node created (UNCONFIGURED)')
        self.publisher = None
        self.timer = None

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        """Configure transition: Set up resources."""
        self.get_logger().info('on_configure() called - Setting up publisher')
        self.publisher = self.create_publisher(String, '/sensor_data', 10)
        self.get_logger().info('Configured! Now in INACTIVE state.')
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        """Activate transition: Start publishing."""
        self.get_logger().info('on_activate() called - Starting sensor')
        self.timer = self.create_timer(1.0, self.publish_sensor_data)
        self.get_logger().info('Activated! Now publishing sensor data.')
        return TransitionCallbackReturn.SUCCESS

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        """Deactivate transition: Stop publishing but keep resources."""
        self.get_logger().info('on_deactivate() called - Stopping sensor')
        if self.timer:
            self.timer.cancel()
        self.get_logger().info('Deactivated! Back to INACTIVE state.')
        return TransitionCallbackReturn.SUCCESS

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        """Cleanup transition: Release resources."""
        self.get_logger().info('on_cleanup() called - Releasing resources')
        self.publisher = None
        self.timer = None
        self.get_logger().info('Cleaned up! Back to UNCONFIGURED state.')
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        """Shutdown transition: Final cleanup."""
        self.get_logger().info('on_shutdown() called - Shutting down')
        return TransitionCallbackReturn.SUCCESS

    def publish_sensor_data(self):
        """Publish simulated sensor data (only when ACTIVE)."""
        msg = String()
        msg.data = f'Sensor reading: {random.uniform(0, 100):.2f}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Published: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = LifecycleSensorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
