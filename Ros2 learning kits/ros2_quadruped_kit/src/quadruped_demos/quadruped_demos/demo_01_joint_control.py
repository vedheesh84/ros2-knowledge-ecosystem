#!/usr/bin/env python3
"""
Demo 01: Joint Control

LEARNING OBJECTIVES:
- Understanding effort control for joints
- Joint limits and safety
- Basic ros2_control interaction

This demo moves individual joints to verify the control pipeline works.
Run the robot in mock hardware mode first.
"""

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState


class JointControlDemo(Node):
    """Demonstrates basic joint control."""

    def __init__(self):
        super().__init__('demo_01_joint_control')

        self.joint_names = [
            'FL_HAA', 'FL_HFE', 'FL_KFE',
            'FR_HAA', 'FR_HFE', 'FR_KFE',
            'RL_HAA', 'RL_HFE', 'RL_KFE',
            'RR_HAA', 'RR_HFE', 'RR_KFE'
        ]

        # Target positions for standing
        self.stand_positions = {
            'FL_HAA': 0.0, 'FL_HFE': -0.5, 'FL_KFE': 1.0,
            'FR_HAA': 0.0, 'FR_HFE': -0.5, 'FR_KFE': 1.0,
            'RL_HAA': 0.0, 'RL_HFE': -0.5, 'RL_KFE': 1.0,
            'RR_HAA': 0.0, 'RR_HFE': -0.5, 'RR_KFE': 1.0,
        }

        self.current_positions = {name: 0.0 for name in self.joint_names}

        # Subscribe to joint states
        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_callback, 10)

        # Publish to joint targets
        self.target_pub = self.create_publisher(
            Float64MultiArray, '/joint_targets', 10)

        # Demo sequence
        self.phase = 0
        self.phase_time = 0.0
        self.create_timer(0.02, self.demo_loop)

        self.get_logger().info('Demo 01: Joint Control started')
        self.get_logger().info('This demo will move joints through a sequence')

    def joint_callback(self, msg: JointState):
        for i, name in enumerate(msg.name):
            if name in self.current_positions:
                self.current_positions[name] = msg.position[i] if msg.position else 0.0

    def demo_loop(self):
        self.phase_time += 0.02

        # Phase 0: Move to stand position
        if self.phase == 0:
            self.get_logger().info('Phase 0: Moving to stand position...', throttle_duration_sec=2.0)
            targets = [self.stand_positions[name] for name in self.joint_names]
            self.publish_targets(targets)

            if self.phase_time > 3.0:
                self.phase = 1
                self.phase_time = 0.0

        # Phase 1: Wave front left leg
        elif self.phase == 1:
            self.get_logger().info('Phase 1: Waving FL leg...', throttle_duration_sec=2.0)
            targets = [self.stand_positions[name] for name in self.joint_names]
            # Lift FL leg
            wave_angle = 0.3 * np.sin(self.phase_time * 2)
            targets[0] = wave_angle  # FL_HAA
            targets[1] = -0.8  # FL_HFE (lift)
            self.publish_targets(targets)

            if self.phase_time > 5.0:
                self.phase = 2
                self.phase_time = 0.0

        # Phase 2: Return to stand
        elif self.phase == 2:
            self.get_logger().info('Phase 2: Returning to stand...', throttle_duration_sec=2.0)
            targets = [self.stand_positions[name] for name in self.joint_names]
            self.publish_targets(targets)

            if self.phase_time > 2.0:
                self.get_logger().info('Demo complete!')
                self.phase = 3

        # Phase 3: Done
        elif self.phase == 3:
            pass  # Stay in stand position

    def publish_targets(self, targets):
        msg = Float64MultiArray()
        msg.data = targets
        self.target_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = JointControlDemo()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
