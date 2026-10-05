"""
dynamics_model.py - Single Rigid Body Dynamics for MPC

LEARNING OBJECTIVES:
- Understanding SRBD (Single Rigid Body Dynamics)
- Why quadrupeds use simplified models for control
- Linearization for convex optimization

SINGLE RIGID BODY DYNAMICS:
We model the quadruped as a single rigid body:
- Mass: m
- Inertia: I (3x3 matrix)
- State: [position, orientation, velocity, angular velocity]
- Control: Ground reaction forces at feet

This simplification ignores:
- Leg dynamics (assumed massless)
- Joint limits (handled by whole-body control)
- Detailed contact dynamics

WHY SRBD?
1. Computationally efficient (vs full dynamics)
2. Captures essential balance physics
3. MPC can run at high rate
4. Good enough for most locomotion tasks

EQUATIONS OF MOTION:
m * a = sum(F_i) - m * g           (Linear)
I * α + ω × (I * ω) = sum(r_i × F_i)  (Angular)

where F_i is ground reaction force at foot i
      r_i is foot position relative to CoM
"""

import numpy as np
from typing import Dict, List, Tuple


class SingleRigidBodyDynamics:
    """
    Single Rigid Body Dynamics model for quadruped MPC.

    State vector (13 states):
    x = [px, py, pz, roll, pitch, yaw, vx, vy, vz, wx, wy, wz, g]

    Note: g (gravity placeholder) is included for state-space form.

    Control vector (12 controls):
    u = [F_FL_x, F_FL_y, F_FL_z, F_FR_x, ..., F_RR_z]
    """

    def __init__(self,
                 mass: float = 12.0,
                 inertia: np.ndarray = None):
        """
        Initialize SRBD model.

        Args:
            mass: Robot mass (kg)
            inertia: 3x3 inertia tensor. If None, uses approximation.
        """
        self.mass = mass
        self.gravity = 9.81

        # Approximate inertia for box-shaped body
        if inertia is None:
            # I = m/12 * diag([h^2+d^2, w^2+d^2, w^2+h^2])
            # Assuming 0.4m long, 0.2m wide, 0.1m tall
            self.inertia = np.diag([
                mass / 12 * (0.2**2 + 0.1**2),  # Ixx
                mass / 12 * (0.4**2 + 0.1**2),  # Iyy
                mass / 12 * (0.4**2 + 0.2**2),  # Izz
            ])
        else:
            self.inertia = inertia

        self.inertia_inv = np.linalg.inv(self.inertia)

        # Number of states and controls
        self.n_states = 13
        self.n_controls = 12  # 4 feet * 3 force components

    def rotation_matrix_from_euler(self, roll: float, pitch: float, yaw: float) -> np.ndarray:
        """Compute rotation matrix from Euler angles (ZYX convention)."""
        cr, sr = np.cos(roll), np.sin(roll)
        cp, sp = np.cos(pitch), np.sin(pitch)
        cy, sy = np.cos(yaw), np.sin(yaw)

        return np.array([
            [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
            [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
            [-sp, cp*sr, cp*cr]
        ])

    def get_continuous_dynamics(self,
                                 state: np.ndarray,
                                 control: np.ndarray,
                                 foot_positions: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Compute state derivative: dx/dt = f(x, u).

        Args:
            state: Current state vector (13,)
            control: Control vector (12,) - forces at each foot
            foot_positions: Dict of foot positions relative to CoM

        Returns:
            State derivative (13,)
        """
        # Extract state
        pos = state[0:3]
        euler = state[3:6]  # roll, pitch, yaw
        vel = state[6:9]
        omega = state[9:12]

        # Rotation matrix
        R = self.rotation_matrix_from_euler(*euler)

        # Reshape control into foot forces
        forces = {
            'FL': control[0:3],
            'FR': control[3:6],
            'RL': control[6:9],
            'RR': control[9:12],
        }

        # Total force and moment
        total_force = np.zeros(3)
        total_moment = np.zeros(3)

        for leg, force in forces.items():
            if leg in foot_positions:
                r = foot_positions[leg]  # Foot position relative to CoM
                total_force += force
                total_moment += np.cross(r, force)

        # Gravity
        gravity_force = np.array([0, 0, -self.mass * self.gravity])
        total_force += gravity_force

        # Linear acceleration: a = F / m
        linear_accel = total_force / self.mass

        # Angular acceleration: I * α = τ - ω × (I * ω)
        omega_cross_I_omega = np.cross(omega, self.inertia @ omega)
        angular_accel = self.inertia_inv @ (total_moment - omega_cross_I_omega)

        # Euler rate from angular velocity (simplified for small angles)
        euler_rate = omega  # Approximation valid for small roll/pitch

        # State derivative
        dx = np.zeros(13)
        dx[0:3] = vel                # Position derivative = velocity
        dx[3:6] = euler_rate         # Euler derivative
        dx[6:9] = linear_accel       # Velocity derivative = acceleration
        dx[9:12] = angular_accel     # Angular velocity derivative
        dx[12] = 0                   # Gravity constant

        return dx

    def discretize(self, dt: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get linearized discrete-time A, B matrices.

        Linearized around hover state (standing still).

        Returns:
            A: State transition matrix (13x13)
            B: Control matrix (13x12)
        """
        # Simplified A matrix (hover linearization)
        A = np.eye(self.n_states)

        # Position integrates velocity
        A[0, 6] = dt
        A[1, 7] = dt
        A[2, 8] = dt

        # Orientation integrates angular velocity
        A[3, 9] = dt
        A[4, 10] = dt
        A[5, 11] = dt

        # Simplified B matrix
        B = np.zeros((self.n_states, self.n_controls))

        # Force affects velocity (F = ma)
        # Each foot contributes to linear velocity
        for i in range(4):  # 4 feet
            for j in range(3):  # x, y, z force
                col = i * 3 + j
                row = 6 + j  # velocity state
                B[row, col] = dt / self.mass

        # Torque affects angular velocity
        # Simplified: assume unit moment arms
        # Real implementation would use actual foot positions

        return A, B

    def get_friction_cone_constraints(self, mu: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate friction cone constraints for ground contact.

        Constraint: |F_xy| <= mu * F_z (linearized)

        Returns:
            C: Constraint matrix
            d: Constraint bounds (C @ u <= d)
        """
        # Linearized friction pyramid (4 faces per foot)
        # F_x <= mu * F_z
        # -F_x <= mu * F_z
        # F_y <= mu * F_z
        # -F_y <= mu * F_z
        # F_z >= 0

        constraints_per_foot = 5
        n_constraints = 4 * constraints_per_foot

        C = np.zeros((n_constraints, self.n_controls))
        d = np.zeros(n_constraints)

        for i in range(4):  # 4 feet
            base = i * 3
            row = i * constraints_per_foot

            # F_x - mu * F_z <= 0
            C[row, base + 0] = 1
            C[row, base + 2] = -mu

            # -F_x - mu * F_z <= 0
            C[row + 1, base + 0] = -1
            C[row + 1, base + 2] = -mu

            # F_y - mu * F_z <= 0
            C[row + 2, base + 1] = 1
            C[row + 2, base + 2] = -mu

            # -F_y - mu * F_z <= 0
            C[row + 3, base + 1] = -1
            C[row + 3, base + 2] = -mu

            # -F_z <= 0 (no pulling)
            C[row + 4, base + 2] = -1

        return C, d
