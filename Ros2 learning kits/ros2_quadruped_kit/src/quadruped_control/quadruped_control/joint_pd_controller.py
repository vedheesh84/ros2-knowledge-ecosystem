#!/usr/bin/env python3
"""
joint_pd_controller.py - Joint-Level PD Control

LEARNING OBJECTIVES:
- Understanding PD control for joints
- Position and velocity feedback
- Feedforward torque addition

PD CONTROL:
The simplest joint controller:
τ = Kp * (q_desired - q_actual) + Kd * (dq_desired - dq_actual) + τ_ff

where:
- Kp: Position gain (stiffness)
- Kd: Velocity gain (damping)
- τ_ff: Feedforward torque (from WBC)

TUNING:
- Higher Kp: Stiffer joints, faster response, more oscillation
- Higher Kd: More damping, slower response, less overshoot
- Critical damping: Kd = 2 * sqrt(Kp * I) where I is joint inertia

This is often used as the lowest level controller,
receiving targets from whole-body control.
"""

import numpy as np
from typing import Dict

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray


class JointPDController(Node):
    """
    Joint-level PD controller with feedforward torque.

    Can operate in two modes:
    1. Position mode: Track desired joint positions
    2. Torque mode: Add PD around current position (compliance)

    Subscribes:
    - /joint_states: Current joint positions/velocities
    - /joint_targets: Desired positions (optional)
    - /leg_controller/commands: Feedforward torques from WBC

    Publishes:
    - /joint_efforts: Final joint torques to hardware
    """

    def __init__(self):
        super().__init__('joint_pd_controller')

        # Parameters
        self.declare_parameter('kp', 50.0)
        self.declare_parameter('kd', 2.0)
        self.declare_parameter('mode', 'torque')  # 'position' or 'torque'

        self.kp = self.get_parameter('kp').value
        self.kd = self.get_parameter('kd').value
        self.mode = self.get_parameter('mode').value

        # Joint names
        self.legs = ['FL', 'FR', 'RL', 'RR']
        self.joint_names = []
        for leg in self.legs:
            self.joint_names.extend([f'{leg}_HAA', f'{leg}_HFE', f'{leg}_KFE'])

        # State storage
        self.positions = {name: 0.0 for name in self.joint_names}
        self.velocities = {name: 0.0 for name in self.joint_names}
        self.target_positions = {name: 0.0 for name in self.joint_names}
        self.feedforward_torques = {name: 0.0 for name in self.joint_names}

        # Default standing pose
        for leg in self.legs:
            self.target_positions[f'{leg}_HAA'] = 0.0
            self.target_positions[f'{leg}_HFE'] = -0.5
            self.target_positions[f'{leg}_KFE'] = 1.0

        # ==================== SUBSCRIBERS ====================
        self.joint_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_callback, 10)
        self.target_sub = self.create_subscription(
            Float64MultiArray, '/joint_targets', self.target_callback, 10)
        self.ff_sub = self.create_subscription(
            Float64MultiArray, '/leg_controller/commands', self.feedforward_callback, 10)

        # ==================== PUBLISHERS ====================
        self.effort_pub = self.create_publisher(
            Float64MultiArray, '/joint_efforts', 10)

        # Control timer (500 Hz for responsive control)
        self.create_timer(0.002, self.control_loop)

        self.get_logger().info(f'Joint PD Controller initialized (Kp={self.kp}, Kd={self.kd})')

    def joint_callback(self, msg: JointState):
        """Update current joint states."""
        for i, name in enumerate(msg.name):
            if name in self.positions:
                self.positions[name] = msg.position[i] if i < len(msg.position) else 0.0
                self.velocities[name] = msg.velocity[i] if i < len(msg.velocity) else 0.0

    def target_callback(self, msg: Float64MultiArray):
        """Update target positions."""
        if len(msg.data) == len(self.joint_names):
            for i, name in enumerate(self.joint_names):
                self.target_positions[name] = msg.data[i]

    def feedforward_callback(self, msg: Float64MultiArray):
        """Update feedforward torques from whole-body control."""
        if len(msg.data) == len(self.joint_names):
            for i, name in enumerate(self.joint_names):
                self.feedforward_torques[name] = msg.data[i]

    def control_loop(self):
        """Compute and publish joint torques."""
        torques = []

        for name in self.joint_names:
            q = self.positions[name]
            dq = self.velocities[name]
            q_des = self.target_positions[name]
            tau_ff = self.feedforward_torques[name]

            if self.mode == 'position':
                # Pure position control
                tau = self.kp * (q_des - q) + self.kd * (0 - dq)
            else:
                # Torque mode: feedforward + PD stabilization
                tau = tau_ff + self.kp * (q_des - q) + self.kd * (0 - dq)

            # Safety limits
            tau = np.clip(tau, -30.0, 30.0)
            torques.append(tau)

        # Publish
        msg = Float64MultiArray()
        msg.data = torques
        self.effort_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = JointPDController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
