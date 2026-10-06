#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Static Pick-Place Demo
=======================

LEARNING OBJECTIVES:
- See simple pick-place without perception
- Understand hard-coded pose sequences
- Learn motion timing and delays
- Practice basic manipulation flow

This demo picks from a fixed location and places at another.
Good for initial testing before adding perception.

USAGE:
  ros2 run mobile_manipulator_manipulation static_pick_place.py
"""

import rclpy
from rclpy.node import Node
import time


class StaticPickPlaceDemo(Node):
    """
    Simple pick-place with hard-coded poses.

    LEARNING: Start with fixed poses to verify:
    - Arm reaches expected positions
    - Gripper opens/closes correctly
    - Timing is appropriate
    """

    def __init__(self):
        super().__init__('static_pick_place_demo')

        # Hard-coded poses (in arm_base_link frame)
        # Adjust these for your setup!
        self.pick_pose = {'x': 0.25, 'y': 0.0, 'z': 0.05}
        self.place_pose = {'x': 0.25, 'y': 0.15, 'z': 0.05}
        self.safe_z = 0.15  # Safe height for transit

        self.get_logger().info('Static pick-place demo initialized')
        self.get_logger().info(f'Pick: {self.pick_pose}')
        self.get_logger().info(f'Place: {self.place_pose}')

        # Run demo after short delay
        self.create_timer(2.0, self._run_demo_once)
        self._demo_done = False

    def _run_demo_once(self):
        """Execute pick-place sequence once."""
        if self._demo_done:
            return
        self._demo_done = True

        self.get_logger().info('=== Starting static pick-place demo ===')

        try:
            # 1. Go to safe height above pick
            self._log_step('Moving to safe height above pick')
            self._move_to(self.pick_pose['x'], self.pick_pose['y'], self.safe_z)

            # 2. Open gripper
            self._log_step('Opening gripper')
            self._gripper_open()

            # 3. Move down to pick
            self._log_step('Moving down to pick position')
            self._move_to(**self.pick_pose)

            # 4. Close gripper
            self._log_step('Closing gripper (grasping)')
            self._gripper_close()

            # 5. Lift object
            self._log_step('Lifting object')
            self._move_to(self.pick_pose['x'], self.pick_pose['y'], self.safe_z)

            # 6. Move to above place
            self._log_step('Moving to place location')
            self._move_to(self.place_pose['x'], self.place_pose['y'], self.safe_z)

            # 7. Lower to place
            self._log_step('Lowering to place')
            self._move_to(**self.place_pose)

            # 8. Open gripper
            self._log_step('Opening gripper (releasing)')
            self._gripper_open()

            # 9. Retract
            self._log_step('Retracting')
            self._move_to(self.place_pose['x'], self.place_pose['y'], self.safe_z)

            self.get_logger().info('=== Demo complete! ===')

        except Exception as e:
            self.get_logger().error(f'Demo failed: {e}')

    def _log_step(self, message: str):
        """Log step with delay."""
        self.get_logger().info(f'Step: {message}')
        time.sleep(0.5)

    def _move_to(self, x: float, y: float, z: float):
        """
        Move arm to position.

        TODO: Replace with actual MoveIt call!
        """
        self.get_logger().info(f'  → Move to ({x:.3f}, {y:.3f}, {z:.3f})')
        time.sleep(1.0)  # Simulate motion time

    def _gripper_open(self):
        """
        Open gripper.

        TODO: Replace with actual gripper action!
        """
        self.get_logger().info('  → Gripper OPEN')
        time.sleep(0.5)

    def _gripper_close(self):
        """
        Close gripper.

        TODO: Replace with actual gripper action!
        """
        self.get_logger().info('  → Gripper CLOSE')
        time.sleep(0.5)


def main(args=None):
    rclpy.init(args=args)
    node = StaticPickPlaceDemo()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
