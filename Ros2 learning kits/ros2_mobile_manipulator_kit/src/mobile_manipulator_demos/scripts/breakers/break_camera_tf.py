#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Breaker: Camera TF
==================

FAILURE INJECTION:
Publishes incorrect camera TF to simulate common camera calibration issues.

FAILURE MODES:
1. offset: TF translation is wrong (camera not where expected)
2. rotation: TF rotation is wrong (camera tilted)
3. stale: TF timestamps are old (TF timeout)

LEARNING OBJECTIVES:
- See how TF errors affect pose estimation
- Practice debugging TF issues
- Understand camera calibration importance

HOW TO USE:
  # Start with correct TF
  ros2 launch mobile_manipulator_bringup simulation.launch.py

  # In another terminal, run breaker
  ros2 run mobile_manipulator_demos break_camera_tf.py --ros-args -p mode:=offset

  # Watch /perception/object_pose drift!

FIX:
  - Ctrl+C the breaker
  - Correct TF resumes from robot_state_publisher
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import math


class CameraTFBreaker(Node):
    def __init__(self):
        super().__init__('break_camera_tf')

        # Parameters
        self.declare_parameter('mode', 'offset')  # offset, rotation, stale
        self.declare_parameter('offset_x', 0.1)   # 10cm error
        self.declare_parameter('offset_y', 0.05)  # 5cm error
        self.declare_parameter('rotation_error', 0.2)  # ~11 degrees

        self.mode = self.get_parameter('mode').value
        self.offset_x = self.get_parameter('offset_x').value
        self.offset_y = self.get_parameter('offset_y').value
        self.rotation_error = self.get_parameter('rotation_error').value

        self.tf_broadcaster = TransformBroadcaster(self)

        self.get_logger().warn('='*50)
        self.get_logger().warn('CAMERA TF BREAKER ACTIVE')
        self.get_logger().warn(f'Mode: {self.mode}')
        self.get_logger().warn('='*50)

        if self.mode == 'offset':
            self.get_logger().warn(f'Injecting position offset: ({self.offset_x}, {self.offset_y}, 0)')
        elif self.mode == 'rotation':
            self.get_logger().warn(f'Injecting rotation error: {math.degrees(self.rotation_error):.1f} degrees')
        elif self.mode == 'stale':
            self.get_logger().warn('Publishing stale TF (10s old timestamps)')

        # Publish broken TF at high rate to override correct TF
        self.create_timer(0.02, self.publish_broken_tf)  # 50Hz

    def publish_broken_tf(self):
        """Publish incorrect camera TF."""
        t = TransformStamped()
        t.header.frame_id = 'body_link'
        t.child_frame_id = 'camera_link'

        # Set timestamp based on mode
        if self.mode == 'stale':
            # Old timestamp causes TF timeout
            old_time = self.get_clock().now().to_msg()
            old_time.sec -= 10  # 10 seconds old
            t.header.stamp = old_time
        else:
            t.header.stamp = self.get_clock().now().to_msg()

        # Correct position (from URDF)
        t.transform.translation.x = 0.1
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.15

        # Apply errors
        if self.mode == 'offset':
            t.transform.translation.x += self.offset_x
            t.transform.translation.y += self.offset_y

        # Rotation (default: looking forward)
        if self.mode == 'rotation':
            # Add rotation error around Z axis
            t.transform.rotation.x = 0.0
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = math.sin(self.rotation_error / 2)
            t.transform.rotation.w = math.cos(self.rotation_error / 2)
        else:
            t.transform.rotation.w = 1.0

        self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = CameraTFBreaker()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Breaker stopped')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
