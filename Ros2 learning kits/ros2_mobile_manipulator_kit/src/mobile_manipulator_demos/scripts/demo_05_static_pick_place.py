#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Demo 05: Static Pick-Place
==========================

LEARNING OBJECTIVES:
- See full manipulation pipeline in action
- Understand state machine coordination
- Learn perception → manipulation flow
- Practice debugging pick failures

PIPELINE:
  Camera → Perception → State Machine → Arm Control
           (detect)      (coordinate)    (execute)

STATE MACHINE STATES:
  IDLE → DETECTING → PRE_GRASP → GRASPING →
  POST_GRASP → TRANSPORTING → PRE_PLACE → PLACING → RETRACTING → IDLE

WATCH FOR:
- /manipulation/state shows current state
- /manipulation/status shows status messages
- Watch for DETECTING timeout if no object
- Watch for PRE_GRASP failures (IK issues)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class StaticPickPlaceDemo(Node):
    def __init__(self):
        super().__init__('demo_05_static_pick_place')

        # Command publisher
        self.cmd_pub = self.create_publisher(
            String, '/manipulation/command', 10
        )

        # State subscriber
        self.state_sub = self.create_subscription(
            String, '/manipulation/state', self.state_callback, 10
        )
        self.status_sub = self.create_subscription(
            String, '/manipulation/status', self.status_callback, 10
        )

        self.current_state = 'UNKNOWN'
        self.get_logger().info('Demo 05: Static Pick-Place initialized')
        self.get_logger().info('')
        self.get_logger().info('='*50)
        self.get_logger().info('STATIC PICK-PLACE DEMO')
        self.get_logger().info('='*50)
        self.get_logger().info('')
        self.get_logger().info('Prerequisites:')
        self.get_logger().info('  1. Robot bringup running (controllers active)')
        self.get_logger().info('  2. Perception node running')
        self.get_logger().info('  3. Manipulation node running')
        self.get_logger().info('  4. Object placed in camera view')
        self.get_logger().info('')
        self.get_logger().info('Commands:')
        self.get_logger().info('  start - Begin pick-place cycle')
        self.get_logger().info('  stop  - Stop and return to IDLE')
        self.get_logger().info('  reset - Reset from ERROR state')
        self.get_logger().info('')

        # Run demo after delay
        self.create_timer(3.0, self.start_demo)
        self._started = False

    def state_callback(self, msg: String):
        """Track state changes."""
        if msg.data != self.current_state:
            self.current_state = msg.data
            self.get_logger().info(f'State: {self.current_state}')

    def status_callback(self, msg: String):
        """Show status messages."""
        self.get_logger().info(f'Status: {msg.data}')

    def start_demo(self):
        """Send start command."""
        if self._started:
            return
        self._started = True

        self.get_logger().info('')
        self.get_logger().info('Sending START command...')
        self.get_logger().info('')

        cmd = String()
        cmd.data = 'start'
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = StaticPickPlaceDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
