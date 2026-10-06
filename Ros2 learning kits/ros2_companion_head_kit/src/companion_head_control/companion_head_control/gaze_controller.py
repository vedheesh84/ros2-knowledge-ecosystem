#!/usr/bin/env python3
"""
gaze_controller.py - Look-at target tracking for Companion Head

LEARNING OBJECTIVES:
====================
1. Inverse kinematics for pan/tilt mechanism
2. Smooth trajectory generation
3. Target tracking with prediction

CONTROL FLOW:
=============
    /gaze/target (PointStamped)
           │
           ▼
    ┌─────────────────┐
    │ Gaze Controller │
    │                 │
    │ 1. Transform to │
    │    head frame   │
    │ 2. Compute IK   │
    │    (pan, tilt)  │
    │ 3. Smooth       │
    │    trajectory   │
    └─────────────────┘
           │
           ▼
    /joint_trajectory_controller/joint_trajectory (JointTrajectory)

TOPICS:
=======
    Subscribes:
    - /gaze/target (geometry_msgs/PointStamped): Target to look at
    - /joint_states (sensor_msgs/JointState): Current joint positions

    Publishes:
    - /joint_trajectory_controller/joint_trajectory: Joint commands
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class GazeController(Node):
    """
    Controls the companion head to look at a target point.

    Uses simple inverse kinematics for the 2-DOF pan/tilt mechanism.
    """

    def __init__(self):
        super().__init__('gaze_controller')

        # Parameters
        self.declare_parameter('tracking_gain', 2.0)
        self.declare_parameter('max_velocity', 1.5)  # rad/s
        self.declare_parameter('smoothing_factor', 0.3)
        self.declare_parameter('pan_limits', [-1.57, 1.57])  # ±90 deg
        self.declare_parameter('tilt_limits', [-0.52, 0.79])  # -30 to +45 deg

        self.tracking_gain = self.get_parameter('tracking_gain').value
        self.max_velocity = self.get_parameter('max_velocity').value
        self.smoothing = self.get_parameter('smoothing_factor').value
        self.pan_limits = self.get_parameter('pan_limits').value
        self.tilt_limits = self.get_parameter('tilt_limits').value

        # State
        self.current_pan = 0.0
        self.current_tilt = 0.0
        self.target_pan = 0.0
        self.target_tilt = 0.0

        # Subscribers
        self.gaze_sub = self.create_subscription(
            PointStamped,
            '/gaze/target',
            self.gaze_callback,
            10
        )

        self.joint_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_callback,
            10
        )

        # Publisher
        self.trajectory_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )

        # Control loop timer
        self.create_timer(0.05, self.control_loop)  # 20 Hz

        self.get_logger().info('Gaze Controller initialized')
        self.get_logger().info(f'  Pan limits: {self.pan_limits}')
        self.get_logger().info(f'  Tilt limits: {self.tilt_limits}')

    def joint_callback(self, msg: JointState):
        """Update current joint positions from joint states."""
        for i, name in enumerate(msg.name):
            if name == 'neck_pan_joint':
                self.current_pan = msg.position[i]
            elif name == 'neck_tilt_joint':
                self.current_tilt = msg.position[i]

    def gaze_callback(self, msg: PointStamped):
        """
        Compute target joint angles from gaze target point.

        The target point is assumed to be in the base_link frame.
        We compute pan (yaw) and tilt (pitch) angles to look at it.
        """
        # Target position relative to head center
        # Assuming base_link frame, head is at approximately (0, 0, 0.2)
        x = msg.point.x
        y = msg.point.y
        z = msg.point.z - 0.2  # Adjust for head height

        # Compute distance to target in XY plane
        dist_xy = math.sqrt(x*x + y*y)

        if dist_xy < 0.01:
            # Target too close or directly above/below
            return

        # Inverse kinematics for pan/tilt
        # Pan angle: atan2(y, x) - but we want forward to be -Y direction
        # (camera faces -Y in our URDF convention)
        self.target_pan = math.atan2(-x, -y)

        # Tilt angle: atan2(z, dist)
        self.target_tilt = math.atan2(z, dist_xy)

        # Clamp to limits
        self.target_pan = max(self.pan_limits[0],
                              min(self.pan_limits[1], self.target_pan))
        self.target_tilt = max(self.tilt_limits[0],
                               min(self.tilt_limits[1], self.target_tilt))

    def control_loop(self):
        """
        Smooth tracking control loop.

        Applies smoothing filter and generates trajectory command.
        """
        # Smooth towards target (exponential smoothing)
        alpha = self.smoothing
        target_pan = alpha * self.target_pan + (1 - alpha) * self.current_pan
        target_tilt = alpha * self.target_tilt + (1 - alpha) * self.current_tilt

        # Only send command if there's significant movement
        pan_diff = abs(target_pan - self.current_pan)
        tilt_diff = abs(target_tilt - self.current_tilt)

        if pan_diff < 0.01 and tilt_diff < 0.01:
            return

        # Create trajectory message
        traj = JointTrajectory()
        traj.header.stamp = self.get_clock().now().to_msg()
        traj.joint_names = ['neck_pan_joint', 'neck_tilt_joint']

        # Single point trajectory
        point = JointTrajectoryPoint()
        point.positions = [target_pan, target_tilt]
        point.velocities = [0.0, 0.0]

        # Compute time based on movement distance and max velocity
        max_diff = max(pan_diff, tilt_diff)
        duration = max(0.1, max_diff / self.max_velocity)
        point.time_from_start = Duration(sec=int(duration),
                                         nanosec=int((duration % 1) * 1e9))

        traj.points = [point]
        self.trajectory_pub.publish(traj)


def main(args=None):
    rclpy.init(args=args)
    node = GazeController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
