#!/usr/bin/env python3
"""
Static TF Node - Broadcasting Fixed Transforms
===============================================

LEARNING OBJECTIVES:
--------------------
1. What is a coordinate frame?
2. How to broadcast static (fixed) transforms
3. Parent-child frame relationships

TF TREE CONCEPT:
----------------
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                         TF TREE EXAMPLE                                 │
    │                                                                         │
    │                           world                                         │
    │                             │                                           │
    │                             │ (static)                                  │
    │                             ▼                                           │
    │                         base_link                                       │
    │                          /    \                                         │
    │                  (static)      (static)                                 │
    │                    /              \                                     │
    │               camera_link      lidar_link                               │
    │                                                                         │
    │   Static transforms NEVER change (sensor mounting positions)            │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

USAGE:
------
    ros2 run learning_tf static_tf_node

    # View the TF tree
    ros2 run tf2_tools view_frames
"""

import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
import math


class StaticTFNode(Node):
    """Broadcasts static transforms for fixed frame relationships."""

    def __init__(self):
        super().__init__('static_tf_broadcaster')
        self.get_logger().info('Static TF Node starting...')

        # Create static transform broadcaster
        self.static_broadcaster = StaticTransformBroadcaster(self)

        # Broadcast static transforms
        self.broadcast_static_transforms()

    def broadcast_static_transforms(self):
        """Broadcast all static transforms."""

        # Transform 1: world -> base_link (robot at origin)
        t1 = TransformStamped()
        t1.header.stamp = self.get_clock().now().to_msg()
        t1.header.frame_id = 'world'        # Parent frame
        t1.child_frame_id = 'base_link'     # Child frame
        t1.transform.translation.x = 0.0
        t1.transform.translation.y = 0.0
        t1.transform.translation.z = 0.0
        t1.transform.rotation.w = 1.0       # Identity quaternion

        # Transform 2: base_link -> camera_link (camera mounted on robot)
        t2 = TransformStamped()
        t2.header.stamp = self.get_clock().now().to_msg()
        t2.header.frame_id = 'base_link'
        t2.child_frame_id = 'camera_link'
        t2.transform.translation.x = 0.2    # 20cm forward
        t2.transform.translation.y = 0.0
        t2.transform.translation.z = 0.3    # 30cm up
        t2.transform.rotation.w = 1.0

        # Transform 3: base_link -> lidar_link
        t3 = TransformStamped()
        t3.header.stamp = self.get_clock().now().to_msg()
        t3.header.frame_id = 'base_link'
        t3.child_frame_id = 'lidar_link'
        t3.transform.translation.x = 0.0
        t3.transform.translation.y = 0.0
        t3.transform.translation.z = 0.5    # 50cm up
        t3.transform.rotation.w = 1.0

        # Broadcast all transforms
        self.static_broadcaster.sendTransform([t1, t2, t3])

        self.get_logger().info('Static transforms published:')
        self.get_logger().info('  world -> base_link')
        self.get_logger().info('  base_link -> camera_link')
        self.get_logger().info('  base_link -> lidar_link')
        self.get_logger().info('Use: ros2 run tf2_tools view_frames')


def main(args=None):
    rclpy.init(args=args)
    node = StaticTFNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
