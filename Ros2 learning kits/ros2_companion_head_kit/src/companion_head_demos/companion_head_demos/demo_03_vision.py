#!/usr/bin/env python3
"""
Demo 03: Vision Processing

LEARNING OBJECTIVES:
====================
1. OpenCV face detection pipeline
2. Image processing in ROS2
3. Detection-to-gaze coordination

WHAT THIS DEMO DOES:
====================
1. Subscribe to camera and face detection topics
2. Display detection statistics
3. Show automatic gaze tracking to detected face

TRY THIS:
=========
- Move in front of the camera
- Watch the head track your face
- See detection confidence scores

COMMANDS:
=========
    # Run this demo
    ros2 run companion_head_demos demo_03_vision

PREREQUISITE:
=============
    ros2 run companion_head_sensors face_detector
"""

import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class VisionDemo(Node):
    """Demo that shows vision processing."""

    def __init__(self):
        super().__init__('demo_03_vision')

        self.face_count = 0
        self.total_detections = 0
        self.start_time = self.get_clock().now()

        # Subscribe to face detections
        self.faces_sub = self.create_subscription(
            String, '/faces/detections', self.faces_callback, 10)

        self.get_logger().info('='*60)
        self.get_logger().info('DEMO 03: VISION PROCESSING')
        self.get_logger().info('='*60)
        self.get_logger().info('')
        self.get_logger().info('Make sure face_detector is running:')
        self.get_logger().info('  ros2 run companion_head_sensors face_detector')
        self.get_logger().info('')
        self.get_logger().info('View annotated image in RViz:')
        self.get_logger().info('  Topic: /faces/image')
        self.get_logger().info('')
        self.get_logger().info('Waiting for face detections...')
        self.get_logger().info('')

        # Status timer
        self.create_timer(5.0, self.print_status)

    def faces_callback(self, msg: String):
        """Process face detection results."""
        try:
            data = json.loads(msg.data)
            count = data.get('count', 0)

            if count != self.face_count:
                self.face_count = count
                if count > 0:
                    self.get_logger().info(f'Detected {count} face(s)!')
                    primary = data.get('primary_id', -1)
                    self.get_logger().info(f'  Primary face ID: {primary}')

                    for face in data.get('faces', []):
                        self.get_logger().info(
                            f"  Face {face['id']}: center=({face['center']['x']:.2f}, "
                            f"{face['center']['y']:.2f}), depth={face.get('depth', 0):.2f}m"
                        )
                else:
                    self.get_logger().info('No faces detected')

            self.total_detections += count

        except json.JSONDecodeError:
            pass

    def print_status(self):
        """Print periodic status."""
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        rate = self.total_detections / elapsed if elapsed > 0 else 0

        self.get_logger().info(f'[Status] Current faces: {self.face_count}, '
                               f'Total detections: {self.total_detections}, '
                               f'Avg rate: {rate:.1f}/s')


def main(args=None):
    rclpy.init(args=args)
    node = VisionDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
