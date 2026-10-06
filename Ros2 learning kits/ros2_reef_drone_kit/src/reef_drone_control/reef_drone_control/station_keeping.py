#!/usr/bin/env python3
"""
station_keeping.py - 3D Position Hold Controller

STATION KEEPING PROBLEM:
========================
Maintain a fixed 3D position (and optionally heading).

This is a cascaded control structure:
  Position error → Velocity command → Force command

CASCADED CONTROL:
-----------------
Outer loop (Position → Velocity):
  v_cmd = Kp_pos * (p_des - p)

Inner loop (Velocity → Force):
  F = Kp_vel * (v_cmd - v) + Ki_vel * ∫(v_cmd - v) dt

This provides:
- Smoother response (velocity limiting)
- Better disturbance rejection
- Easier tuning

COORDINATE FRAMES:
==================
Position error is computed in the world frame.
Force commands are in the body frame.
Must rotate the force command by vehicle orientation.

For horizontal motion (X-Y):
  F_body = R_yaw * F_world

Where R_yaw is the rotation matrix for current heading.

Topics:
  Subscribe: /odom (nav_msgs/Odometry) - current pose and velocity
  Subscribe: /station/setpoint (geometry_msgs/PoseStamped) - desired pose
  Publish: /control/wrench (geometry_msgs/Wrench)
"""

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Wrench
from nav_msgs.msg import Odometry
import transforms3d


class StationKeeping(Node):
    """Cascaded position-velocity controller for station keeping."""

    def __init__(self):
        super().__init__('station_keeping')

        # Position loop gains
        self.declare_parameter('kp_pos', 2.0)  # 1/s (velocity per meter error)
        self.declare_parameter('max_velocity', 0.5)  # m/s

        # Velocity loop gains
        self.declare_parameter('kp_vel', 30.0)  # N/(m/s)
        self.declare_parameter('ki_vel', 3.0)   # N/m

        # Heading loop gains
        self.declare_parameter('kp_heading', 10.0)  # N·m/rad
        self.declare_parameter('kd_heading', 5.0)   # N·m·s/rad

        # Limits
        self.declare_parameter('max_force', 100.0)  # N
        self.declare_parameter('max_torque', 20.0)  # N·m

        # Get parameters
        self.kp_pos = self.get_parameter('kp_pos').value
        self.max_velocity = self.get_parameter('max_velocity').value
        self.kp_vel = self.get_parameter('kp_vel').value
        self.ki_vel = self.get_parameter('ki_vel').value
        self.kp_heading = self.get_parameter('kp_heading').value
        self.kd_heading = self.get_parameter('kd_heading').value
        self.max_force = self.get_parameter('max_force').value
        self.max_torque = self.get_parameter('max_torque').value

        # State
        self.position_setpoint = np.array([0.0, 0.0, -5.0])  # Default 5m depth
        self.heading_setpoint = 0.0
        self.current_position = np.zeros(3)
        self.current_velocity = np.zeros(3)
        self.current_heading = 0.0
        self.yaw_rate = 0.0
        self.vel_integral = np.zeros(3)
        self.last_time = self.get_clock().now()

        # Subscribers
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.setpoint_sub = self.create_subscription(
            PoseStamped, '/station/setpoint', self.setpoint_callback, 10)

        # Publisher
        self.wrench_pub = self.create_publisher(Wrench, '/control/wrench', 10)

        # Control loop timer (50 Hz)
        self.timer = self.create_timer(0.02, self.control_loop)

        self.get_logger().info('Station Keeping Controller started')

    def odom_callback(self, msg: Odometry):
        """Update current state from odometry."""
        self.current_position = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z
        ])
        self.current_velocity = np.array([
            msg.twist.twist.linear.x,
            msg.twist.twist.linear.y,
            msg.twist.twist.linear.z
        ])
        self.yaw_rate = msg.twist.twist.angular.z

        # Extract yaw from quaternion
        q = msg.pose.pose.orientation
        _, _, yaw = transforms3d.euler.quat2euler([q.w, q.x, q.y, q.z])
        self.current_heading = yaw

    def setpoint_callback(self, msg: PoseStamped):
        """Update position setpoint."""
        self.position_setpoint = np.array([
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z
        ])

        # Extract yaw from setpoint quaternion
        q = msg.pose.orientation
        _, _, yaw = transforms3d.euler.quat2euler([q.w, q.x, q.y, q.z])
        self.heading_setpoint = yaw

        self.get_logger().info(
            f'New setpoint: pos=[{self.position_setpoint[0]:.1f}, '
            f'{self.position_setpoint[1]:.1f}, {self.position_setpoint[2]:.1f}], '
            f'heading={np.degrees(self.heading_setpoint):.1f}°')

    def control_loop(self):
        """Execute cascaded position-velocity control."""
        # Calculate dt
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds * 1e-9
        self.last_time = current_time

        if dt <= 0 or dt > 1.0:
            return

        # ===== Position loop (outer) =====
        pos_error = self.position_setpoint - self.current_position
        vel_cmd = self.kp_pos * pos_error

        # Limit velocity command
        vel_mag = np.linalg.norm(vel_cmd)
        if vel_mag > self.max_velocity:
            vel_cmd = vel_cmd * (self.max_velocity / vel_mag)

        # ===== Velocity loop (inner) =====
        vel_error = vel_cmd - self.current_velocity

        # PI control on velocity
        p_term = self.kp_vel * vel_error
        self.vel_integral += vel_error * dt
        self.vel_integral = np.clip(self.vel_integral, -10.0, 10.0)
        i_term = self.ki_vel * self.vel_integral

        force_world = p_term + i_term

        # Transform force from world frame to body frame
        force_body = self._world_to_body(force_world, self.current_heading)

        # Clamp forces
        force_body = np.clip(force_body, -self.max_force, self.max_force)

        # ===== Heading loop =====
        heading_error = self._wrap_angle(self.heading_setpoint - self.current_heading)
        torque_z = self.kp_heading * heading_error - self.kd_heading * self.yaw_rate
        torque_z = max(-self.max_torque, min(self.max_torque, torque_z))

        # Publish wrench
        wrench = Wrench()
        wrench.force.x = force_body[0]
        wrench.force.y = force_body[1]
        wrench.force.z = force_body[2]
        wrench.torque.z = torque_z
        self.wrench_pub.publish(wrench)

    def _world_to_body(self, vec_world: np.ndarray, heading: float) -> np.ndarray:
        """Transform vector from world frame to body frame (2D rotation)."""
        c = np.cos(heading)
        s = np.sin(heading)
        return np.array([
            c * vec_world[0] + s * vec_world[1],
            -s * vec_world[0] + c * vec_world[1],
            vec_world[2]  # Z unchanged
        ])

    def _wrap_angle(self, angle: float) -> float:
        """Wrap angle to [-π, π]."""
        return np.arctan2(np.sin(angle), np.cos(angle))


def main(args=None):
    rclpy.init(args=args)
    node = StationKeeping()
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
