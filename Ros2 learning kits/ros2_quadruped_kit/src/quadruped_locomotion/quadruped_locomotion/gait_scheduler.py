#!/usr/bin/env python3
"""
gait_scheduler.py - Gait Pattern Generation for Quadruped

LEARNING OBJECTIVES:
- Understanding gait patterns (walk, trot, bound, gallop)
- Phase-based gait scheduling
- Contact sequence timing

GAIT DEFINITIONS:
- Walk: Only one leg swings at a time (most stable, slowest)
- Trot: Diagonal legs swing together (balance of speed/stability)
- Bound: Front legs together, rear legs together (fast)
- Gallop: Sequential front-rear pattern (fastest, least stable)

PHASE EXPLANATION:
Each leg has a phase φ ∈ [0, 1) in the gait cycle:
- φ = 0: Start of swing phase
- φ = duty_factor: End of swing, start of stance
- φ = 1: Cycle repeats

Duty factor = fraction of cycle in stance phase (typically 0.5-0.7)
"""

import numpy as np
from enum import Enum
from typing import Dict, List, Tuple
from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64MultiArray
from geometry_msgs.msg import Twist


class GaitType(Enum):
    """Available gait patterns."""
    STAND = 0
    WALK = 1
    TROT = 2
    BOUND = 3


@dataclass
class GaitParams:
    """Parameters defining a gait pattern."""
    name: str
    period: float  # Gait cycle duration (seconds)
    duty_factor: float  # Fraction of cycle in stance
    phase_offsets: Dict[str, float]  # Phase offset for each leg


# Predefined gait patterns
GAITS = {
    GaitType.STAND: GaitParams(
        name='stand',
        period=1.0,
        duty_factor=1.0,  # All legs always in stance
        phase_offsets={'FL': 0.0, 'FR': 0.0, 'RL': 0.0, 'RR': 0.0}
    ),
    GaitType.WALK: GaitParams(
        name='walk',
        period=1.0,
        duty_factor=0.75,  # 75% stance, 25% swing
        phase_offsets={'FL': 0.0, 'FR': 0.5, 'RL': 0.25, 'RR': 0.75}
    ),
    GaitType.TROT: GaitParams(
        name='trot',
        period=0.5,
        duty_factor=0.5,  # 50% stance, 50% swing
        phase_offsets={'FL': 0.0, 'FR': 0.5, 'RL': 0.5, 'RR': 0.0}
    ),
    GaitType.BOUND: GaitParams(
        name='bound',
        period=0.4,
        duty_factor=0.4,  # 40% stance, 60% swing
        phase_offsets={'FL': 0.0, 'FR': 0.0, 'RL': 0.5, 'RR': 0.5}
    ),
}


class GaitScheduler(Node):
    """
    Generates gait schedules based on commanded velocity.

    Subscribes:
    - /cmd_vel: Velocity commands

    Publishes:
    - /gait/contact_schedule: Which legs should be in contact
    - /gait/phase: Current phase of each leg
    - /gait/swing_targets: Target foot positions for swing legs
    """

    def __init__(self):
        super().__init__('gait_scheduler')

        # Parameters
        self.declare_parameter('default_gait', 'trot')
        self.declare_parameter('velocity_threshold', 0.05)  # m/s

        # State
        self.current_gait = GaitType.STAND
        self.gait_phase = 0.0  # Master phase [0, 1)
        self.leg_phases = {'FL': 0.0, 'FR': 0.0, 'RL': 0.0, 'RR': 0.0}
        self.contact_state = {'FL': True, 'FR': True, 'RL': True, 'RR': True}

        # Commanded velocity
        self.cmd_vel = Twist()

        # ==================== SUBSCRIBERS ====================
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)

        self.gait_sub = self.create_subscription(
            String, '/gait/select', self.gait_select_callback, 10)

        # ==================== PUBLISHERS ====================
        self.contact_pub = self.create_publisher(
            Float64MultiArray, '/gait/contact_schedule', 10)
        self.phase_pub = self.create_publisher(
            Float64MultiArray, '/gait/phase', 10)

        # Timer for gait updates (100 Hz)
        self.create_timer(0.01, self.update_gait)
        self.last_update = self.get_clock().now()

        self.get_logger().info('Gait Scheduler initialized')

    def cmd_vel_callback(self, msg: Twist):
        """Store commanded velocity."""
        self.cmd_vel = msg

        # Auto-select gait based on speed
        speed = np.sqrt(msg.linear.x**2 + msg.linear.y**2)
        threshold = self.get_parameter('velocity_threshold').value

        if speed < threshold and abs(msg.angular.z) < threshold:
            self.current_gait = GaitType.STAND
        elif speed < 0.3:
            self.current_gait = GaitType.WALK
        else:
            self.current_gait = GaitType.TROT

    def gait_select_callback(self, msg: String):
        """Manually select gait pattern."""
        gait_name = msg.data.lower()
        for gait_type in GaitType:
            if gait_type.name.lower() == gait_name:
                self.current_gait = gait_type
                self.get_logger().info(f'Gait changed to: {gait_name}')
                return
        self.get_logger().warn(f'Unknown gait: {gait_name}')

    def update_gait(self):
        """Update gait phase and contact schedule."""
        current_time = self.get_clock().now()
        dt = (current_time - self.last_update).nanoseconds * 1e-9
        self.last_update = current_time

        gait_params = GAITS[self.current_gait]

        # Update master phase
        if gait_params.period > 0:
            self.gait_phase += dt / gait_params.period
            self.gait_phase = self.gait_phase % 1.0

        # Compute leg phases and contact states
        for leg in ['FL', 'FR', 'RL', 'RR']:
            # Leg phase = master phase + offset
            leg_phase = (self.gait_phase + gait_params.phase_offsets[leg]) % 1.0
            self.leg_phases[leg] = leg_phase

            # Contact = in stance portion of cycle
            # Swing phase: 0 to (1 - duty_factor)
            # Stance phase: (1 - duty_factor) to 1
            swing_duration = 1.0 - gait_params.duty_factor
            self.contact_state[leg] = leg_phase >= swing_duration

        # Publish contact schedule [FL, FR, RL, RR]
        contact_msg = Float64MultiArray()
        contact_msg.data = [
            1.0 if self.contact_state['FL'] else 0.0,
            1.0 if self.contact_state['FR'] else 0.0,
            1.0 if self.contact_state['RL'] else 0.0,
            1.0 if self.contact_state['RR'] else 0.0,
        ]
        self.contact_pub.publish(contact_msg)

        # Publish phases
        phase_msg = Float64MultiArray()
        phase_msg.data = [
            self.leg_phases['FL'],
            self.leg_phases['FR'],
            self.leg_phases['RL'],
            self.leg_phases['RR'],
        ]
        self.phase_pub.publish(phase_msg)

    def get_swing_progress(self, leg: str) -> float:
        """
        Get normalized progress through swing phase [0, 1].

        Returns 0 if leg is in stance.
        """
        gait_params = GAITS[self.current_gait]
        swing_duration = 1.0 - gait_params.duty_factor

        if self.contact_state[leg]:
            return 0.0  # In stance

        # Normalize swing phase to [0, 1]
        return self.leg_phases[leg] / swing_duration


def main(args=None):
    rclpy.init(args=args)
    node = GaitScheduler()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
