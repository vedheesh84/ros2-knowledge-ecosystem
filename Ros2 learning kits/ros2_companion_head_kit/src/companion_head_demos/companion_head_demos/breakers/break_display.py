#!/usr/bin/env python3
"""
break_display.py - Display Failure Injection

LEARNING OBJECTIVES:
====================
1. Expression degradation handling
2. Visual feedback alternatives
3. Display fault detection

FAILURE MODES:
==============
- freeze: Display stuck on frame
- glitch: Random visual artifacts
- lag: Delayed expression updates
- blank: Display goes blank

USAGE:
======
    ros2 run companion_head_demos break_display --ros-args -p mode:=glitch
"""

import cv2
import numpy as np
import random
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class BreakDisplay(Node):
    """Injects failures into face display."""

    def __init__(self):
        super().__init__('break_display')

        # Parameters
        self.declare_parameter('mode', 'glitch')
        self.declare_parameter('intensity', 0.5)

        self.mode = self.get_parameter('mode').value
        self.intensity = self.get_parameter('intensity').value

        self.bridge = CvBridge()
        self.frozen_frame = None
        self.frame_buffer = []
        self.lag_frames = int(30 * self.intensity)  # Up to 1 second lag

        # Subscriber
        self.image_sub = self.create_subscription(
            Image, '/face/display', self.image_callback, 10)

        # Publisher
        self.image_pub = self.create_publisher(Image, '/face/display_broken', 10)

        self.get_logger().info('='*60)
        self.get_logger().info('BREAKER: Display Failure Injection')
        self.get_logger().info('='*60)
        self.get_logger().info(f'  Mode: {self.mode}')
        self.get_logger().info(f'  Intensity: {self.intensity}')
        self.get_logger().info('')
        self.get_logger().info('Publishing broken display to /face/display_broken')

    def image_callback(self, msg: Image):
        """Apply failure mode to display."""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'CV Bridge error: {e}')
            return

        if self.mode == 'freeze':
            if self.frozen_frame is None:
                self.frozen_frame = cv_image.copy()
            cv_image = self.frozen_frame

        elif self.mode == 'glitch':
            # Random pixel displacement
            if random.random() < self.intensity:
                h, w = cv_image.shape[:2]
                for _ in range(int(20 * self.intensity)):
                    x1, y1 = random.randint(0, w-20), random.randint(0, h-20)
                    x2, y2 = random.randint(0, w-20), random.randint(0, h-20)
                    block = cv_image[y1:y1+10, x1:x1+10].copy()
                    cv_image[y2:y2+10, x2:x2+10] = block

        elif self.mode == 'lag':
            self.frame_buffer.append(cv_image.copy())
            if len(self.frame_buffer) > self.lag_frames:
                cv_image = self.frame_buffer.pop(0)
            else:
                cv_image = self.frame_buffer[0]

        elif self.mode == 'blank':
            if random.random() < self.intensity:
                cv_image = np.zeros_like(cv_image)
                self.get_logger().warn('[BREAK] Display blank!')

        # Publish
        broken_msg = self.bridge.cv2_to_imgmsg(cv_image, 'bgr8')
        broken_msg.header = msg.header
        self.image_pub.publish(broken_msg)


def main(args=None):
    rclpy.init(args=args)
    node = BreakDisplay()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
