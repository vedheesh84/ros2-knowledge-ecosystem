#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Demo 02: Gripper Control
========================

LEARNING OBJECTIVES:
- Understand GripperCommand action interface
- See open/close control patterns
- Learn gripper feedback (position, effort)
- Practice detecting grasp success

KEY CONCEPTS:
- GripperCommand: position + max_effort
- Result includes reached_goal and stalled flags
- Stall detection = grip force hit limit

WATCH FOR:
- position 0.0 = closed, 0.8 = open (for this gripper)
- max_effort limits grip force
- Stall means object is gripped
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import GripperCommand
from sensor_msgs.msg import JointState
import time


class GripperControlDemo(Node):
    def __init__(self):
        super().__init__('demo_02_gripper_control')

        # Action client for gripper
        self.gripper_client = ActionClient(
            self,
            GripperCommand,
            '/gripper_controller/gripper_cmd'
        )

        # Joint state for feedback
        self.gripper_position = 0.0
        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_callback, 10
        )

        self.get_logger().info('Demo 02: Gripper Control initialized')
        self.get_logger().info('Waiting for gripper action server...')

        # Wait for action server
        if not self.gripper_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('Gripper action server not available!')
            return

        # Run demo
        self.create_timer(2.0, self.run_demo)
        self._demo_started = False

    def joint_callback(self, msg: JointState):
        """Track gripper position."""
        if 'left_gear_joint' in msg.name:
            idx = msg.name.index('left_gear_joint')
            self.gripper_position = msg.position[idx]

    def run_demo(self):
        """Execute gripper demo."""
        if self._demo_started:
            return
        self._demo_started = True

        self.get_logger().info('='*50)
        self.get_logger().info('DEMO 02: GRIPPER CONTROL')
        self.get_logger().info('='*50)

        # Demo sequence
        actions = [
            ('Opening gripper', 0.8),
            ('Closing gripper', 0.0),
            ('Half open', 0.4),
            ('Closing with max effort', 0.0),
            ('Opening fully', 0.8),
        ]

        for name, position in actions:
            self.get_logger().info(f'\n{name}...')
            success = self.send_gripper_command(position, max_effort=10.0)

            if success:
                self.get_logger().info(f'  Reached position: {self.gripper_position:.3f}')
            else:
                self.get_logger().warn('  Command failed or stalled')

            time.sleep(1.5)

        self.get_logger().info('\n' + '='*50)
        self.get_logger().info('Demo complete!')
        self.get_logger().info('='*50)

    def send_gripper_command(self, position: float, max_effort: float = 10.0) -> bool:
        """
        Send gripper command and wait for result.

        LEARNING:
        - position: Target gripper opening
        - max_effort: Force limit (stall detection)
        - Returns True if goal reached, False if stalled
        """
        goal = GripperCommand.Goal()
        goal.command.position = position
        goal.command.max_effort = max_effort

        future = self.gripper_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

        if future.result() is None:
            return False

        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected')
            return False

        # Wait for result
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=10.0)

        if result_future.result() is None:
            return False

        result = result_future.result().result
        if result.stalled:
            self.get_logger().info('  Gripper stalled (object gripped?)')
        return result.reached_goal


def main(args=None):
    rclpy.init(args=args)
    node = GripperControlDemo()

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
