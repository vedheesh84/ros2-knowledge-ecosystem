#!/usr/bin/env python3
"""
Demo 07: Full Companion Behavior

LEARNING OBJECTIVES:
====================
1. Complete behavior state machine
2. End-to-end interaction flow
3. System integration

BEHAVIOR FLOW:
==============
    IDLE ──► GREETING ──► TRACKING ──► LISTENING ──► RESPONDING ──► IDLE
         face      done     wake word    speech       done
         detected

WHAT THIS DEMO DOES:
====================
1. Run the full behavior controller
2. Show complete interaction cycle
3. Demonstrate all subsystems working together

TRY THIS:
=========
- Stand in front of camera → greeting
- Say wake word → listening mode
- Speak → see response
- Wait → watch sleepy behavior

PREREQUISITE:
=============
    Full system launch:
    ros2 launch companion_head_bringup simulation.launch.py

    Or manually run all nodes.
"""

import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class FullCompanionDemo(Node):
    """Demo that shows complete companion behavior."""

    def __init__(self):
        super().__init__('demo_07_full_companion')

        self.current_state = 'UNKNOWN'

        # Subscribe to behavior state
        self.state_sub = self.create_subscription(
            String, '/behavior/state', self.state_callback, 10)

        self.get_logger().info('='*60)
        self.get_logger().info('DEMO 07: FULL COMPANION BEHAVIOR')
        self.get_logger().info('='*60)
        self.get_logger().info('')
        self.get_logger().info('This is the complete companion behavior demo.')
        self.get_logger().info('')
        self.get_logger().info('Required: Full system running')
        self.get_logger().info('  ros2 launch companion_head_bringup simulation.launch.py')
        self.get_logger().info('')
        self.get_logger().info('Behavior States:')
        self.get_logger().info('  IDLE      - Waiting, subtle animations')
        self.get_logger().info('  GREETING  - Face detected, saying hello')
        self.get_logger().info('  TRACKING  - Following user with gaze')
        self.get_logger().info('  LISTENING - Wake word activated, waiting for speech')
        self.get_logger().info('  RESPONDING - Processing and responding')
        self.get_logger().info('  SLEEPING  - Long idle, drowsy behavior')
        self.get_logger().info('')
        self.get_logger().info('Watching behavior state...')
        self.get_logger().info('')

    def state_callback(self, msg: String):
        """Display behavior state changes."""
        state = msg.data

        if state != self.current_state:
            self.current_state = state

            # State descriptions
            descriptions = {
                'IDLE': 'Robot is waiting for interaction...',
                'GREETING': 'Hello! Robot detected you and is greeting!',
                'TRACKING': 'Robot is tracking your face with its gaze.',
                'LISTENING': 'Listening... Say something!',
                'RESPONDING': 'Processing your input and responding...',
                'SLEEPING': 'Zzz... Robot is sleepy (long idle time)',
            }

            desc = descriptions.get(state, '')
            self.get_logger().info('')
            self.get_logger().info(f'[STATE] {state}')
            self.get_logger().info(f'        {desc}')


def main(args=None):
    rclpy.init(args=args)
    node = FullCompanionDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
