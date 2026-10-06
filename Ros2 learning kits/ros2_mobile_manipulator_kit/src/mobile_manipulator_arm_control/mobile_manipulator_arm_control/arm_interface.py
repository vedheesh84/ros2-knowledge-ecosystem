#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Arm Interface - MoveIt2 Python Wrapper
======================================

LEARNING OBJECTIVES:
- Understand MoveGroupInterface usage
- See pose goal vs joint goal patterns
- Learn planning and execution flow
- Practice error handling for motion

KEY CONCEPTS:
- MoveGroupInterface: Main MoveIt API
- PlanningSceneInterface: Collision objects
- Named Targets: Pre-defined poses from SRDF
- Cartesian Path: Straight-line motion

USAGE:
    from mobile_manipulator_arm_control import ArmInterface

    arm = ArmInterface(node)
    arm.go_to_named_pose('ready')
    arm.go_to_pose(x=0.3, y=0.0, z=0.2)
    arm.open_gripper()
    arm.close_gripper()
"""

import rclpy
from rclpy.node import Node
from rclpy.logging import get_logger
from geometry_msgs.msg import Pose, PoseStamped
from moveit_msgs.action import MoveGroup, ExecuteTrajectory
from moveit_msgs.msg import (
    MotionPlanRequest,
    Constraints,
    JointConstraint,
    PositionConstraint,
    OrientationConstraint,
    BoundingVolume,
    RobotState,
)
from shape_msgs.msg import SolidPrimitive
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
from rclpy.action import ActionClient
from typing import Optional, List, Tuple
import math


class ArmInterface:
    """
    High-level interface for arm motion control.

    LEARNING OBJECTIVES:
    - Encapsulates MoveIt2 complexity
    - Provides simple API for common operations
    - Handles planning and execution flow
    """

    def __init__(
        self,
        node: Node,
        arm_group: str = 'arm',
        gripper_group: str = 'gripper',
        base_frame: str = 'arm_base_link',
        ee_frame: str = 'tool_frame',
    ):
        """
        Initialize arm interface.

        Args:
            node: ROS2 node for communication
            arm_group: MoveIt planning group for arm
            gripper_group: MoveIt planning group for gripper
            base_frame: Reference frame for poses
            ee_frame: End effector frame
        """
        self._node = node
        self._logger = node.get_logger()
        self._arm_group = arm_group
        self._gripper_group = gripper_group
        self._base_frame = base_frame
        self._ee_frame = ee_frame

        # Joint names (must match URDF/SRDF)
        self._arm_joints = [
            'joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint'
        ]
        self._gripper_joints = ['left_gear_joint']

        # Named poses (from SRDF)
        self._named_poses = {
            'home': [0.0, 0.0, 0.0, 0.0, 0.0],
            'ready': [0.0, 0.5, 0.7, 0.4, 0.0],
            'extended': [0.0, 0.3, 0.0, 0.0, 0.0],
        }

        # Action clients
        self._move_action_client = ActionClient(
            node, MoveGroup, '/move_action'
        )

        # Current state subscription
        self._current_joint_state: Optional[JointState] = None
        self._joint_state_sub = node.create_subscription(
            JointState, '/joint_states', self._joint_state_callback, 10
        )

        self._logger.info(f'ArmInterface initialized: arm={arm_group}, gripper={gripper_group}')

    def _joint_state_callback(self, msg: JointState):
        """Store latest joint state."""
        self._current_joint_state = msg

    def get_current_joint_values(self, group: str = 'arm') -> Optional[List[float]]:
        """
        Get current joint positions.

        LEARNING: Joint states come from /joint_states topic,
        published by joint_state_broadcaster.
        """
        if self._current_joint_state is None:
            self._logger.warn('No joint state received yet')
            return None

        joints = self._arm_joints if group == 'arm' else self._gripper_joints
        values = []

        for joint in joints:
            try:
                idx = self._current_joint_state.name.index(joint)
                values.append(self._current_joint_state.position[idx])
            except ValueError:
                self._logger.warn(f'Joint {joint} not found in joint_states')
                return None

        return values

    def go_to_named_pose(self, pose_name: str, wait: bool = True) -> bool:
        """
        Move to a named pose defined in SRDF.

        LEARNING: Named poses are joint configurations stored in SRDF.
        Examples: 'home', 'ready', 'extended'

        Args:
            pose_name: Name of pose from SRDF
            wait: Block until motion complete

        Returns:
            True if motion succeeded
        """
        if pose_name not in self._named_poses:
            self._logger.error(f'Unknown pose: {pose_name}')
            return False

        joint_values = self._named_poses[pose_name]
        return self.go_to_joint_values(joint_values, wait)

    def go_to_joint_values(
        self,
        joint_values: List[float],
        wait: bool = True
    ) -> bool:
        """
        Move to specific joint angles.

        LEARNING: Joint-space planning is:
        - Faster to plan
        - More predictable path
        - No IK needed

        Args:
            joint_values: Target angles in radians
            wait: Block until motion complete

        Returns:
            True if motion succeeded
        """
        if len(joint_values) != len(self._arm_joints):
            self._logger.error(
                f'Expected {len(self._arm_joints)} values, got {len(joint_values)}'
            )
            return False

        self._logger.info(f'Moving to joints: {joint_values}')

        # Build joint constraints
        constraints = Constraints()
        for name, value in zip(self._arm_joints, joint_values):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = value
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            constraints.joint_constraints.append(jc)

        # For now, just log the intent
        # Full MoveGroup action implementation would go here
        self._logger.info(f'Would plan to: {joint_values}')
        return True

    def go_to_pose(
        self,
        x: float,
        y: float,
        z: float,
        roll: float = 0.0,
        pitch: float = 0.0,
        yaw: float = 0.0,
        wait: bool = True
    ) -> bool:
        """
        Move end effector to Cartesian pose.

        LEARNING: Pose-space planning:
        - Requires IK solution
        - May have multiple solutions
        - Can fail if unreachable

        Args:
            x, y, z: Position in base_frame (meters)
            roll, pitch, yaw: Orientation (radians)
            wait: Block until motion complete

        Returns:
            True if motion succeeded
        """
        self._logger.info(f'Moving to pose: x={x:.3f}, y={y:.3f}, z={z:.3f}')

        pose = PoseStamped()
        pose.header.frame_id = self._base_frame
        pose.header.stamp = self._node.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z

        # Convert RPY to quaternion
        qx, qy, qz, qw = self._rpy_to_quaternion(roll, pitch, yaw)
        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw

        # Full implementation would use MoveGroup action
        self._logger.info(f'Would plan to pose: {pose.pose}')
        return True

    def open_gripper(self, wait: bool = True) -> bool:
        """
        Open the gripper.

        LEARNING: Gripper uses position control.
        0.8 rad = fully open for this gripper.
        """
        self._logger.info('Opening gripper')
        return self._set_gripper(0.8, wait)

    def close_gripper(self, wait: bool = True) -> bool:
        """
        Close the gripper.

        LEARNING: Gripper uses position control.
        0.0 rad = fully closed for this gripper.
        """
        self._logger.info('Closing gripper')
        return self._set_gripper(0.0, wait)

    def _set_gripper(self, position: float, wait: bool = True) -> bool:
        """Set gripper position."""
        self._logger.info(f'Setting gripper to {position:.2f}')
        # Full implementation would use GripperCommand action
        return True

    def _rpy_to_quaternion(
        self,
        roll: float,
        pitch: float,
        yaw: float
    ) -> Tuple[float, float, float, float]:
        """Convert roll-pitch-yaw to quaternion."""
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy

        return (qx, qy, qz, qw)

    def stop(self):
        """
        Stop current motion.

        LEARNING: Always have an e-stop capability!
        """
        self._logger.warn('STOP requested')
        # Would cancel current action goal
