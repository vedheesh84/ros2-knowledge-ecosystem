#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Demo 01: Arm Joint Control
==========================

LEARNING OBJECTIVES:
- Understand JointTrajectory message structure
- See how to command individual joints
- Learn trajectory point timing
- Practice reading joint states

KEY CONCEPTS:
- JointTrajectory: List of waypoints with timestamps
- JointTrajectoryPoint: Position + time_from_start
- Joint names must match URDF exactly

WATCH FOR:
- Joint limits (check URDF for limits)
- Trajectory timing (too fast = jerky motion)
- Joint state feedback in /joint_states
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
from control_msgs.action import FollowJointTrajectory
from builtin_interfaces.msg import Duration
import time


class JointControlDemo(Node):
    def __init__(self):
        super().__init__('demo_01_joint_control')

        # Arm joint names (from URDF)
        self.arm_joints = [
            'joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint'
        ]

        # Publisher for direct topic control
        self.traj_pub = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )

        # Action client for proper feedback
        self.action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/arm_controller/follow_joint_trajectory'
        )

        # Subscribe to joint states
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        self.current_positions = {}
        self.get_logger().info('Demo 01: Joint Control initialized')

        # Run demo after delay
        self.create_timer(2.0, self.run_demo)
        self._demo_started = False

    def joint_state_callback(self, msg: JointState):
        """Store current joint positions."""
        for name, pos in zip(msg.name, msg.position):
            self.current_positions[name] = pos

    def run_demo(self):
        """Execute joint control demo."""
        if self._demo_started:
            return
        self._demo_started = True

        self.get_logger().info('='*50)
        self.get_logger().info('DEMO 01: ARM JOINT CONTROL')
        self.get_logger().info('='*50)

        # Print current positions
        self.get_logger().info('\nCurrent joint positions:')
        for joint in self.arm_joints:
            pos = self.current_positions.get(joint, 'N/A')
            self.get_logger().info(f'  {joint}: {pos}')

        # Demo sequence
        poses = [
            ('Home', [0.0, 0.0, 0.0, 0.0, 0.0]),
            ('Wave 1', [0.5, 0.3, 0.0, 0.0, 0.0]),
            ('Wave 2', [-0.5, 0.3, 0.0, 0.0, 0.0]),
            ('Reach', [0.0, 0.5, 0.7, 0.4, 0.0]),
            ('Home', [0.0, 0.0, 0.0, 0.0, 0.0]),
        ]

        for name, positions in poses:
            self.get_logger().info(f'\nMoving to: {name}')
            self.send_trajectory(positions, duration=2.0)
            time.sleep(3.0)

        self.get_logger().info('\n' + '='*50)
        self.get_logger().info('Demo complete!')
        self.get_logger().info('='*50)

    def send_trajectory(self, positions: list, duration: float = 2.0):
        """
        Send joint trajectory command.

        LEARNING: JointTrajectory contains:
        - joint_names: Which joints to move
        - points: List of waypoints
        - Each point has positions and time_from_start
        """
        traj = JointTrajectory()
        traj.joint_names = self.arm_joints

        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=int(duration), nanosec=0)

        traj.points = [point]

        self.traj_pub.publish(traj)
        self.get_logger().info(f'  Sent trajectory: {positions}')


def main(args=None):
    rclpy.init(args=args)
    node = JointControlDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
