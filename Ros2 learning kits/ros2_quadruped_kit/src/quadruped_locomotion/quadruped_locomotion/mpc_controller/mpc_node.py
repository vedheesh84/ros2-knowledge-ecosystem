#!/usr/bin/env python3
"""
mpc_node.py - Model Predictive Controller for Quadruped

LEARNING OBJECTIVES:
- Understanding MPC for legged robots
- Convex optimization for real-time control
- Prediction horizon and receding horizon control

MPC OVERVIEW:
At each timestep, MPC:
1. Gets current state from estimator
2. Predicts future states over horizon
3. Optimizes control inputs to minimize cost
4. Applies first control, discards rest
5. Repeat (receding horizon)

OPTIMIZATION PROBLEM:
minimize: sum over horizon of (state cost + control cost)
subject to:
  - Dynamics constraints
  - Friction cone constraints
  - Force limits
  - Contact schedule

This uses a simplified QP formulation.
Production systems use osqp/qpOASES for real-time performance.
"""

import numpy as np
from typing import Dict, Optional

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64MultiArray

from .dynamics_model import SingleRigidBodyDynamics


class MPCController(Node):
    """
    Model Predictive Controller for quadruped locomotion.

    Computes optimal ground reaction forces for each foot
    to track desired velocity while maintaining balance.

    Subscribes:
    - /odom: Current state from estimator
    - /cmd_vel: Desired velocity
    - /gait/contact_schedule: Which feet are in contact

    Publishes:
    - /mpc/forces: Optimal ground reaction forces
    """

    def __init__(self):
        super().__init__('mpc_controller')

        # Parameters
        self.declare_parameter('horizon', 10)
        self.declare_parameter('dt', 0.03)  # 33 Hz MPC
        self.declare_parameter('friction_coef', 0.5)
        self.declare_parameter('max_force', 150.0)  # N per foot

        self.horizon = self.get_parameter('horizon').value
        self.dt = self.get_parameter('dt').value
        self.mu = self.get_parameter('friction_coef').value
        self.max_force = self.get_parameter('max_force').value

        # Dynamics model
        self.dynamics = SingleRigidBodyDynamics(mass=12.0)

        # State and command
        self.current_state = np.zeros(13)
        self.current_state[12] = 9.81  # Gravity
        self.cmd_vel = np.zeros(3)  # [vx, vy, wz]

        # Contact schedule
        self.contact_state = {'FL': True, 'FR': True, 'RL': True, 'RR': True}

        # Foot positions (relative to CoM, in body frame)
        self.foot_positions = {
            'FL': np.array([0.15, -0.16, -0.35]),
            'FR': np.array([0.15, 0.16, -0.35]),
            'RL': np.array([-0.15, -0.16, -0.35]),
            'RR': np.array([-0.15, 0.16, -0.35]),
        }

        # MPC weights
        self.Q = np.diag([
            0.0, 0.0, 100.0,     # Position (only penalize z deviation)
            100.0, 100.0, 0.0,   # Orientation (penalize roll/pitch)
            10.0, 10.0, 1.0,     # Velocity (track cmd_vel)
            1.0, 1.0, 10.0,      # Angular velocity
            0.0                   # Gravity (don't penalize)
        ])
        self.R = np.eye(12) * 0.001  # Control effort

        # ==================== SUBSCRIBERS ====================
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.contact_sub = self.create_subscription(
            Float64MultiArray, '/gait/contact_schedule', self.contact_callback, 10)

        # ==================== PUBLISHERS ====================
        self.force_pub = self.create_publisher(
            Float64MultiArray, '/mpc/forces', 10)

        # MPC timer (runs at 1/dt Hz)
        self.create_timer(self.dt, self.run_mpc)

        self.get_logger().info(f'MPC Controller initialized (horizon={self.horizon}, dt={self.dt})')

    def odom_callback(self, msg: Odometry):
        """Update current state from odometry."""
        # Position
        self.current_state[0] = msg.pose.pose.position.x
        self.current_state[1] = msg.pose.pose.position.y
        self.current_state[2] = msg.pose.pose.position.z

        # Orientation (quaternion to Euler)
        q = msg.pose.pose.orientation
        roll, pitch, yaw = self.quaternion_to_euler(q.x, q.y, q.z, q.w)
        self.current_state[3] = roll
        self.current_state[4] = pitch
        self.current_state[5] = yaw

        # Velocity
        self.current_state[6] = msg.twist.twist.linear.x
        self.current_state[7] = msg.twist.twist.linear.y
        self.current_state[8] = msg.twist.twist.linear.z
        self.current_state[9] = msg.twist.twist.angular.x
        self.current_state[10] = msg.twist.twist.angular.y
        self.current_state[11] = msg.twist.twist.angular.z

    def cmd_vel_callback(self, msg: Twist):
        """Update commanded velocity."""
        self.cmd_vel[0] = msg.linear.x
        self.cmd_vel[1] = msg.linear.y
        self.cmd_vel[2] = msg.angular.z

    def contact_callback(self, msg: Float64MultiArray):
        """Update contact schedule."""
        if len(msg.data) >= 4:
            self.contact_state['FL'] = msg.data[0] > 0.5
            self.contact_state['FR'] = msg.data[1] > 0.5
            self.contact_state['RL'] = msg.data[2] > 0.5
            self.contact_state['RR'] = msg.data[3] > 0.5

    def quaternion_to_euler(self, x, y, z, w):
        """Convert quaternion to Euler angles (roll, pitch, yaw)."""
        # Roll
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        # Pitch
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = np.copysign(np.pi / 2, sinp)
        else:
            pitch = np.arcsin(sinp)

        # Yaw
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw

    def run_mpc(self):
        """
        Run MPC optimization and publish forces.

        Simplified MPC using analytical solution for demonstration.
        Production systems would use QP solver (osqp, qpOASES).
        """
        # Count feet in contact
        n_contact = sum(1 for c in self.contact_state.values() if c)

        if n_contact == 0:
            # No contact - can't apply forces
            forces = np.zeros(12)
        else:
            # Compute desired accelerations
            forces = self.compute_qp_forces(n_contact)

        # Publish forces
        msg = Float64MultiArray()
        msg.data = forces.tolist()
        self.force_pub.publish(msg)

    def compute_qp_forces(self, n_contact: int) -> np.ndarray:
        """
        Compute optimal forces using simplified QP.

        For learning purposes, this uses an analytical approximation.
        Real MPC would formulate and solve a QP problem.

        The solution balances:
        1. Supporting robot weight (F_z = mg / n_contact per foot)
        2. Correcting orientation (torque from off-center forces)
        3. Tracking velocity (horizontal forces)
        """
        forces = np.zeros(12)

        # Robot weight per contacting foot
        weight_per_foot = self.dynamics.mass * self.dynamics.gravity / n_contact

        # Desired velocity error
        vel_error = np.array([
            self.cmd_vel[0] - self.current_state[6],  # vx error
            self.cmd_vel[1] - self.current_state[7],  # vy error
            0.0,  # vz (maintain height)
        ])

        # Orientation error (try to stay level)
        roll_error = -self.current_state[3]
        pitch_error = -self.current_state[4]

        # PD gains for force computation
        kp_vel = 50.0
        kp_roll = 100.0
        kp_pitch = 100.0

        legs = ['FL', 'FR', 'RL', 'RR']

        for i, leg in enumerate(legs):
            if not self.contact_state[leg]:
                continue  # No force if not in contact

            base = i * 3

            # Base vertical force (support weight)
            forces[base + 2] = weight_per_foot

            # Horizontal forces for velocity tracking
            forces[base + 0] = kp_vel * vel_error[0] / n_contact
            forces[base + 1] = kp_vel * vel_error[1] / n_contact

            # Orientation correction via differential vertical forces
            foot_pos = self.foot_positions[leg]

            # Roll correction: left feet push more when rolling right
            if foot_pos[1] < 0:  # Left side
                forces[base + 2] += kp_roll * roll_error
            else:  # Right side
                forces[base + 2] -= kp_roll * roll_error

            # Pitch correction: front feet push more when pitching back
            if foot_pos[0] > 0:  # Front
                forces[base + 2] += kp_pitch * pitch_error
            else:  # Rear
                forces[base + 2] -= kp_pitch * pitch_error

            # Apply friction cone limits
            fz = max(forces[base + 2], 0.0)  # No pulling
            fx_limit = self.mu * fz
            fy_limit = self.mu * fz

            forces[base + 0] = np.clip(forces[base + 0], -fx_limit, fx_limit)
            forces[base + 1] = np.clip(forces[base + 1], -fy_limit, fy_limit)
            forces[base + 2] = np.clip(fz, 0, self.max_force)

        return forces


def main(args=None):
    rclpy.init(args=args)
    node = MPCController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
