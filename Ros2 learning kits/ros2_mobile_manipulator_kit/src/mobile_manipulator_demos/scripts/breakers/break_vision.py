#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Breaker: Vision Failures
========================

FAILURE INJECTION:
Simulates common computer vision detection problems.

FAILURE MODES:
1. phantom: Publish fake detections (no real object)
2. noise: Add significant noise to positions
3. dropout: Randomly drop detections
4. duplicate: Publish multiple conflicting detections

LEARNING OBJECTIVES:
- See how vision noise affects manipulation
- Understand need for detection filtering
- Practice handling phantom detections

HOW TO USE:
  # Instead of real perception
  ros2 run mobile_manipulator_demos break_vision.py --ros-args -p mode:=phantom

  # Watch manipulation chase phantom objects!

COMMON VISION ISSUES:
1. Lighting changes → color detection fails
2. Occlusion → partial detection
3. Reflections → phantom detections
4. Camera shake → position jitter
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import random
import math


class VisionBreaker(Node):
    def __init__(self):
        super().__init__('break_vision')

        # Parameters
        self.declare_parameter('mode', 'phantom')
        self.declare_parameter('noise_std', 0.05)  # 5cm noise
        self.declare_parameter('dropout_rate', 0.5)  # 50% dropout

        self.mode = self.get_parameter('mode').value
        self.noise_std = self.get_parameter('noise_std').value
        self.dropout_rate = self.get_parameter('dropout_rate').value

        # Publisher
        self.pose_pub = self.create_publisher(
            PoseStamped,
            '/perception/object_pose',
            10
        )

        self.get_logger().warn('='*50)
        self.get_logger().warn('VISION BREAKER ACTIVE')
        self.get_logger().warn(f'Mode: {self.mode}')
        self.get_logger().warn('='*50)

        # Publish at 5Hz
        self.create_timer(0.2, self.publish_broken_detection)

        self.frame_count = 0

    def publish_broken_detection(self):
        """Publish broken detection."""
        self.frame_count += 1

        if self.mode == 'phantom':
            # Fake object at random position in workspace
            self.publish_detection(
                x=random.uniform(0.15, 0.35),
                y=random.uniform(-0.15, 0.15),
                z=random.uniform(0.02, 0.10),
            )
            if self.frame_count % 10 == 0:
                self.get_logger().warn('Publishing phantom detection')

        elif self.mode == 'noise':
            # Real-ish position with lots of noise
            base_x, base_y, base_z = 0.25, 0.0, 0.05
            self.publish_detection(
                x=base_x + random.gauss(0, self.noise_std),
                y=base_y + random.gauss(0, self.noise_std),
                z=base_z + random.gauss(0, self.noise_std),
            )

        elif self.mode == 'dropout':
            # Random detection dropout
            if random.random() > self.dropout_rate:
                self.publish_detection(x=0.25, y=0.0, z=0.05)
            else:
                if self.frame_count % 10 == 0:
                    self.get_logger().warn('Detection dropped!')

        elif self.mode == 'duplicate':
            # Multiple conflicting detections
            self.publish_detection(x=0.20, y=-0.05, z=0.05)
            self.publish_detection(x=0.30, y=0.05, z=0.05)
            if self.frame_count % 20 == 0:
                self.get_logger().warn('Publishing duplicate detections')

    def publish_detection(self, x: float, y: float, z: float):
        """Publish single detection."""
        pose = PoseStamped()
        pose.header.frame_id = 'arm_base_link'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z
        pose.pose.orientation.w = 1.0

        self.pose_pub.publish(pose)


def main(args=None):
    rclpy.init(args=args)
    node = VisionBreaker()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Breaker stopped')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
