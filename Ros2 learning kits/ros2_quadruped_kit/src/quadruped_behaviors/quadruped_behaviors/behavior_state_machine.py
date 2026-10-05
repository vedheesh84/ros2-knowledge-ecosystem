#!/usr/bin/env python3
"""
behavior_state_machine.py - High-Level Behavior Management

LEARNING OBJECTIVES:
- Understanding behavior-level control
- State machine design for robots
- Recovery behavior design

BEHAVIOR HIERARCHY:
The behavior layer sits above locomotion:

User Commands → Behavior → Locomotion → Control → Hardware

Behaviors handle high-level decisions:
- When to walk vs stand
- How to recover from falls
- Emergency stops
- Mode transitions

STATE MACHINE:
IDLE → STANDING → WALKING/TROTTING → RECOVERY → IDLE
"""

from enum import Enum, auto
from typing import Optional

import numpy as np

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Bool
from sensor_msgs.msg import Imu


class BehaviorState(Enum):
    """Robot behavior states."""
    IDLE = auto()
    STANDING = auto()
    WALKING = auto()
    TROTTING = auto()
    RECOVERY = auto()
    EMERGENCY = auto()


class BehaviorStateMachine(Node):
    """
    High-level behavior state machine for quadruped.

    Manages transitions between behaviors based on:
    - User commands
    - Robot state (fallen, etc.)
    - Safety conditions

    Subscribes:
    - /cmd_vel: Velocity commands
    - /imu/data: Robot orientation
    - /behavior/command: Explicit behavior commands

    Publishes:
    - /behavior/state: Current behavior state
    - /gait/select: Gait selection for locomotion
    - /cmd_vel_filtered: Filtered velocity commands
    """

    def __init__(self):
        super().__init__('behavior_state_machine')

        # Parameters
        self.declare_parameter('fall_angle_threshold', 0.8)  # rad
        self.declare_parameter('velocity_threshold', 0.05)  # m/s

        self.fall_threshold = self.get_parameter('fall_angle_threshold').value
        self.vel_threshold = self.get_parameter('velocity_threshold').value

        # State
        self.current_state = BehaviorState.IDLE
        self.previous_state = BehaviorState.IDLE
        self.cmd_vel = Twist()
        self.roll = 0.0
        self.pitch = 0.0
        self.is_fallen = False

        # ==================== SUBSCRIBERS ====================
        self.cmd_vel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)
        self.command_sub = self.create_subscription(
            String, '/behavior/command', self.command_callback, 10)

        # ==================== PUBLISHERS ====================
        self.state_pub = self.create_publisher(String, '/behavior/state', 10)
        self.gait_pub = self.create_publisher(String, '/gait/select', 10)
        self.vel_pub = self.create_publisher(Twist, '/cmd_vel_filtered', 10)

        # State machine timer (50 Hz)
        self.create_timer(0.02, self.state_machine_loop)

        self.get_logger().info('Behavior State Machine initialized')

    def cmd_vel_callback(self, msg: Twist):
        """Store velocity command."""
        self.cmd_vel = msg

    def imu_callback(self, msg: Imu):
        """Update orientation and check for falls."""
        # Convert quaternion to roll/pitch
        q = msg.orientation
        self.roll, self.pitch, _ = self.quaternion_to_euler(q.x, q.y, q.z, q.w)

        # Check for fall
        self.is_fallen = (abs(self.roll) > self.fall_threshold or
                          abs(self.pitch) > self.fall_threshold)

    def command_callback(self, msg: String):
        """Handle explicit behavior commands."""
        cmd = msg.data.lower()

        if cmd == 'stand':
            self.transition_to(BehaviorState.STANDING)
        elif cmd == 'walk':
            self.transition_to(BehaviorState.WALKING)
        elif cmd == 'trot':
            self.transition_to(BehaviorState.TROTTING)
        elif cmd == 'stop':
            self.transition_to(BehaviorState.IDLE)
        elif cmd == 'recover':
            self.transition_to(BehaviorState.RECOVERY)

    def quaternion_to_euler(self, x, y, z, w):
        """Convert quaternion to Euler angles."""
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        pitch = np.arcsin(np.clip(sinp, -1, 1))

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw

    def transition_to(self, new_state: BehaviorState):
        """Transition to a new state."""
        if new_state != self.current_state:
            self.get_logger().info(
                f'Behavior transition: {self.current_state.name} -> {new_state.name}')
            self.previous_state = self.current_state
            self.current_state = new_state

    def state_machine_loop(self):
        """Main state machine loop."""
        # Emergency check (always active)
        if self.is_fallen and self.current_state != BehaviorState.RECOVERY:
            self.transition_to(BehaviorState.RECOVERY)

        # State-specific logic
        if self.current_state == BehaviorState.IDLE:
            self.handle_idle()
        elif self.current_state == BehaviorState.STANDING:
            self.handle_standing()
        elif self.current_state == BehaviorState.WALKING:
            self.handle_walking()
        elif self.current_state == BehaviorState.TROTTING:
            self.handle_trotting()
        elif self.current_state == BehaviorState.RECOVERY:
            self.handle_recovery()

        # Publish state
        state_msg = String()
        state_msg.data = self.current_state.name
        self.state_pub.publish(state_msg)

    def handle_idle(self):
        """IDLE state: Robot is powered but not active."""
        # Zero velocity
        self.publish_zero_velocity()

        # Transition to standing if commanded
        speed = np.sqrt(self.cmd_vel.linear.x**2 + self.cmd_vel.linear.y**2)
        if speed > self.vel_threshold:
            self.transition_to(BehaviorState.STANDING)

    def handle_standing(self):
        """STANDING state: Robot is standing, ready to move."""
        # Select stand gait
        gait_msg = String()
        gait_msg.data = 'stand'
        self.gait_pub.publish(gait_msg)

        # Zero velocity while standing
        self.publish_zero_velocity()

        # Transition to walking if commanded
        speed = np.sqrt(self.cmd_vel.linear.x**2 + self.cmd_vel.linear.y**2)
        if speed > self.vel_threshold:
            self.transition_to(BehaviorState.WALKING)

    def handle_walking(self):
        """WALKING state: Slow locomotion."""
        # Select walk gait
        gait_msg = String()
        gait_msg.data = 'walk'
        self.gait_pub.publish(gait_msg)

        # Pass through velocity (limited)
        vel = Twist()
        vel.linear.x = np.clip(self.cmd_vel.linear.x, -0.3, 0.3)
        vel.linear.y = np.clip(self.cmd_vel.linear.y, -0.2, 0.2)
        vel.angular.z = np.clip(self.cmd_vel.angular.z, -0.5, 0.5)
        self.vel_pub.publish(vel)

        # Transition to standing if stopped
        speed = np.sqrt(self.cmd_vel.linear.x**2 + self.cmd_vel.linear.y**2)
        if speed < self.vel_threshold and abs(self.cmd_vel.angular.z) < self.vel_threshold:
            self.transition_to(BehaviorState.STANDING)

        # Transition to trot if faster
        if speed > 0.25:
            self.transition_to(BehaviorState.TROTTING)

    def handle_trotting(self):
        """TROTTING state: Fast locomotion."""
        # Select trot gait
        gait_msg = String()
        gait_msg.data = 'trot'
        self.gait_pub.publish(gait_msg)

        # Pass through velocity (higher limits)
        vel = Twist()
        vel.linear.x = np.clip(self.cmd_vel.linear.x, -1.0, 1.0)
        vel.linear.y = np.clip(self.cmd_vel.linear.y, -0.5, 0.5)
        vel.angular.z = np.clip(self.cmd_vel.angular.z, -1.0, 1.0)
        self.vel_pub.publish(vel)

        # Transition to walking if slower
        speed = np.sqrt(self.cmd_vel.linear.x**2 + self.cmd_vel.linear.y**2)
        if speed < 0.2:
            self.transition_to(BehaviorState.WALKING)

    def handle_recovery(self):
        """RECOVERY state: Attempt to recover from fall."""
        self.get_logger().info('Executing recovery behavior...')

        # Zero velocity during recovery
        self.publish_zero_velocity()

        # Check if recovered
        if not self.is_fallen:
            self.get_logger().info('Recovery successful!')
            self.transition_to(BehaviorState.STANDING)

    def publish_zero_velocity(self):
        """Publish zero velocity command."""
        vel = Twist()
        self.vel_pub.publish(vel)


def main(args=None):
    rclpy.init(args=args)
    node = BehaviorStateMachine()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
