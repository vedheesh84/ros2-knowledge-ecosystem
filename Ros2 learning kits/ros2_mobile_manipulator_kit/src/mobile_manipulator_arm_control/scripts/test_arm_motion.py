#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Test Arm Motion - Simple MoveIt2 Demo
======================================

LEARNING OBJECTIVES:
- See ArmInterface usage
- Test arm motion patterns
- Verify MoveIt2 setup

USAGE:
    ros2 run mobile_manipulator_arm_control test_arm_motion.py
"""

import rclpy
from rclpy.node import Node
from mobile_manipulator_arm_control import ArmInterface
import time


class TestArmMotion(Node):
    def __init__(self):
        super().__init__('test_arm_motion')
        self.arm = ArmInterface(self)
        self.get_logger().info('Test arm motion node started')

        # Run test sequence after short delay
        self.create_timer(2.0, self.run_test_sequence)
        self._test_done = False

    def run_test_sequence(self):
        if self._test_done:
            return
        self._test_done = True

        self.get_logger().info('=== Starting arm test sequence ===')

        # Test 1: Get current joint values
        self.get_logger().info('Test 1: Reading current joint values')
        joints = self.arm.get_current_joint_values()
        if joints:
            self.get_logger().info(f'Current joints: {joints}')
        else:
            self.get_logger().warn('No joint values available')

        # Test 2: Named poses
        self.get_logger().info('Test 2: Moving to named poses')

        self.get_logger().info('Going to HOME...')
        self.arm.go_to_named_pose('home')
        time.sleep(2.0)

        self.get_logger().info('Going to READY...')
        self.arm.go_to_named_pose('ready')
        time.sleep(2.0)

        self.get_logger().info('Going to EXTENDED...')
        self.arm.go_to_named_pose('extended')
        time.sleep(2.0)

        # Test 3: Gripper
        self.get_logger().info('Test 3: Gripper control')

        self.get_logger().info('Opening gripper...')
        self.arm.open_gripper()
        time.sleep(1.0)

        self.get_logger().info('Closing gripper...')
        self.arm.close_gripper()
        time.sleep(1.0)

        # Test 4: Return home
        self.get_logger().info('Test 4: Return to home')
        self.arm.go_to_named_pose('home')

        self.get_logger().info('=== Test sequence complete ===')


def main(args=None):
    rclpy.init(args=args)
    node = TestArmMotion()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
