#!/usr/bin/env python3
"""
velocity_controller.py - PID Velocity Controller

VELOCITY CONTROL PROBLEM:
=========================
Track a desired velocity vector using thrust forces.

USE CASES:
----------
1. Manual velocity commands (joystick)
2. Output from position controller (cascaded control)
3. Waypoint tracking (velocity toward goal)

SYSTEM DYNAMICS:
----------------
Velocity dynamics (simplified):

  m * v_dot = F_thrust - F_drag

At steady state (v_dot = 0):
  F_thrust = F_drag

For quadratic drag:
  F_thrust = D * |v| * v

FEEDFORWARD + FEEDBACK:
=======================
For better tracking, combine:
1. Feedforward: F_ff = D * |v_des| * v_des (compensate expected drag)
2. Feedback:    F_fb = Kp * e + Ki * ∫e dt (correct errors)

Total: F = F_ff + F_fb

Topics:
  Subscribe: /dvl/velocity (geometry_msgs/TwistWithCovarianceStamped)
  Subscribe: /cmd_vel (geometry_msgs/Twist) - desired velocity
  Publish: /control/wrench (geometry_msgs/Wrench)
"""

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistWithCovarianceStamped, Wrench


class VelocityController(Node):
    """PI controller for velocity tracking."""

    def __init__(self):
        super().__init__('velocity_controller')

        # Parameters
        self.declare_parameter('kp', 30.0)  # N/(m/s)
        self.declare_parameter('ki', 3.0)   # N/m
        self.declare_parameter('max_force', 150.0)  # N
        self.declare_parameter('integral_limit', 10.0)  # m

        # Drag coefficients for feedforward
        self.declare_parameter('drag_x', 20.0)  # N·s²/m²
        self.declare_parameter('drag_y', 40.0)
        self.declare_parameter('drag_z', 40.0)

        self.kp = self.get_parameter('kp').value
        self.ki = self.get_parameter('ki').value
        self.max_force = self.get_parameter('max_force').value
        self.integral_limit = self.get_parameter('integral_limit').value

        self.drag = np.array([
            self.get_parameter('drag_x').value,
            self.get_parameter('drag_y').value,
            self.get_parameter('drag_z').value
        ])

        # State
        self.vel_setpoint = np.zeros(3)
        self.current_vel = np.zeros(3)
        self.integral = np.zeros(3)
        self.last_time = self.get_clock().now()

        # Subscribers
        self.vel_sub = self.create_subscription(
            TwistWithCovarianceStamped, '/dvl/velocity', self.vel_callback, 10)
        self.cmd_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_callback, 10)

        # Publisher
        self.wrench_pub = self.create_publisher(Wrench, '/control/wrench', 10)

        # Control loop timer (50 Hz)
        self.timer = self.create_timer(0.02, self.control_loop)

        self.get_logger().info(
            f'Velocity Controller started: Kp={self.kp}, Ki={self.ki}')

    def vel_callback(self, msg: TwistWithCovarianceStamped):
        """Update current velocity from DVL."""
        self.current_vel = np.array([
            msg.twist.twist.linear.x,
            msg.twist.twist.linear.y,
            msg.twist.twist.linear.z
        ])

    def cmd_callback(self, msg: Twist):
        """Update velocity setpoint."""
        self.vel_setpoint = np.array([
            msg.linear.x,
            msg.linear.y,
            msg.linear.z
        ])

    def control_loop(self):
        """Execute PI control with feedforward."""
        # Calculate dt
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds * 1e-9
        self.last_time = current_time

        if dt <= 0 or dt > 1.0:
            return

        # Calculate error
        error = self.vel_setpoint - self.current_vel

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup
        self.integral += error * dt
        self.integral = np.clip(self.integral, -self.integral_limit, self.integral_limit)
        i_term = self.ki * self.integral

        # Feedforward term (compensate expected drag at desired velocity)
        ff_term = self.drag * np.abs(self.vel_setpoint) * self.vel_setpoint

        # Total force
        force = p_term + i_term + ff_term

        # Clamp each component
        force = np.clip(force, -self.max_force, self.max_force)

        # Publish wrench
        wrench = Wrench()
        wrench.force.x = force[0]
        wrench.force.y = force[1]
        wrench.force.z = force[2]
        self.wrench_pub.publish(wrench)


def main(args=None):
    rclpy.init(args=args)
    node = VelocityController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
