#!/usr/bin/env python3
"""
swing_trajectory.py - Swing Leg Trajectory Generation

LEARNING OBJECTIVES:
- Bezier curve trajectories for smooth motion
- Foot clearance and landing control
- Velocity matching at touchdown

SWING TRAJECTORY DESIGN:
The foot follows a 3D trajectory during swing phase:
1. Lift off from current position
2. Rise to clearance height
3. Move forward toward target
4. Descend to landing position
5. Touch down with near-zero velocity

Bezier curves provide:
- Smooth position profiles
- Controllable velocity at endpoints
- Easy height and length parameterization
"""

import numpy as np
from typing import Tuple

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Point, Vector3


def cubic_bezier(t: float, p0: float, p1: float, p2: float, p3: float) -> float:
    """
    Evaluate cubic Bezier curve at parameter t.

    P(t) = (1-t)^3 * P0 + 3*(1-t)^2*t * P1 + 3*(1-t)*t^2 * P2 + t^3 * P3
    """
    t1 = 1.0 - t
    return (t1**3 * p0 +
            3 * t1**2 * t * p1 +
            3 * t1 * t**2 * p2 +
            t**3 * p3)


def cubic_bezier_derivative(t: float, p0: float, p1: float, p2: float, p3: float) -> float:
    """
    Evaluate derivative of cubic Bezier curve at parameter t.

    P'(t) = 3*(1-t)^2*(P1-P0) + 6*(1-t)*t*(P2-P1) + 3*t^2*(P3-P2)
    """
    t1 = 1.0 - t
    return (3 * t1**2 * (p1 - p0) +
            6 * t1 * t * (p2 - p1) +
            3 * t**2 * (p3 - p2))


