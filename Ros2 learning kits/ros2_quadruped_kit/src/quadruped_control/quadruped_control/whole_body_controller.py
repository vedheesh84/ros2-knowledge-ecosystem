#!/usr/bin/env python3
"""
whole_body_controller.py - Force-to-Torque Mapping

LEARNING OBJECTIVES:
- Understanding the Jacobian transpose method
- Force distribution to joint torques
- Why whole-body control is needed

WHOLE-BODY CONTROL:
MPC outputs desired forces at the feet (task space).
We need to convert these to joint torques (joint space).

The relationship is:
τ = J^T * F

where:
- τ: Joint torques (3 per leg)
- J: Jacobian of foot position w.r.t. joint angles
- F: Desired foot force (3D vector)

This is called "Jacobian Transpose Control" and is widely used
because it doesn't require Jacobian inversion (more stable).
"""

import numpy as np
from typing import Dict

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


class WholeBodyController(Node):
    """
    Converts foot forces to joint torques using Jacobian transpose.

    Subscribes:
    - /mpc/forces: Desired foot forces from MPC
    - /joint_states: Current joint positions

    Publishes:
    - /leg_controller/commands: Joint torque commands
    """

    def __init__(self):
        super().__init__('whole_body_controller')

        # Robot parameters (from URDF)
        self.hip_offset = 0.08
        self.upper_leg = 0.20
        self.lower_leg = 0.20

        # Leg names and joint order
        self.legs = ['FL', 'FR', 'RL', 'RR']
        self.joint_names = []
        for leg in self.legs:
            self.joint_names.extend([f'{leg}_HAA', f'{leg}_HFE', f'{leg}_KFE'])

        # Current joint positions
        self.joint_positions = {name: 0.0 for name in self.joint_names}

        # ==================== SUBSCRIBERS ====================
        self.force_sub = self.create_subscription(
            Float64MultiArray, '/mpc/forces', self.force_callback, 10)
        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_callback, 10)

        # ==================== PUBLISHERS ====================
        self.torque_pub = self.create_publisher(
            Float64MultiArray, '/leg_controller/commands', 10)

        self.get_logger().info('Whole Body Controller initialized')

    def joint_callback(self, msg: JointState):
        """Update current joint positions."""
        for i, name in enumerate(msg.name):
            if name in self.joint_positions:
                self.joint_positions[name] = msg.position[i] if msg.position else 0.0

    def compute_jacobian(self, leg: str) -> np.ndarray:
        """
        Compute 3x3 Jacobian for a leg.

        The Jacobian relates foot velocity to joint velocities:
        v_foot = J * dq

        For force control, we use:
        τ = J^T * F
        """
        # Get joint angles
        q_haa = self.joint_positions.get(f'{leg}_HAA', 0.0)
        q_hfe = self.joint_positions.get(f'{leg}_HFE', 0.0)
        q_kfe = self.joint_positions.get(f'{leg}_KFE', 0.0)

        # Side multiplier (left legs have negative y)
        side = -1 if leg[1] == 'L' else 1

        # Precompute trig
        c1, s1 = np.cos(q_haa), np.sin(q_haa)
        c2, s2 = np.cos(q_hfe), np.sin(q_hfe)
        c23 = np.cos(q_hfe + q_kfe)
        s23 = np.sin(q_hfe + q_kfe)

        l1 = self.hip_offset * side
        l2 = self.upper_leg
        l3 = self.lower_leg

        # Jacobian columns (partial derivatives of foot position)
        # Column 1: d(foot)/d(HAA)
        J1 = np.array([
            0,
            -c1 * (l1 + l2 * c2 + l3 * c23) - s1 * (l2 * s2 + l3 * s23),
            -s1 * (l1 + l2 * c2 + l3 * c23) + c1 * (l2 * s2 + l3 * s23)
        ])

        # Column 2: d(foot)/d(HFE)
        J2 = np.array([
            -l2 * c2 - l3 * c23,
            s1 * (-l2 * s2 - l3 * s23),
            c1 * (-l2 * s2 - l3 * s23)
        ])

        # Column 3: d(foot)/d(KFE)
        J3 = np.array([
            -l3 * c23,
            -s1 * l3 * s23,
            c1 * (-l3 * s23)
        ])

        return np.column_stack([J1, J2, J3])

    def force_callback(self, msg: Float64MultiArray):
        """Convert foot forces to joint torques."""
        if len(msg.data) != 12:
            return

        torques = []

        for i, leg in enumerate(self.legs):
            # Extract force for this leg
            force = np.array(msg.data[i*3:(i+1)*3])

            # Compute Jacobian
            J = self.compute_jacobian(leg)

            # Torque = J^T * Force
            tau = J.T @ force

            torques.extend(tau.tolist())

        # Publish torques
        torque_msg = Float64MultiArray()
        torque_msg.data = torques
        self.torque_pub.publish(torque_msg)


def main(args=None):
    rclpy.init(args=args)
    node = WholeBodyController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
