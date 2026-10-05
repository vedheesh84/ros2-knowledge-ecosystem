#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Breaker: Grasp Frame
====================

FAILURE INJECTION:
Modifies detected object poses to simulate grasp planning errors.

FAILURE MODES:
1. z_offset: Grasp point too high/low (misses object)
2. orientation: Wrong gripper approach angle
3. noise: Random jitter in pose (unstable detection)

LEARNING OBJECTIVES:
- See how grasp pose errors cause failures
- Understand approach vector importance
- Practice grasp frame debugging

HOW TO USE:
  # Run perception
  ros2 launch mobile_manipulator_perception perception.launch.py

  # In another terminal, run breaker
  ros2 run mobile_manipulator_demos break_grasp_frame.py --ros-args -p mode:=z_offset

  # Watch grasps fail!

FIX:
  - Stop breaker
  - Check grasp planner parameters
  - Verify tool_frame in URDF
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import random
import math


class GraspFrameBreaker(Node):
    def __init__(self):
        super().__init__('break_grasp_frame')

        # Parameters
        self.declare_parameter('mode', 'z_offset')  # z_offset, orientation, noise
        self.declare_parameter('z_error', 0.05)      # 5cm error
        self.declare_parameter('angle_error', 0.5)   # ~30 degrees
        self.declare_parameter('noise_std', 0.03)    # 3cm noise

        self.mode = self.get_parameter('mode').value
        self.z_error = self.get_parameter('z_error').value
        self.angle_error = self.get_parameter('angle_error').value
        self.noise_std = self.get_parameter('noise_std').value

        # Intercept and modify object poses
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/perception/object_pose',
            self.pose_callback,
            10
        )

        # Republish modified poses
        self.pose_pub = self.create_publisher(
            PoseStamped,
            '/perception/object_pose_broken',
            10
        )

        self.get_logger().warn('='*50)
        self.get_logger().warn('GRASP FRAME BREAKER ACTIVE')
        self.get_logger().warn(f'Mode: {self.mode}')
        self.get_logger().warn('='*50)
        self.get_logger().warn('')
        self.get_logger().warn('Modified poses on: /perception/object_pose_broken')
        self.get_logger().warn('Remap manipulation to use broken topic!')

    def pose_callback(self, msg: PoseStamped):
        """Modify and republish pose."""
        broken = PoseStamped()
        broken.header = msg.header
        broken.pose = msg.pose

        if self.mode == 'z_offset':
            # Grasp point at wrong height
            broken.pose.position.z += self.z_error
            self.get_logger().debug(f'Added Z offset: {self.z_error}')

        elif self.mode == 'orientation':
            # Wrong approach angle
            broken.pose.orientation.x = math.sin(self.angle_error / 2)
            broken.pose.orientation.w = math.cos(self.angle_error / 2)
            self.get_logger().debug(f'Modified orientation')

        elif self.mode == 'noise':
            # Random position jitter
            broken.pose.position.x += random.gauss(0, self.noise_std)
            broken.pose.position.y += random.gauss(0, self.noise_std)
            broken.pose.position.z += random.gauss(0, self.noise_std)
            self.get_logger().debug(f'Added noise')

        self.pose_pub.publish(broken)


def main(args=None):
    rclpy.init(args=args)
    node = GraspFrameBreaker()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Breaker stopped')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
