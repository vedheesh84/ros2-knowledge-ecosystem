#!/usr/bin/env python3
"""
depth_sensor.py - Pressure-Based Depth Sensor

DEPTH MEASUREMENT PRINCIPLE:
============================
Underwater depth is measured using pressure sensors.

HYDROSTATIC PRESSURE:
---------------------
Pressure increases linearly with depth:

  P = P_atm + rho * g * h

Where:
  P     = Absolute pressure at depth (Pa)
  P_atm = Atmospheric pressure at surface (101325 Pa)
  rho   = Water density (1025 kg/m³ for seawater)
  g     = Gravitational acceleration (9.81 m/s²)
  h     = Depth below surface (m)

Solving for depth:
  h = (P - P_atm) / (rho * g)
  h = (P - 101325) / 10055.25  [meters]

PRESSURE UNITS:
---------------
1 bar = 100000 Pa = ~10m depth
1 atm = 101325 Pa = surface pressure
1 dbar (decibar) = 10000 Pa = ~1m depth

SENSOR CHARACTERISTICS:
-----------------------
- Resolution: Typically 0.01-0.1 mbar (0.1-1 cm depth)
- Accuracy: 0.1-0.5% of full scale
- Temperature compensation required (water density varies)
- Response time: Nearly instantaneous

SIMULATION:
===========
This node simulates a depth sensor by:
1. Reading Z position from ground truth
2. Converting to depth (relative to surface at Z=0)
3. Adding realistic noise

Topics:
  Subscribe: /ground_truth/odom (nav_msgs/Odometry)
  Publish: /depth (std_msgs/Float64) - depth in meters (positive down)
  Publish: /pressure (std_msgs/Float64) - pressure in Pa
"""

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry


class DepthSensor(Node):
    """Simulates a pressure-based depth sensor."""

    def __init__(self):
        super().__init__('depth_sensor')

        # Parameters
        self.declare_parameter('update_rate', 20.0)  # Hz
        self.declare_parameter('noise_stddev', 0.005)  # m (~0.5 cm)
        self.declare_parameter('bias', 0.0)  # m (static offset)
        self.declare_parameter('surface_z', 0.0)  # Z coordinate of surface
        self.declare_parameter('water_density', 1025.0)  # kg/m³

        self.update_rate = self.get_parameter('update_rate').value
        self.noise_stddev = self.get_parameter('noise_stddev').value
        self.bias = self.get_parameter('bias').value
        self.surface_z = self.get_parameter('surface_z').value
        self.water_density = self.get_parameter('water_density').value

        # Physical constants
        self.g = 9.81  # m/s²
        self.p_atm = 101325.0  # Pa (atmospheric pressure)

        # State
        self.current_z = 0.0

        # Publishers
        self.depth_pub = self.create_publisher(Float64, '/depth', 10)
        self.pressure_pub = self.create_publisher(Float64, '/pressure', 10)

        # Subscriber
        self.odom_sub = self.create_subscription(
            Odometry, '/ground_truth/odom', self.odom_callback, 10)

        # Timer
        self.timer = self.create_timer(1.0 / self.update_rate, self.publish_depth)

        self.get_logger().info(
            f'Depth Sensor started: rate={self.update_rate}Hz, '
            f'noise={self.noise_stddev*100:.1f}cm, '
            f'water_density={self.water_density}kg/m³')

    def odom_callback(self, msg: Odometry):
        """Store current Z position."""
        self.current_z = msg.pose.pose.position.z

    def publish_depth(self):
        """Publish depth and pressure with noise."""
        # Calculate true depth (positive down, relative to surface)
        # In ROS convention, Z is up, so depth = surface_z - current_z
        true_depth = self.surface_z - self.current_z

        # Add noise and bias
        measured_depth = true_depth + np.random.normal(0, self.noise_stddev) + self.bias

        # Clamp to non-negative (can't be above surface in this model)
        measured_depth = max(0.0, measured_depth)

        # Publish depth
        depth_msg = Float64()
        depth_msg.data = measured_depth
        self.depth_pub.publish(depth_msg)

        # Calculate and publish pressure
        # P = P_atm + rho * g * h
        pressure = self.p_atm + self.water_density * self.g * measured_depth
        pressure_msg = Float64()
        pressure_msg.data = pressure
        self.pressure_pub.publish(pressure_msg)


def main(args=None):
    rclpy.init(args=args)
    node = DepthSensor()
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
