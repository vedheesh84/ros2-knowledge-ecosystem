#!/usr/bin/env python3
"""
dvl_simulator.py - Doppler Velocity Log Simulator

DVL WORKING PRINCIPLE:
======================
The Doppler Velocity Log measures velocity using the Doppler effect.

1. BEAM GEOMETRY (Janus Configuration):
   Four acoustic beams aimed at the seafloor, typically at 20-30° from vertical.

       Beam 1     Beam 2
           \\     //
            \\   //
             \\ //
              AUV
             // \\
            //   \\
       Beam 3     Beam 4
              |
              v
           Seafloor

2. DOPPLER SHIFT:
   When the AUV moves, the frequency of reflected sound shifts:

   f_received = f_transmitted * (c + v_receiver) / (c - v_source)

   For small velocities relative to sound speed:
   delta_f / f = 2 * v / c

   Where:
   - c = speed of sound in water (~1500 m/s)
   - v = velocity component along beam

3. VELOCITY COMPUTATION:
   Each beam measures velocity along its axis.
   With 4 beams, we can compute 3D velocity + check consistency.

   v_along_beam = (c * delta_f) / (2 * f)

   Transform beam velocities to body frame using known geometry.

4. BOTTOM LOCK:
   DVL needs a reflective surface (seafloor) within range.
   - Typical range: 0.5m to 200m from bottom
   - If too high, no bottom lock (velocity unavailable)
   - Can also use "water track" mode (less accurate)

5. ALTITUDE:
   DVL also provides altitude (distance to seafloor):
   altitude = c * t_round_trip / 2

SIMULATION:
===========
This node simulates DVL by:
1. Subscribing to Gazebo model state (ground truth)
2. Adding realistic noise characteristics
3. Publishing velocity and altitude

Topics:
  Subscribe: /gazebo/model_states (nav_msgs/ModelState)
  Publish: /dvl/velocity (geometry_msgs/TwistWithCovarianceStamped)
  Publish: /dvl/altitude (std_msgs/Float64)
"""

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistWithCovarianceStamped, Vector3
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry


class DVLSimulator(Node):
    """Simulates a Doppler Velocity Log sensor."""

    def __init__(self):
        super().__init__('dvl_simulator')

        # Parameters
        self.declare_parameter('update_rate', 10.0)  # Hz
        self.declare_parameter('noise_stddev', 0.01)  # m/s
        self.declare_parameter('seafloor_depth', -20.0)  # m (Z coordinate)
        self.declare_parameter('max_range', 100.0)  # m
        self.declare_parameter('min_range', 0.5)  # m

        self.update_rate = self.get_parameter('update_rate').value
        self.noise_stddev = self.get_parameter('noise_stddev').value
        self.seafloor_depth = self.get_parameter('seafloor_depth').value
        self.max_range = self.get_parameter('max_range').value
        self.min_range = self.get_parameter('min_range').value

        # State
        self.current_velocity = Vector3()
        self.current_position_z = 0.0

        # Publishers
        self.vel_pub = self.create_publisher(
            TwistWithCovarianceStamped, '/dvl/velocity', 10)
        self.alt_pub = self.create_publisher(
            Float64, '/dvl/altitude', 10)

        # Subscriber (from ground truth or EKF)
        self.odom_sub = self.create_subscription(
            Odometry, '/ground_truth/odom', self.odom_callback, 10)

        # Timer for publishing
        self.timer = self.create_timer(1.0 / self.update_rate, self.publish_dvl)

        self.get_logger().info(
            f'DVL Simulator started: rate={self.update_rate}Hz, '
            f'noise={self.noise_stddev}m/s, seafloor={self.seafloor_depth}m')

    def odom_callback(self, msg: Odometry):
        """Store current velocity and position from ground truth."""
        self.current_velocity = msg.twist.twist.linear
        self.current_position_z = msg.pose.pose.position.z

    def publish_dvl(self):
        """Publish DVL velocity and altitude with noise."""
        # Calculate altitude (distance to seafloor)
        altitude = self.current_position_z - self.seafloor_depth

        # Check if bottom lock is possible
        if altitude < self.min_range or altitude > self.max_range:
            # No bottom lock - don't publish velocity
            self.get_logger().debug(f'No bottom lock: altitude={altitude:.1f}m')
            return

        # Publish altitude
        alt_msg = Float64()
        alt_msg.data = altitude + np.random.normal(0, 0.02)  # 2cm noise
        self.alt_pub.publish(alt_msg)

        # Publish velocity with noise
        vel_msg = TwistWithCovarianceStamped()
        vel_msg.header.stamp = self.get_clock().now().to_msg()
        vel_msg.header.frame_id = 'dvl_link'

        # Add Gaussian noise to velocity
        vel_msg.twist.twist.linear.x = (
            self.current_velocity.x + np.random.normal(0, self.noise_stddev))
        vel_msg.twist.twist.linear.y = (
            self.current_velocity.y + np.random.normal(0, self.noise_stddev))
        vel_msg.twist.twist.linear.z = (
            self.current_velocity.z + np.random.normal(0, self.noise_stddev))

        # Covariance matrix (diagonal)
        variance = self.noise_stddev ** 2
        # 6x6 covariance: [vx, vy, vz, wx, wy, wz]
        vel_msg.twist.covariance = [
            variance, 0, 0, 0, 0, 0,
            0, variance, 0, 0, 0, 0,
            0, 0, variance, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0,
        ]

        self.vel_pub.publish(vel_msg)


def main(args=None):
    rclpy.init(args=args)
    node = DVLSimulator()
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
