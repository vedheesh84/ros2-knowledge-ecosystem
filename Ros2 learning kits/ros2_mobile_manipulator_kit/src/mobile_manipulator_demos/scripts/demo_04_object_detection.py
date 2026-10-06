#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Demo 04: Object Detection
=========================

LEARNING OBJECTIVES:
- Understand OpenCV color detection pipeline
- See HSV tuning for different lighting
- Learn 2D→3D pose estimation
- Practice detection debugging

KEY CONCEPTS:
- HSV better than RGB for color detection
- Morphology cleans up noise
- Known object size enables depth estimation
- Multiple detections need filtering

WATCH FOR:
- /perception/detections image shows detection overlay
- /perception/object_pose shows 3D position
- ros2 topic hz /perception/object_pose for rate
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String


class ObjectDetectionDemo(Node):
    def __init__(self):
        super().__init__('demo_04_object_detection')

        # Track detection stats
        self.detection_count = 0
        self.last_pose = None

        # Subscribers
        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/perception/object_pose',
            self.pose_callback,
            10
        )

        self.detection_sub = self.create_subscription(
            Image,
            '/perception/detections',
            self.detection_callback,
            10
        )

        self.get_logger().info('Demo 04: Object Detection initialized')
        self.get_logger().info('Subscribing to /perception/object_pose')
        self.get_logger().info('Make sure perception_node is running!')

        # Status timer
        self.create_timer(2.0, self.print_status)

    def pose_callback(self, msg: PoseStamped):
        """Handle detected object pose."""
        self.detection_count += 1
        self.last_pose = msg

    def detection_callback(self, msg: Image):
        """Handle detection image (for stats)."""
        pass  # Just counting in pose_callback

    def print_status(self):
        """Print detection status."""
        self.get_logger().info('='*50)
        self.get_logger().info('OBJECT DETECTION STATUS')
        self.get_logger().info('='*50)
        self.get_logger().info(f'\nDetections received: {self.detection_count}')

        if self.last_pose:
            p = self.last_pose.pose.position
            self.get_logger().info(f'\nLast detected pose:')
            self.get_logger().info(f'  Frame: {self.last_pose.header.frame_id}')
            self.get_logger().info(f'  Position: ({p.x:.3f}, {p.y:.3f}, {p.z:.3f})')
        else:
            self.get_logger().info('\nNo objects detected yet')
            self.get_logger().info('\nTroubleshooting:')
            self.get_logger().info('  1. Is camera publishing? (ros2 topic hz /camera/image_raw)')
            self.get_logger().info('  2. Is perception node running? (ros2 node list)')
            self.get_logger().info('  3. Is target color correct? (default: red)')
            self.get_logger().info('  4. Try: ros2 run rqt_image_view rqt_image_view')

        self.get_logger().info('\n' + '='*50)


def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectionDemo()

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
