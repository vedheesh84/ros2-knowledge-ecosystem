#!/usr/bin/env python3
"""
Demo 05: Walking

LEARNING OBJECTIVES:
- Walk gait pattern (one leg at a time)
- Gait scheduling
- Velocity tracking

This demo shows the robot walking at slow speed.
Walk gait is the most stable but slowest gait.
"""

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist


class WalkingDemo(Node):
    """Demonstrates walk gait locomotion."""

    def __init__(self):
        super().__init__('demo_05_walking')

        # Publishers
        self.behavior_pub = self.create_publisher(String, '/behavior/command', 10)
        self.vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Demo parameters
        self.phase = 0
        self.phase_time = 0.0

        self.create_timer(0.02, self.demo_loop)

        self.get_logger().info('Demo 05: Walking started')
        self.get_logger().info('Robot will walk in a square pattern')

    def demo_loop(self):
        self.phase_time += 0.02

        # Send walk command
        cmd = String()
        cmd.data = 'walk'
        self.behavior_pub.publish(cmd)

        vel = Twist()

        # Phase 0: Walk forward
        if self.phase == 0:
            self.get_logger().info('Walking forward...', throttle_duration_sec=2.0)
            vel.linear.x = 0.2
            if self.phase_time > 5.0:
                self.phase = 1
                self.phase_time = 0.0

        # Phase 1: Turn left
        elif self.phase == 1:
            self.get_logger().info('Turning left...', throttle_duration_sec=2.0)
            vel.angular.z = 0.3
            if self.phase_time > 3.0:
                self.phase = 2
                self.phase_time = 0.0

        # Phase 2: Walk forward
        elif self.phase == 2:
            self.get_logger().info('Walking forward...', throttle_duration_sec=2.0)
            vel.linear.x = 0.2
            if self.phase_time > 5.0:
                self.phase = 3
                self.phase_time = 0.0

        # Phase 3: Stop
        elif self.phase == 3:
            self.get_logger().info('Demo complete! Stopping...', throttle_duration_sec=2.0)
            # Zero velocity

        self.vel_pub.publish(vel)


def main(args=None):
    rclpy.init(args=args)
    node = WalkingDemo()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
