#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Breaker: IK Failures
====================

FAILURE INJECTION:
Publishes object poses that cause IK failures.

FAILURE MODES:
1. unreachable: Pose too far for arm workspace
2. singularity: Pose at arm singularity
3. collision: Pose would cause self-collision

LEARNING OBJECTIVES:
- Understand arm workspace limits
- See IK failure error messages
- Learn singularity avoidance

HOW TO USE:
  # Run manipulation
  ros2 launch mobile_manipulator_manipulation manipulation.launch.py

  # Inject unreachable poses
  ros2 run mobile_manipulator_demos break_ik.py --ros-args -p mode:=unreachable

DEBUGGING:
  - Check /moveit/motion_plan_request for IK status
  - Use MoveIt RViz plugin to visualize workspace

COMMON IK FAILURES:
1. Out of reach (too far)
2. Out of reach (too close / behind base)
3. Singularity (arm fully extended)
4. Orientation impossible (wrist limits)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import math


class IKBreaker(Node):
    def __init__(self):
        super().__init__('break_ik')

        # Parameters
        self.declare_parameter('mode', 'unreachable')

        self.mode = self.get_parameter('mode').value

        # Publisher for fake object poses
        self.pose_pub = self.create_publisher(
            PoseStamped,
            '/perception/object_pose',
            10
        )

        self.get_logger().warn('='*50)
        self.get_logger().warn('IK BREAKER ACTIVE')
        self.get_logger().warn(f'Mode: {self.mode}')
        self.get_logger().warn('='*50)

        # Publish bad poses periodically
        self.create_timer(1.0, self.publish_bad_pose)

    def publish_bad_pose(self):
        """Publish pose that will cause IK failure."""
        pose = PoseStamped()
        pose.header.frame_id = 'arm_base_link'
        pose.header.stamp = self.get_clock().now().to_msg()

        if self.mode == 'unreachable':
            # Way too far for arm to reach
            pose.pose.position.x = 1.0   # 1 meter away
            pose.pose.position.y = 0.0
            pose.pose.position.z = 0.2
            self.get_logger().warn('Publishing unreachable pose (1m away)')

        elif self.mode == 'singularity':
            # At singularity (arm fully extended)
            # Most 5-DOF arms have singularity when fully stretched
            pose.pose.position.x = 0.35  # At workspace edge
            pose.pose.position.y = 0.0
            pose.pose.position.z = 0.0   # Low, arm extended
            self.get_logger().warn('Publishing singularity pose (arm extended)')

        elif self.mode == 'collision':
            # Behind/under the base (self-collision risk)
            pose.pose.position.x = -0.1  # Behind base
            pose.pose.position.y = 0.0
            pose.pose.position.z = 0.0
            self.get_logger().warn('Publishing collision-risk pose (behind base)')

        # Standard top-down orientation
        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = math.sin(math.pi / 4)  # 90 deg pitch
        pose.pose.orientation.z = 0.0
        pose.pose.orientation.w = math.cos(math.pi / 4)

        self.pose_pub.publish(pose)


def main(args=None):
    rclpy.init(args=args)
    node = IKBreaker()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Breaker stopped')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
