#!/usr/bin/env python3
"""
Demo 07: Autonomous Survey Mission

LEARNING OBJECTIVES:
====================
1. Understand mission state machines
2. See complete autonomous behavior
3. Learn survey pattern execution

WHAT THIS DEMO DOES:
====================
1. Executes a complete survey mission:
   - Descend to operating depth
   - Execute lawnmower survey pattern
   - Return and surface
2. Demonstrates full system integration

MISSION PHASES:
===============
IDLE     → Waiting for start command
DESCEND  → Diving to survey depth
NAVIGATE → Following survey waypoints
SURVEY   → Executing pattern
SURFACE  → Returning to surface
COMPLETE → Mission done

LAWNMOWER PATTERN:
==================
    Start →→→→→→→→→→
                    ↓
    ←←←←←←←←←←←←←←←←
    ↓
    →→→→→→→→→→→→→→→→
                    ↓
    ←←←←←←←←←←← End
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Demo07SurveyMission(Node):
    """Demo 07: Execute autonomous survey mission."""

    def __init__(self):
        super().__init__('demo_07_survey_mission')

        self.mission_cmd_pub = self.create_publisher(
            String, '/mission/command', 10)
        self.mission_status_sub = self.create_subscription(
            String, '/mission/status', self.status_callback, 10)

        self.get_logger().info('=== Demo 07: Autonomous Survey Mission ===')
        self.get_logger().info('')
        self.get_logger().info('This demo executes a complete survey mission:')
        self.get_logger().info('  1. Descend to 10m')
        self.get_logger().info('  2. Execute lawnmower survey')
        self.get_logger().info('  3. Return and surface')
        self.get_logger().info('')
        self.get_logger().info('Starting mission in 5 seconds...')

        # Start mission after delay
        self.create_timer(5.0, self.start_mission)
        self.mission_started = False

    def start_mission(self):
        """Send mission start command."""
        if not self.mission_started:
            self.get_logger().info('>>> Starting mission!')
            msg = String()
            msg.data = 'start_demo'
            self.mission_cmd_pub.publish(msg)
            self.mission_started = True

    def status_callback(self, msg: String):
        """Log mission status updates."""
        self.get_logger().info(f'Mission status: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = Demo07SurveyMission()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
