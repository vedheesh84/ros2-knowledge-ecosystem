#!/usr/bin/env python3
"""
depth_controller.py - PID Depth Controller

DEPTH CONTROL PROBLEM:
======================
Maintain a desired depth (Z position) using vertical thrust.

SYSTEM DYNAMICS:
----------------
The depth DOF is approximately:

  m * z_ddot = F_thrust - F_buoyancy - F_weight + F_drag

For small velocities (negligible drag):
  m * z_ddot = F_thrust + (B - W)

Where:
  B = buoyancy force (up)
  W = weight (down)
  (B - W) is the net buoyancy (positive for positive buoyancy)

PID CONTROL:
============
Classic PID controller:

  F = Kp * e + Ki * ∫e dt + Kd * de/dt

Where:
  e = z_desired - z_measured  (depth error)
  Kp = Proportional gain (responds to current error)
  Ki = Integral gain (eliminates steady-state error)
  Kd = Derivative gain (damps oscillations)

For depth control, the integral term is important because:
- Net buoyancy creates a constant disturbance
- Without integral, there's steady-state error

TUNING GUIDELINES:
==================
1. Start with Kp only (Ki=Kd=0)
2. Increase Kp until oscillation starts
3. Add Kd to damp oscillations
4. Add Ki to eliminate steady-state error

Typical values for small AUV:
  Kp: 50-100 N/m
  Ki: 5-20 N/(m·s)
  Kd: 20-50 N·s/m

ANTI-WINDUP:
============
Integral windup occurs when actuators saturate.
Solution: Clamp integral term and/or use back-calculation.

Topics:
  Subscribe: /depth (std_msgs/Float64)
  Subscribe: /depth/setpoint (std_msgs/Float64)
  Publish: /control/wrench (geometry_msgs/Wrench) - Z force component
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from geometry_msgs.msg import Wrench


class DepthController(Node):
    """PID controller for depth regulation."""

    def __init__(self):
        super().__init__('depth_controller')

        # PID parameters
        self.declare_parameter('kp', 50.0)  # N/m
        self.declare_parameter('ki', 5.0)   # N/(m·s)
        self.declare_parameter('kd', 20.0)  # N·s/m
        self.declare_parameter('max_force', 100.0)  # N
        self.declare_parameter('integral_limit', 20.0)  # m·s

        self.kp = self.get_parameter('kp').value
        self.ki = self.get_parameter('ki').value
        self.kd = self.get_parameter('kd').value
        self.max_force = self.get_parameter('max_force').value
        self.integral_limit = self.get_parameter('integral_limit').value

        # State
        self.depth_setpoint = 5.0  # Default: 5m depth
        self.current_depth = 0.0
        self.last_error = 0.0
        self.integral = 0.0
        self.last_time = self.get_clock().now()

        # Subscribers
        self.depth_sub = self.create_subscription(
            Float64, '/depth', self.depth_callback, 10)
        self.setpoint_sub = self.create_subscription(
            Float64, '/depth/setpoint', self.setpoint_callback, 10)

        # Publisher
        self.wrench_pub = self.create_publisher(Wrench, '/control/wrench', 10)

        # Control loop timer (50 Hz)
        self.timer = self.create_timer(0.02, self.control_loop)

        self.get_logger().info(
            f'Depth Controller started: Kp={self.kp}, Ki={self.ki}, Kd={self.kd}')

    def depth_callback(self, msg: Float64):
        """Update current depth measurement."""
        self.current_depth = msg.data

    def setpoint_callback(self, msg: Float64):
        """Update depth setpoint."""
        self.depth_setpoint = msg.data
        self.get_logger().info(f'New depth setpoint: {self.depth_setpoint:.2f}m')

    def control_loop(self):
        """Execute PID control."""
        # Calculate dt
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds * 1e-9
        self.last_time = current_time

        if dt <= 0 or dt > 1.0:
            return  # Skip on first iteration or clock issues

        # Calculate error
        # Positive error = we're too shallow (need to go down)
        error = self.depth_setpoint - self.current_depth

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup
        self.integral += error * dt
        self.integral = max(-self.integral_limit,
                           min(self.integral_limit, self.integral))
        i_term = self.ki * self.integral

        # Derivative term (on error)
        derivative = (error - self.last_error) / dt
        d_term = self.kd * derivative
        self.last_error = error

        # Total force (negative because positive depth = down, but positive Fz = up)
        force_z = -(p_term + i_term + d_term)

        # Clamp force
        force_z = max(-self.max_force, min(self.max_force, force_z))

        # Publish wrench (only Fz for depth control)
        wrench = Wrench()
        wrench.force.z = force_z
        self.wrench_pub.publish(wrench)


def main(args=None):
    rclpy.init(args=args)
    node = DepthController()
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
