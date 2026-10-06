#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Demo 06: Mobile Pick-Place
==========================

LEARNING OBJECTIVES:
- See navigation + manipulation coordination
- Understand when to stow arm for driving
- Learn base positioning for reach
- Practice full system integration

EXTENDED PIPELINE:
  Nav2 Goal → Navigate → Position Check → Perception →
  State Machine → Arm Control → Navigate to Place → Done

KEY CHALLENGES:
- Arm must be stowed during navigation
- Robot must position for arm reach
- TF changes as robot moves
- Timing between subsystems

WATCH FOR:
- Navigation goal tolerance affects arm reach
- EKF drift during manipulation
- Object may shift during pickup
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient


class MobilePickPlaceDemo(Node):
    def __init__(self):
        super().__init__('demo_06_mobile_pick_place')

        # Navigation action client
        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            '/navigate_to_pose'
        )

        # Manipulation command
        self.cmd_pub = self.create_publisher(
            String, '/manipulation/command', 10
        )

        # State tracking
        self.state_sub = self.create_subscription(
            String, '/manipulation/state', self.state_callback, 10
        )

        self.current_state = 'IDLE'
        self.get_logger().info('Demo 06: Mobile Pick-Place initialized')
        self.get_logger().info('')
        self.get_logger().info('='*50)
        self.get_logger().info('MOBILE PICK-PLACE DEMO')
        self.get_logger().info('='*50)
        self.get_logger().info('')
        self.get_logger().info('This demo coordinates:')
        self.get_logger().info('  1. Navigation to pick location')
        self.get_logger().info('  2. Object detection and pick')
        self.get_logger().info('  3. Navigation to place location')
        self.get_logger().info('  4. Object placement')
        self.get_logger().info('')
        self.get_logger().info('Prerequisites:')
        self.get_logger().info('  - Full system bringup with Nav2')
        self.get_logger().info('  - SLAM or localization active')
        self.get_logger().info('  - Perception and manipulation nodes')
        self.get_logger().info('')

        # Demo locations (adjust for your map!)
        self.pick_location = {'x': 1.0, 'y': 0.0, 'yaw': 0.0}
        self.place_location = {'x': 1.0, 'y': 1.0, 'yaw': 0.0}

        # Run after delay
        self.create_timer(5.0, self.run_demo)
        self._demo_started = False

    def state_callback(self, msg: String):
        """Track manipulation state."""
        self.current_state = msg.data

    def run_demo(self):
        """Execute mobile pick-place demo."""
        if self._demo_started:
            return
        self._demo_started = True

        self.get_logger().info('Starting mobile pick-place sequence...')

        # Check Nav2 availability
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Nav2 not available!')
            self.get_logger().info('Run: ros2 launch nav2_bringup navigation_launch.py')
            return

        # Step 1: Navigate to pick location
        self.get_logger().info('')
        self.get_logger().info('Step 1: Navigating to pick location...')
        self.get_logger().info(f'  Target: {self.pick_location}')

        success = self.navigate_to(
            self.pick_location['x'],
            self.pick_location['y'],
            self.pick_location['yaw']
        )

        if not success:
            self.get_logger().error('Navigation to pick failed!')
            return

        # Step 2: Pick object
        self.get_logger().info('')
        self.get_logger().info('Step 2: Picking object...')

        cmd = String()
        cmd.data = 'start'
        self.cmd_pub.publish(cmd)

        # Wait for pick to complete
        import time
        timeout = 30.0
        start = time.time()
        while time.time() - start < timeout:
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.current_state == 'IDLE':
                break
            if self.current_state == 'ERROR':
                self.get_logger().error('Pick failed!')
                return

        # Step 3: Navigate to place
        self.get_logger().info('')
        self.get_logger().info('Step 3: Navigating to place location...')

        success = self.navigate_to(
            self.place_location['x'],
            self.place_location['y'],
            self.place_location['yaw']
        )

        if not success:
            self.get_logger().error('Navigation to place failed!')
            return

        self.get_logger().info('')
        self.get_logger().info('='*50)
        self.get_logger().info('Mobile pick-place complete!')
        self.get_logger().info('='*50)

    def navigate_to(self, x: float, y: float, yaw: float) -> bool:
        """Navigate to pose."""
        import math

        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(yaw / 2)
        goal.pose.pose.orientation.w = math.cos(yaw / 2)

        future = self.nav_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)

        if future.result() is None:
            return False

        goal_handle = future.result()
        if not goal_handle.accepted:
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=60.0)

        return result_future.result() is not None


def main(args=None):
    rclpy.init(args=args)
    node = MobilePickPlaceDemo()

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
