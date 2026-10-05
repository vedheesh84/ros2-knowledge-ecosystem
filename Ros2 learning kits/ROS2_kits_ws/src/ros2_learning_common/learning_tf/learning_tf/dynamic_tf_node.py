#!/usr/bin/env python3
"""
Dynamic TF Node - Broadcasting Moving Transforms
=================================================

LEARNING OBJECTIVES:
--------------------
1. Dynamic transforms that change over time
2. Continuous broadcasting (required for moving frames)
3. Rotation with quaternions

STATIC vs DYNAMIC:
------------------
- STATIC: Published once, never changes (sensor mounts)
- DYNAMIC: Published continuously, represents motion (robot movement)
"""

import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped
import math


class DynamicTFNode(Node):
    """Broadcasts dynamic transforms for moving frames."""

    def __init__(self):
        super().__init__('dynamic_tf_broadcaster')
        self.get_logger().info('Dynamic TF Node starting...')

        # Create dynamic transform broadcaster
        self.broadcaster = TransformBroadcaster(self)

        # Timer for continuous publishing
        self.timer = self.create_timer(0.1, self.broadcast_transform)  # 10 Hz
        self.angle = 0.0

        self.get_logger().info('Broadcasting rotating sensor frame...')

    def broadcast_transform(self):
        """Broadcast a rotating transform."""
        t = TransformStamped()

        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'rotating_sensor'

        # Fixed position, rotating orientation
        t.transform.translation.x = 0.3
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.1

        # Rotate around Z axis
        self.angle += 0.05  # radians per update
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = math.sin(self.angle / 2)
        t.transform.rotation.w = math.cos(self.angle / 2)

        self.broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = DynamicTFNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
