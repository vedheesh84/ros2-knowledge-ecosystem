#!/usr/bin/env python3
"""
heading_controller.py - PID Heading (Yaw) Controller

HEADING CONTROL PROBLEM:
========================
Maintain a desired heading (yaw angle) using yaw torque.

SYSTEM DYNAMICS:
----------------
Yaw dynamics:

  I_zz * yaw_ddot = T_yaw - D_yaw * yaw_dot

Where:
  I_zz = Moment of inertia about Z axis
  T_yaw = Applied yaw torque
  D_yaw = Yaw damping coefficient

ANGLE WRAPPING:
===============
Heading angles wrap around at ±π (or 0 and 2π).
Error calculation must handle this:

  error = atan2(sin(desired - current), cos(desired - current))

This gives the shortest angular distance, always in [-π, π].

PD CONTROL (No Integral):
=========================
For heading, we typically use PD control:

  T = Kp * e + Kd * de/dt

Integral is often omitted because:
- No constant disturbance (unlike depth with buoyancy)
- Can cause windup when turning through ±π boundary

However, integral can be added for current rejection.

Topics:
  Subscribe: /heading (std_msgs/Float64) - current heading [rad]
  Subscribe: /heading/setpoint (std_msgs/Float64) - desired heading [rad]
  Subscribe: /imu/data (sensor_msgs/Imu) - for yaw rate
  Publish: /control/wrench (geometry_msgs/Wrench) - Z torque component
"""

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Wrench


class HeadingController(Node):
    """PD controller for heading (yaw) regulation."""

    def __init__(self):
        super().__init__('heading_controller')

        # PID parameters
        self.declare_parameter('kp', 10.0)  # N·m/rad
        self.declare_parameter('kd', 5.0)   # N·m·s/rad
        self.declare_parameter('max_torque', 20.0)  # N·m

        self.kp = self.get_parameter('kp').value
        self.kd = self.get_parameter('kd').value
        self.max_torque = self.get_parameter('max_torque').value

        # State
        self.heading_setpoint = 0.0  # rad
        self.current_heading = 0.0  # rad
        self.yaw_rate = 0.0  # rad/s

        # Subscribers
        self.heading_sub = self.create_subscription(
            Float64, '/heading', self.heading_callback, 10)
        self.setpoint_sub = self.create_subscription(
            Float64, '/heading/setpoint', self.setpoint_callback, 10)
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)

        # Publisher
        self.wrench_pub = self.create_publisher(Wrench, '/control/wrench', 10)

        # Control loop timer (50 Hz)
        self.timer = self.create_timer(0.02, self.control_loop)

        self.get_logger().info(
            f'Heading Controller started: Kp={self.kp}, Kd={self.kd}')

    def heading_callback(self, msg: Float64):
        """Update current heading."""
        self.current_heading = msg.data

    def setpoint_callback(self, msg: Float64):
        """Update heading setpoint."""
        self.heading_setpoint = msg.data
        self.get_logger().info(
            f'New heading setpoint: {np.degrees(self.heading_setpoint):.1f}°')

    def imu_callback(self, msg: Imu):
        """Get yaw rate from IMU."""
        self.yaw_rate = msg.angular_velocity.z

    def _wrap_angle(self, angle: float) -> float:
        """Wrap angle to [-π, π]."""
        return np.arctan2(np.sin(angle), np.cos(angle))

    def control_loop(self):
        """Execute PD control."""
        # Calculate angular error with wrapping
        error = self._wrap_angle(self.heading_setpoint - self.current_heading)

        # Proportional term
        p_term = self.kp * error

        # Derivative term (using yaw rate from IMU)
        # Negative because we want to oppose the rotation if it increases error
        d_term = -self.kd * self.yaw_rate

        # Total torque
        torque_z = p_term + d_term

        # Clamp torque
        torque_z = max(-self.max_torque, min(self.max_torque, torque_z))

        # Publish wrench (only Tz for heading control)
        wrench = Wrench()
        wrench.torque.z = torque_z
        self.wrench_pub.publish(wrench)


def main(args=None):
    rclpy.init(args=args)
    node = HeadingController()
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
