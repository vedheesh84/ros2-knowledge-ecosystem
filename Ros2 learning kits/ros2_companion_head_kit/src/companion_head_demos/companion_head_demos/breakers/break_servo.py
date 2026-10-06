#!/usr/bin/env python3
"""
break_servo.py - Servo Failure Injection

LEARNING OBJECTIVES:
====================
1. Motion system robustness
2. Reduced mobility handling
3. Servo fault detection

FAILURE MODES:
==============
- jam: Servo stuck at position
- drift: Gradual position drift
- limit: Reduced range of motion
- noise: Jittery motion

USAGE:
======
    ros2 run companion_head_demos break_servo --ros-args -p joint:=neck_pan_joint -p mode:=jam
"""

import random
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class BreakServo(Node):
    """Injects failures into servo commands."""

    def __init__(self):
        super().__init__('break_servo')

        # Parameters
        self.declare_parameter('joint', 'neck_pan_joint')
        self.declare_parameter('mode', 'jam')
        self.declare_parameter('intensity', 0.5)

        self.joint = self.get_parameter('joint').value
        self.mode = self.get_parameter('mode').value
        self.intensity = self.get_parameter('intensity').value

        self.jammed_position = None
        self.drift_offset = 0.0

        # Subscriber
        self.traj_sub = self.create_subscription(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            self.trajectory_callback,
            10
        )

        # Publisher
        self.traj_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory_broken',
            10
        )

        self.get_logger().info('='*60)
        self.get_logger().info('BREAKER: Servo Failure Injection')
        self.get_logger().info('='*60)
        self.get_logger().info(f'  Joint: {self.joint}')
        self.get_logger().info(f'  Mode: {self.mode}')
        self.get_logger().info(f'  Intensity: {self.intensity}')

        # Drift timer
        if self.mode == 'drift':
            self.create_timer(0.1, self.apply_drift)

    def apply_drift(self):
        """Gradually increase drift offset."""
        self.drift_offset += 0.001 * self.intensity

    def trajectory_callback(self, msg: JointTrajectory):
        """Apply failure to trajectory command."""
        # Find target joint index
        try:
            joint_idx = msg.joint_names.index(self.joint)
        except ValueError:
            # Joint not in this message
            self.traj_pub.publish(msg)
            return

        # Modify trajectory points
        for point in msg.points:
            original = point.positions[joint_idx]

            if self.mode == 'jam':
                if self.jammed_position is None:
                    self.jammed_position = original
                point.positions = list(point.positions)
                point.positions[joint_idx] = self.jammed_position
                self.get_logger().warn(f'[BREAK] Jam: keeping at {self.jammed_position:.2f}')

            elif self.mode == 'drift':
                point.positions = list(point.positions)
                point.positions[joint_idx] += self.drift_offset
                self.get_logger().warn(f'[BREAK] Drift: +{self.drift_offset:.3f}')

            elif self.mode == 'limit':
                # Reduce range
                max_range = 0.5 * (1 - self.intensity)
                point.positions = list(point.positions)
                point.positions[joint_idx] = max(-max_range, min(max_range, original))

            elif self.mode == 'noise':
                noise = random.gauss(0, self.intensity * 0.1)
                point.positions = list(point.positions)
                point.positions[joint_idx] += noise

        self.traj_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = BreakServo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
