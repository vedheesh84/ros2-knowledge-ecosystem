#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Breaker: Controller Conflicts
=============================

FAILURE INJECTION:
Creates controller configuration issues common in ros2_control.

FAILURE MODES:
1. duplicate: Load controller that claims same joints
2. wrong_joints: Load controller with non-existent joints
3. unload: Unload active controller

LEARNING OBJECTIVES:
- Understand controller conflicts
- See ros2_control error messages
- Practice controller debugging

HOW TO USE:
  # System running with controllers
  ros2 launch mobile_manipulator_bringup simulation.launch.py

  # Break it
  ros2 run mobile_manipulator_demos break_controller.py --ros-args -p mode:=unload

DEBUGGING:
  ros2 control list_controllers
  ros2 control list_hardware_interfaces

FIX:
  - Restart controller_manager
  - Or re-spawn the unloaded controller
"""

import rclpy
from rclpy.node import Node
from controller_manager_msgs.srv import (
    LoadController,
    UnloadController,
    ConfigureController,
)
import subprocess


class ControllerBreaker(Node):
    def __init__(self):
        super().__init__('break_controller')

        # Parameters
        self.declare_parameter('mode', 'unload')  # unload, wrong_joints

        self.mode = self.get_parameter('mode').value

        self.get_logger().warn('='*50)
        self.get_logger().warn('CONTROLLER BREAKER')
        self.get_logger().warn(f'Mode: {self.mode}')
        self.get_logger().warn('='*50)

        # Execute after delay
        self.create_timer(2.0, self.break_controllers)
        self._done = False

    def break_controllers(self):
        """Execute controller breaking."""
        if self._done:
            return
        self._done = True

        if self.mode == 'unload':
            self.get_logger().warn('Unloading arm_controller...')
            self.get_logger().warn('This will stop arm trajectory execution!')

            try:
                result = subprocess.run([
                    'ros2', 'control', 'unload_controller', 'arm_controller'
                ], capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    self.get_logger().error('arm_controller unloaded!')
                    self.get_logger().info('')
                    self.get_logger().info('TO FIX: ros2 control load_controller arm_controller')
                    self.get_logger().info('        ros2 control set_controller_state arm_controller active')
                else:
                    self.get_logger().warn(f'Unload failed: {result.stderr}')

            except Exception as e:
                self.get_logger().error(f'Error: {e}')

        elif self.mode == 'wrong_joints':
            self.get_logger().warn('Attempting to load controller with wrong joints...')
            self.get_logger().warn('This should fail with clear error message')

            # This would require creating a temporary config file
            # For now just show the concept
            self.get_logger().info('')
            self.get_logger().info('Common controller config mistakes:')
            self.get_logger().info('  1. Joint name typo (joint1 vs joint_1)')
            self.get_logger().info('  2. Missing joint in URDF')
            self.get_logger().info('  3. Wrong interface type (velocity vs position)')
            self.get_logger().info('  4. Duplicate joint claims')

        self.get_logger().info('')
        self.get_logger().info('Check controller status:')
        self.get_logger().info('  ros2 control list_controllers')
        self.get_logger().info('  ros2 control list_hardware_interfaces')


def main(args=None):
    rclpy.init(args=args)
    node = ControllerBreaker()

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
