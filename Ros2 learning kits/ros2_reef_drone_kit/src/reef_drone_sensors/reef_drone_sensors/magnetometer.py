#!/usr/bin/env python3
"""
magnetometer.py - Magnetic Compass Sensor

MAGNETOMETER PRINCIPLE:
=======================
A magnetometer measures the local magnetic field vector.

EARTH'S MAGNETIC FIELD:
-----------------------
The Earth has a magnetic field with:
  - Horizontal component: ~20-40 μT (points toward magnetic North)
  - Vertical component: ~20-60 μT (varies with latitude)
  - Total field: ~25-65 μT

The field vector in the body frame reveals the vehicle's heading.

HEADING CALCULATION:
--------------------
Given magnetic field in body frame (Bx, By, Bz):

  heading = atan2(-By, Bx)

This gives the angle from magnetic North to the vehicle's X-axis.

Note: This assumes the vehicle is level (no roll/pitch).
For tilted vehicles, need to compensate using roll/pitch from IMU.

TILT COMPENSATION:
------------------
1. Get roll (phi) and pitch (theta) from IMU
2. Transform magnetic field to level frame:
   Bx' = Bx*cos(theta) + Bz*sin(theta)
   By' = Bx*sin(phi)*sin(theta) + By*cos(phi) - Bz*sin(phi)*cos(theta)
3. heading = atan2(-By', Bx')

MAGNETIC DECLINATION:
---------------------
Magnetic North ≠ True North
Declination varies by location (e.g., +13° in California)
Must be added to get true heading.

DISTURBANCES:
-------------
- Hard iron: Permanent magnetization (constant offset)
- Soft iron: Material affecting field shape (scale/rotation)
- Motors, electronics create interference
- Calibration is essential!

SIMULATION:
===========
This node simulates a magnetometer by:
1. Computing magnetic field from vehicle orientation
2. Adding noise and hard/soft iron effects

Topics:
  Subscribe: /ground_truth/odom (nav_msgs/Odometry)
  Publish: /mag/data (geometry_msgs/Vector3Stamped) - field in body frame
  Publish: /heading (std_msgs/Float64) - heading in radians
"""

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3Stamped
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
import transforms3d


class Magnetometer(Node):
    """Simulates a magnetometer/compass sensor."""

    def __init__(self):
        super().__init__('magnetometer')

        # Parameters
        self.declare_parameter('update_rate', 20.0)  # Hz
        self.declare_parameter('noise_stddev', 0.5)  # μT
        self.declare_parameter('declination', 0.0)  # rad (magnetic to true North)

        # Local magnetic field in NED frame (North, East, Down)
        # These values are approximate for mid-latitudes
        self.declare_parameter('field_north', 20.0)  # μT
        self.declare_parameter('field_east', 0.0)  # μT
        self.declare_parameter('field_down', 40.0)  # μT

        self.update_rate = self.get_parameter('update_rate').value
        self.noise_stddev = self.get_parameter('noise_stddev').value
        self.declination = self.get_parameter('declination').value

        # Local magnetic field vector in NED (world frame)
        self.field_ned = np.array([
            self.get_parameter('field_north').value,
            self.get_parameter('field_east').value,
            self.get_parameter('field_down').value
        ])

        # State
        self.orientation_quat = [1.0, 0.0, 0.0, 0.0]  # w, x, y, z

        # Publishers
        self.mag_pub = self.create_publisher(Vector3Stamped, '/mag/data', 10)
        self.heading_pub = self.create_publisher(Float64, '/heading', 10)

        # Subscriber
        self.odom_sub = self.create_subscription(
            Odometry, '/ground_truth/odom', self.odom_callback, 10)

        # Timer
        self.timer = self.create_timer(1.0 / self.update_rate, self.publish_mag)

        self.get_logger().info(
            f'Magnetometer started: rate={self.update_rate}Hz, '
            f'noise={self.noise_stddev}μT, declination={np.degrees(self.declination):.1f}°')

    def odom_callback(self, msg: Odometry):
        """Store current orientation."""
        q = msg.pose.pose.orientation
        # transforms3d uses [w, x, y, z] order
        self.orientation_quat = [q.w, q.x, q.y, q.z]

    def publish_mag(self):
        """Publish magnetic field in body frame and heading."""
        # Get rotation matrix from quaternion (world to body)
        # transforms3d.quaternions.quat2mat expects [w, x, y, z]
        R_world_to_body = transforms3d.quaternions.quat2mat(self.orientation_quat).T

        # Convert NED to ENU (ROS convention) for world frame
        # NED: [North, East, Down] -> ENU: [East, North, -Down]
        field_enu = np.array([
            self.field_ned[1],   # East
            self.field_ned[0],   # North
            -self.field_ned[2]   # Up
        ])

        # Transform to body frame
        field_body = R_world_to_body @ field_enu

        # Add noise
        field_body += np.random.normal(0, self.noise_stddev, 3)

        # Publish magnetic field
        mag_msg = Vector3Stamped()
        mag_msg.header.stamp = self.get_clock().now().to_msg()
        mag_msg.header.frame_id = 'imu_link'
        mag_msg.vector.x = field_body[0]
        mag_msg.vector.y = field_body[1]
        mag_msg.vector.z = field_body[2]
        self.mag_pub.publish(mag_msg)

        # Calculate heading (simplified - assumes level)
        # heading = atan2(-By, Bx) gives angle from body X to magnetic North
        heading_magnetic = np.arctan2(-field_body[1], field_body[0])

        # Add declination to get true heading
        heading_true = heading_magnetic + self.declination

        # Normalize to [0, 2*pi)
        heading_true = heading_true % (2 * np.pi)

        # Publish heading
        heading_msg = Float64()
        heading_msg.data = heading_true
        self.heading_pub.publish(heading_msg)


def main(args=None):
    rclpy.init(args=args)
    node = Magnetometer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
