#!/usr/bin/env python3
"""
TF Listener Node - Looking Up Transforms
=========================================

LEARNING OBJECTIVES:
--------------------
1. How to query transforms between any two frames
2. Using TF buffer for time travel
3. Handling transform exceptions

KEY CONCEPT:
------------
TF2 can compute transforms between ANY two frames in the tree,
even if they're not directly connected!

    world -> base_link -> camera_link

    You can ask: "What's the transform from world to camera_link?"
    TF2 chains them automatically!
"""

import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener, LookupException
from geometry_msgs.msg import TransformStamped


class TFListenerNode(Node):
    """Listens to and looks up transforms."""

    def __init__(self):
        super().__init__('tf_listener')
        self.get_logger().info('TF Listener Node starting...')

        # Create TF buffer and listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        # Timer to periodically lookup transforms
        self.timer = self.create_timer(1.0, self.lookup_transforms)

        self.get_logger().info('Waiting for transforms...')

    def lookup_transforms(self):
        """Look up transforms and log them."""

        # Try to look up world -> camera_link
        try:
            transform = self.tf_buffer.lookup_transform(
                'world',           # Target frame
                'camera_link',     # Source frame
                rclpy.time.Time()  # Latest available
            )
            self.get_logger().info(
                f'world -> camera_link: '
                f'x={transform.transform.translation.x:.2f}, '
                f'y={transform.transform.translation.y:.2f}, '
                f'z={transform.transform.translation.z:.2f}'
            )
        except Exception as e:
            self.get_logger().warn(f'Could not get world->camera: {e}')

        # Try rotating sensor
        try:
            transform = self.tf_buffer.lookup_transform(
                'base_link',
                'rotating_sensor',
                rclpy.time.Time()
            )
            self.get_logger().info(
                f'base_link -> rotating_sensor: '
                f'rotation z={transform.transform.rotation.z:.2f}'
            )
        except Exception as e:
            self.get_logger().debug(f'No rotating_sensor yet: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = TFListenerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
