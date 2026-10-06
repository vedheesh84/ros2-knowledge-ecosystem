#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Perception Node - Main Perception Pipeline
==========================================

LEARNING OBJECTIVES:
- See complete perception pipeline
- Understand ROS2 image handling
- Learn detection → pose → TF workflow
- Practice publishing object poses

PIPELINE:
1. Subscribe to /camera/image_raw
2. Run object detection (color/shape)
3. Estimate 3D pose from 2D detection
4. Transform to arm_base_link frame
5. Publish as PoseStamped

TOPICS:
  Subscribe:
    - /camera/image_raw: Input images
    - /camera/camera_info: Camera intrinsics

  Publish:
    - /perception/detections: Detection image
    - /perception/object_pose: Object pose for manipulation
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped, TransformStamped
from std_msgs.msg import Header
from cv_bridge import CvBridge

import tf2_ros
import tf2_geometry_msgs

from mobile_manipulator_perception.object_detector import ObjectDetector, Detection
from mobile_manipulator_perception.pose_estimator import (
    PoseEstimator, CameraInfo as CamInfo, create_default_camera_info
)

from typing import Optional
import numpy as np


class PerceptionNode(Node):
    """
    Main perception pipeline node.

    LEARNING OBJECTIVES:
    - Combines detection and pose estimation
    - Handles camera calibration
    - Publishes poses for manipulation
    """

    def __init__(self):
        super().__init__('perception_node')

        # Parameters
        self.declare_parameter('target_color', 'red')
        self.declare_parameter('object_width', 0.05)  # 5cm
        self.declare_parameter('detection_rate', 10.0)
        self.declare_parameter('target_frame', 'arm_base_link')

        self.target_color = self.get_parameter('target_color').value
        self.object_width = self.get_parameter('object_width').value
        self.detection_rate = self.get_parameter('detection_rate').value
        self.target_frame = self.get_parameter('target_frame').value

        # CV Bridge
        self.bridge = CvBridge()

        # Detection and pose estimation
        self.detector = ObjectDetector(min_area=500, max_area=50000)
        self.camera_info: Optional[CamInfo] = None
        self.pose_estimator: Optional[PoseEstimator] = None

        # TF2 for frame transforms
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Publishers
        self.pub_detections = self.create_publisher(
            Image, '/perception/detections', 10
        )
        self.pub_object_pose = self.create_publisher(
            PoseStamped, '/perception/object_pose', 10
        )

        # Subscribers
        self.sub_image = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )
        self.sub_camera_info = self.create_subscription(
            CameraInfo, '/camera/camera_info', self.camera_info_callback, 10
        )

        # Rate limiting
        self.detection_interval = 1.0 / self.detection_rate
        self.last_detection_time = self.get_clock().now()

        self.get_logger().info(
            f'Perception node started: target={self.target_color}, '
            f'width={self.object_width}m'
        )

    def camera_info_callback(self, msg: CameraInfo):
        """
        Store camera calibration.

        LEARNING: Camera calibration is essential for accurate
        pose estimation. The K matrix contains:
        [fx  0  cx]
        [0  fy  cy]
        [0   0   1]
        """
        if self.camera_info is None:
            self.camera_info = CamInfo(
                fx=msg.k[0],
                fy=msg.k[4],
                cx=msg.k[2],
                cy=msg.k[5],
                width=msg.width,
                height=msg.height,
            )
            self.pose_estimator = PoseEstimator(
                self.camera_info,
                known_object_width=self.object_width
            )
            self.get_logger().info(
                f'Camera info received: {msg.width}x{msg.height}, '
                f'fx={self.camera_info.fx:.1f}'
            )

    def image_callback(self, msg: Image):
        """Process camera images for objects."""
        # Rate limiting
        current_time = self.get_clock().now()
        elapsed = (current_time - self.last_detection_time).nanoseconds / 1e9
        if elapsed < self.detection_interval:
            return
        self.last_detection_time = current_time

        # Use default camera info if not received
        if self.pose_estimator is None:
            self.camera_info = create_default_camera_info(msg.width, msg.height)
            self.pose_estimator = PoseEstimator(
                self.camera_info,
                known_object_width=self.object_width
            )
            self.get_logger().warn('Using default camera intrinsics')

        try:
            # Convert ROS image to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

            # Run detection
            detections = self.detector.detect_by_color(cv_image, self.target_color)

            if detections:
                # Take best detection (largest)
                best = max(detections, key=lambda d: d.width * d.height)

                # Estimate pose in camera optical frame
                pose = self.pose_estimator.estimate_pose(
                    best.center_x, best.center_y, best.width
                )

                if pose:
                    # Create PoseStamped in camera optical frame
                    pose_msg = PoseStamped()
                    pose_msg.header.stamp = msg.header.stamp
                    pose_msg.header.frame_id = 'camera_link_optical'
                    pose_msg.pose.position.x = pose.x
                    pose_msg.pose.position.y = pose.y
                    pose_msg.pose.position.z = pose.z
                    pose_msg.pose.orientation.w = 1.0  # No rotation

                    # Transform to target frame
                    try:
                        transformed = self.tf_buffer.transform(
                            pose_msg, self.target_frame
                        )
                        self.pub_object_pose.publish(transformed)

                        self.get_logger().debug(
                            f'Object at ({transformed.pose.position.x:.3f}, '
                            f'{transformed.pose.position.y:.3f}, '
                            f'{transformed.pose.position.z:.3f}) in {self.target_frame}'
                        )
                    except tf2_ros.TransformException as e:
                        # Publish in camera frame if transform not available
                        self.pub_object_pose.publish(pose_msg)
                        self.get_logger().debug(
                            f'TF not available, publishing in camera frame: {e}'
                        )

            # Publish detection visualization
            viz_image = self.detector.draw_detections(cv_image, detections)
            detection_msg = self.bridge.cv2_to_imgmsg(viz_image, 'bgr8')
            detection_msg.header = msg.header
            self.pub_detections.publish(detection_msg)

        except Exception as e:
            self.get_logger().warn(f'Perception error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()

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
