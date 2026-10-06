#!/usr/bin/env python3
"""
thruster_allocator.py - Thruster Allocation Matrix

THRUSTER ALLOCATION PROBLEM:
============================
Given a desired force/torque vector τ, find thruster commands u.

  τ = B * u

Where:
  τ = [Fx, Fy, Fz, Tx, Ty, Tz]  (6x1 desired forces/torques)
  u = [u1, u2, u3, u4, u5, u6]  (6x1 thruster commands)
  B = Configuration matrix       (6x6 for our vehicle)

CONFIGURATION MATRIX B:
=======================
Each column of B describes how one thruster affects all 6 DOF.

For thruster i at position p_i with thrust direction d_i:
  Force contribution:  F_i = T_i * d_i
  Torque contribution: T_i = p_i × (T_i * d_i)

So column i of B is:
  B[:, i] = [d_ix, d_iy, d_iz, (p_i × d_i)_x, (p_i × d_i)_y, (p_i × d_i)_z]

BLUEROV2 6-THRUSTER CONFIGURATION:
==================================
Horizontal thrusters at 45° (vectored):
  T1: pos=[0.12, -0.12, 0], dir=[0.707, 0.707, 0]  (fwd-right)
  T2: pos=[0.12, 0.12, 0], dir=[0.707, -0.707, 0]  (fwd-left)
  T3: pos=[-0.12, -0.12, 0], dir=[0.707, -0.707, 0] (fwd-left)
  T4: pos=[-0.12, 0.12, 0], dir=[0.707, 0.707, 0]  (fwd-right)

Vertical thrusters:
  T5: pos=[0, -0.10, 0.05], dir=[0, 0, 1]  (up)
  T6: pos=[0, 0.10, 0.05], dir=[0, 0, 1]   (up)

SOLVING FOR THRUSTER COMMANDS:
==============================
  u = B⁺ * τ

Where B⁺ is the pseudoinverse of B.

If B is square and full rank: B⁺ = B⁻¹
Otherwise: B⁺ = (B^T * B)⁻¹ * B^T

SATURATION HANDLING:
====================
After computing u, check if any |u_i| > 1.
If so, scale all commands by max(|u|) to preserve direction.

Topics:
  Subscribe: /control/wrench (geometry_msgs/Wrench)
  Publish: /thrusters/cmd (std_msgs/Float64MultiArray)
"""

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Wrench
from std_msgs.msg import Float64MultiArray


class ThrusterAllocator(Node):
    """Converts force/torque commands to thruster commands."""

    def __init__(self):
        super().__init__('thruster_allocator')

        # Parameters
        self.declare_parameter('max_thrust', 50.0)  # N per thruster

        self.max_thrust = self.get_parameter('max_thrust').value

        # Build configuration matrix B
        self.B = self._build_configuration_matrix()
        self.get_logger().info(f'Configuration matrix B:\n{self.B}')

        # Compute pseudoinverse
        self.B_pinv = np.linalg.pinv(self.B)
        self.get_logger().info(f'Pseudoinverse B+:\n{self.B_pinv}')

        # Subscriber for desired wrench
        self.wrench_sub = self.create_subscription(
            Wrench, '/control/wrench', self.wrench_callback, 10)

        # Publisher for thruster commands
        self.cmd_pub = self.create_publisher(
            Float64MultiArray, '/thrusters/cmd', 10)

        self.get_logger().info('Thruster Allocator started')

    def _build_configuration_matrix(self) -> np.ndarray:
        """
        Build the 6x6 thruster configuration matrix.

        Each column is [Fx, Fy, Fz, Tx, Ty, Tz] contribution
        from that thruster at unit thrust.
        """
        # Thruster positions (m) relative to CoM
        # [x, y, z] in body frame
        positions = np.array([
            [0.12, -0.12, 0.0],   # T1: front-left
            [0.12, 0.12, 0.0],    # T2: front-right
            [-0.12, -0.12, 0.0],  # T3: rear-left
            [-0.12, 0.12, 0.0],   # T4: rear-right
            [0.0, -0.10, 0.05],   # T5: vertical-left
            [0.0, 0.10, 0.05],    # T6: vertical-right
        ])

        # Thruster directions (unit vectors)
        # Direction of positive thrust in body frame
        sqrt2_2 = np.sqrt(2) / 2  # ~0.707
        directions = np.array([
            [sqrt2_2, sqrt2_2, 0.0],    # T1: forward-right
            [sqrt2_2, -sqrt2_2, 0.0],   # T2: forward-left
            [sqrt2_2, -sqrt2_2, 0.0],   # T3: forward-left
            [sqrt2_2, sqrt2_2, 0.0],    # T4: forward-right
            [0.0, 0.0, 1.0],            # T5: up
            [0.0, 0.0, 1.0],            # T6: up
        ])

        # Build B matrix (6 DOF x 6 thrusters)
        B = np.zeros((6, 6))

        for i in range(6):
            p = positions[i]
            d = directions[i]

            # Force contribution (rows 0-2)
            B[0:3, i] = d

            # Torque contribution (rows 3-5): torque = position × force
            B[3:6, i] = np.cross(p, d)

        return B

    def wrench_callback(self, msg: Wrench):
        """
        Convert desired wrench to thruster commands.

        Wrench: [force.x, force.y, force.z, torque.x, torque.y, torque.z]
        """
        # Extract desired forces and torques
        tau = np.array([
            msg.force.x,
            msg.force.y,
            msg.force.z,
            msg.torque.x,
            msg.torque.y,
            msg.torque.z
        ])

        # Compute thruster forces: u = B+ * tau
        thruster_forces = self.B_pinv @ tau

        # Convert forces to normalized commands [-1, 1]
        # Command = force / max_thrust
        commands = thruster_forces / self.max_thrust

        # Handle saturation: if any |cmd| > 1, scale all
        max_cmd = np.max(np.abs(commands))
        if max_cmd > 1.0:
            commands = commands / max_cmd
            self.get_logger().debug(f'Thruster saturation: scaled by {1/max_cmd:.2f}')

        # Publish commands
        cmd_msg = Float64MultiArray()
        cmd_msg.data = commands.tolist()
        self.cmd_pub.publish(cmd_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ThrusterAllocator()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException, Exception):
        pass
    finally:
        try:
            node.destroy_node()
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
