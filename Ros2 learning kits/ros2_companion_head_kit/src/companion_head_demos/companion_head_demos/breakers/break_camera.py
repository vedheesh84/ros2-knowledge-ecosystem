#!/usr/bin/env python3
"""
break_camera.py - Camera Failure Injection

LEARNING OBJECTIVES:
====================
1. Vision system robustness testing
2. Graceful degradation without vision
3. Sensor failure detection

FAILURE MODES:
==============
- blackout: Camera returns black frames
- noise: Heavy noise injection
- blur: Gaussian blur (focus issues)
- freeze: Frozen frame (stuck camera)

USAGE:
======
    ros2 run companion_head_demos break_camera --ros-args -p mode:=blackout
    ros2 run companion_head_demos break_camera --ros-args -p mode:=noise -p intensity:=0.8
"""

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class BreakCamera(Node):
    """Injects failures into camera stream."""

    def __init__(self):
        super().__init__('break_camera')

        # Parameters
        self.declare_parameter('mode', 'noise')
        self.declare_parameter('intensity', 0.5)

        self.mode = self.get_parameter('mode').value
        self.intensity = self.get_parameter('intensity').value

        self.bridge = CvBridge()
        self.frozen_frame = None

        # Subscriber
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)

        # Publisher
        self.image_pub = self.create_publisher(Image, '/camera/image_broken', 10)

        self.get_logger().info('='*60)
        self.get_logger().info('BREAKER: Camera Failure Injection')
        self.get_logger().info('='*60)
        self.get_logger().info(f'  Mode: {self.mode}')
        self.get_logger().info(f'  Intensity: {self.intensity}')
        self.get_logger().info('')
        self.get_logger().info('Publishing broken images to /camera/image_broken')
        self.get_logger().info('Remap your face_detector to use this topic to test.')

    def image_callback(self, msg: Image):
        """Apply failure mode and republish."""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'CV Bridge error: {e}')
            return

        # Apply failure mode
        if self.mode == 'blackout':
            cv_image = np.zeros_like(cv_image)

        elif self.mode == 'noise':
            noise = np.random.normal(0, 255 * self.intensity, cv_image.shape)
            cv_image = np.clip(cv_image + noise, 0, 255).astype(np.uint8)

        elif self.mode == 'blur':
            kernel_size = int(50 * self.intensity) | 1  # Must be odd
            cv_image = cv2.GaussianBlur(cv_image, (kernel_size, kernel_size), 0)

        elif self.mode == 'freeze':
            if self.frozen_frame is None:
                self.frozen_frame = cv_image.copy()
            cv_image = self.frozen_frame

        # Publish
        broken_msg = self.bridge.cv2_to_imgmsg(cv_image, 'bgr8')
        broken_msg.header = msg.header
        self.image_pub.publish(broken_msg)


def main(args=None):
    rclpy.init(args=args)
    node = BreakCamera()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