class SwingTrajectory:
    """
    Generate swing trajectories using Bezier curves.

    Parameters:
    - swing_height: Maximum foot clearance (m)
    - step_length: Forward step distance (m)
    """

    def __init__(self,
                 swing_height: float = 0.08,
                 landing_height_offset: float = -0.01):
        """
        Initialize swing trajectory generator.

        Args:
            swing_height: Peak height of swing arc (m)
            landing_height_offset: Lower target slightly for ground detection (m)
        """
        self.swing_height = swing_height
        self.landing_offset = landing_height_offset

    def compute_trajectory(self,
                           start_pos: np.ndarray,
                           target_pos: np.ndarray,
                           phase: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute foot position and velocity at given swing phase.

        Args:
            start_pos: Foot position at lift-off [x, y, z]
            target_pos: Foot target position at touchdown [x, y, z]
            phase: Normalized swing phase [0, 1]

        Returns:
            (position, velocity): 3D position and velocity at phase
        """
        # Clamp phase
        phase = np.clip(phase, 0.0, 1.0)

        # X-Y trajectory: straight line with smooth acceleration
        # Using cubic Bezier for smooth start/end velocities
        # Control points for x/y: linear interpolation
        x_pos = cubic_bezier(phase,
                             start_pos[0],
                             start_pos[0] + 0.3 * (target_pos[0] - start_pos[0]),
                             start_pos[0] + 0.7 * (target_pos[0] - start_pos[0]),
                             target_pos[0])
        y_pos = cubic_bezier(phase,
                             start_pos[1],
                             start_pos[1] + 0.3 * (target_pos[1] - start_pos[1]),
                             start_pos[1] + 0.7 * (target_pos[1] - start_pos[1]),
                             target_pos[1])

        # Z trajectory: lift, peak, lower
        # Bezier control points for parabolic-like arc
        z_start = start_pos[2]
        z_end = target_pos[2] + self.landing_offset
        z_peak = max(z_start, z_end) + self.swing_height

        # 4-point Bezier for height
        z_pos = cubic_bezier(phase,
                             z_start,
                             z_peak,
                             z_peak,
                             z_end)

        # Compute velocities
        x_vel = cubic_bezier_derivative(phase,
                                        start_pos[0],
                                        start_pos[0] + 0.3 * (target_pos[0] - start_pos[0]),
                                        start_pos[0] + 0.7 * (target_pos[0] - start_pos[0]),
                                        target_pos[0])
        y_vel = cubic_bezier_derivative(phase,
                                        start_pos[1],
                                        start_pos[1] + 0.3 * (target_pos[1] - start_pos[1]),
                                        start_pos[1] + 0.7 * (target_pos[1] - start_pos[1]),
                                        target_pos[1])
        z_vel = cubic_bezier_derivative(phase, z_start, z_peak, z_peak, z_end)

        position = np.array([x_pos, y_pos, z_pos])
        velocity = np.array([x_vel, y_vel, z_vel])

        return position, velocity


class SwingTrajectoryNode(Node):
    """
    ROS 2 node for swing trajectory generation.

    Subscribes:
    - /gait/phase: Current leg phases
    - /gait/contact_schedule: Which legs are in stance

    Publishes:
    - /swing/foot_targets: Target positions for swing feet
    """

    def __init__(self):
        super().__init__('swing_trajectory')

        # Parameters
        self.declare_parameter('swing_height', 0.08)
        self.declare_parameter('default_step_length', 0.1)

        swing_height = self.get_parameter('swing_height').value
        self.step_length = self.get_parameter('default_step_length').value

        self.trajectory_gen = SwingTrajectory(swing_height=swing_height)

        # Leg default positions (in body frame)
        self.default_positions = {
            'FL': np.array([0.15, -0.16, -0.35]),
            'FR': np.array([0.15, 0.16, -0.35]),
            'RL': np.array([-0.15, -0.16, -0.35]),
            'RR': np.array([-0.15, 0.16, -0.35]),
        }

        # Current foot positions (updated during stance)
        self.foot_positions = {leg: pos.copy() for leg, pos in self.default_positions.items()}

        # Lift-off positions (stored at start of swing)
        self.liftoff_positions = {leg: pos.copy() for leg, pos in self.default_positions.items()}

        # Phase storage
        self.leg_phases = {'FL': 0.0, 'FR': 0.0, 'RL': 0.0, 'RR': 0.0}
        self.contact_state = {'FL': True, 'FR': True, 'RL': True, 'RR': True}
        self.prev_contact = {'FL': True, 'FR': True, 'RL': True, 'RR': True}

        # Commanded velocity
        self.cmd_vel_x = 0.0
        self.cmd_vel_y = 0.0
        self.cmd_vel_yaw = 0.0

        # ==================== SUBSCRIBERS ====================
        self.phase_sub = self.create_subscription(
            Float64MultiArray, '/gait/phase', self.phase_callback, 10)
        self.contact_sub = self.create_subscription(
            Float64MultiArray, '/gait/contact_schedule', self.contact_callback, 10)

        # ==================== PUBLISHERS ====================
        self.target_pub = self.create_publisher(
            Float64MultiArray, '/swing/foot_targets', 10)

        # Timer
        self.create_timer(0.01, self.compute_swing_targets)

        self.get_logger().info('Swing Trajectory Node initialized')

    def phase_callback(self, msg: Float64MultiArray):
        """Update leg phases."""
        if len(msg.data) >= 4:
            self.leg_phases['FL'] = msg.data[0]
            self.leg_phases['FR'] = msg.data[1]
            self.leg_phases['RL'] = msg.data[2]
            self.leg_phases['RR'] = msg.data[3]

    def contact_callback(self, msg: Float64MultiArray):
        """Update contact schedule."""
        if len(msg.data) >= 4:
            self.contact_state['FL'] = msg.data[0] > 0.5
            self.contact_state['FR'] = msg.data[1] > 0.5
            self.contact_state['RL'] = msg.data[2] > 0.5
            self.contact_state['RR'] = msg.data[3] > 0.5

    def compute_swing_targets(self):
        """Compute target positions for swing legs."""
        legs = ['FL', 'FR', 'RL', 'RR']
        targets = []

        for leg in legs:
            # Detect lift-off transition
            if self.prev_contact[leg] and not self.contact_state[leg]:
                self.liftoff_positions[leg] = self.foot_positions[leg].copy()

            self.prev_contact[leg] = self.contact_state[leg]

            if self.contact_state[leg]:
                # Stance: target is current position (foot stays put)
                target = self.foot_positions[leg]
            else:
                # Swing: compute trajectory target
                start = self.liftoff_positions[leg]

                # Target is step forward from default position
                target_pos = self.default_positions[leg].copy()
                target_pos[0] += self.step_length * self.cmd_vel_x
                target_pos[1] += self.step_length * self.cmd_vel_y

                # Get swing phase (0 = just lifted, 1 = about to land)
                # Phase from gait scheduler is global, we need swing progress
                duty = 0.5  # Approximate
                swing_duration = 1.0 - duty
                swing_progress = self.leg_phases[leg] / swing_duration
                swing_progress = np.clip(swing_progress, 0.0, 1.0)

                target, _ = self.trajectory_gen.compute_trajectory(
                    start, target_pos, swing_progress)

            targets.extend(target.tolist())

        # Publish [FL_x, FL_y, FL_z, FR_x, FR_y, FR_z, RL_x, RL_y, RL_z, RR_x, RR_y, RR_z]
        msg = Float64MultiArray()
        msg.data = targets
        self.target_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SwingTrajectoryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
