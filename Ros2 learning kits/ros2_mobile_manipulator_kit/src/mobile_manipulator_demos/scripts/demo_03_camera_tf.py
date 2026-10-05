#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Demo 03: Camera TF Alignment
============================

LEARNING OBJECTIVES:
- Understand camera frame conventions
- See camera_link vs camera_link_optical
- Learn to transform poses between frames
- Practice TF debugging techniques

KEY CONCEPTS:
- camera_link: ROS convention (X forward)
- camera_link_optical: OpenCV convention (Z forward)
- Detections are in optical frame!
- Must transform to arm frame for grasping

FRAME CONVENTIONS:
  ROS (camera_link):     OpenCV (camera_link_optical):
    Z                        Y
    |  X                     |
    | /                      |
    |/___Y                   |___X
                            /
                           Z (into image)

WATCH FOR:
- ros2 run tf2_tools view_frames (visualize TF tree)
- ros2 topic echo /tf_static (check camera transform)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped, TransformStamped
from tf2_ros import Buffer, TransformListener, TransformBroadcaster
import tf2_geometry_msgs
import math


class CameraTFDemo(Node):
    def __init__(self):
        super().__init__('demo_03_camera_tf')

        # TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # For visualizing test point
        self.tf_broadcaster = TransformBroadcaster(self)

        self.get_logger().info('Demo 03: Camera TF Alignment initialized')

        # Run demo after TF is available
        self.create_timer(2.0, self.run_demo)
        self._demo_started = False

    def run_demo(self):
        """Execute camera TF demo."""
        if self._demo_started:
            return
        self._demo_started = True

        self.get_logger().info('='*50)
        self.get_logger().info('DEMO 03: CAMERA TF ALIGNMENT')
        self.get_logger().info('='*50)

        # 1. Show available frames
        self.get_logger().info('\n1. Checking TF frames...')
        frames = self.tf_buffer.all_frames_as_string()
        self.get_logger().info(f'\nAvailable frames:\n{frames}')

        # 2. Get camera transforms
        self.get_logger().info('\n2. Camera frame transforms...')

        try:
            # camera_link to body_link
            t1 = self.tf_buffer.lookup_transform(
                'body_link', 'camera_link', rclpy.time.Time()
            )
            self.get_logger().info(f'\nbody_link → camera_link:')
            self.get_logger().info(f'  Position: ({t1.transform.translation.x:.3f}, '
                                   f'{t1.transform.translation.y:.3f}, '
                                   f'{t1.transform.translation.z:.3f})')

            # camera_link_optical to camera_link
            t2 = self.tf_buffer.lookup_transform(
                'camera_link', 'camera_link_optical', rclpy.time.Time()
            )
            self.get_logger().info(f'\ncamera_link → camera_link_optical:')
            self.get_logger().info(f'  This is the ROS↔OpenCV frame rotation')

        except Exception as e:
            self.get_logger().warn(f'TF lookup failed: {e}')

        # 3. Transform a test point
        self.get_logger().info('\n3. Transforming a detected point...')
        self.get_logger().info('   Simulating object at (0.0, 0.0, 0.5) in camera_optical')

        point_in_optical = PointStamped()
        point_in_optical.header.frame_id = 'camera_link_optical'
        point_in_optical.header.stamp = self.get_clock().now().to_msg()
        point_in_optical.point.x = 0.0  # Center of image
        point_in_optical.point.y = 0.0  # Center of image
        point_in_optical.point.z = 0.5  # 50cm depth

        try:
            # Transform to arm frame
            point_in_arm = self.tf_buffer.transform(
                point_in_optical, 'arm_base_link'
            )
            self.get_logger().info(f'\n   In arm_base_link frame:')
            self.get_logger().info(f'   x={point_in_arm.point.x:.3f}, '
                                   f'y={point_in_arm.point.y:.3f}, '
                                   f'z={point_in_arm.point.z:.3f}')

        except Exception as e:
            self.get_logger().warn(f'   Transform failed: {e}')

        # 4. Common mistakes
        self.get_logger().info('\n4. COMMON MISTAKES:')
        self.get_logger().info('   - Using camera_link instead of camera_link_optical')
        self.get_logger().info('   - X/Y swapped in detection (row vs column)')
        self.get_logger().info('   - Stale transform (timestamp too old)')
        self.get_logger().info('   - Missing camera calibration (wrong intrinsics)')

        self.get_logger().info('\n' + '='*50)
        self.get_logger().info('Demo complete!')
        self.get_logger().info('='*50)
        self.get_logger().info('\nTry: ros2 run tf2_tools view_frames')


def main(args=None):
    rclpy.init(args=args)
    node = CameraTFDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
