#!/usr/bin/env python3
"""
auv_ekf.py - Extended Kalman Filter for AUV State Estimation

UNDERWATER NAVIGATION CHALLENGE:
================================
Unlike ground/air vehicles, AUVs cannot use GPS underwater.
State estimation must rely on:
  - IMU (orientation, angular velocity)
  - DVL (velocity relative to seafloor)
  - Depth sensor (vertical position)
  - Magnetometer (heading reference)

EKF OVERVIEW:
=============
The Extended Kalman Filter estimates state by:
1. PREDICT: Propagate state using dynamics model
2. UPDATE: Correct using sensor measurements

STATE VECTOR:
=============
We estimate 12 states:

  x = [px, py, pz,        Position (m)
       vx, vy, vz,        Velocity (m/s)
       roll, pitch, yaw,  Orientation (rad)
       wx, wy, wz]        Angular velocity (rad/s)

PREDICTION MODEL:
=================
Position update:
  p(k+1) = p(k) + R * v(k) * dt

Where R is the rotation matrix from body to world frame.

Velocity update (using IMU acceleration):
  v(k+1) = v(k) + (R * a_body - g) * dt

Orientation update (using IMU gyroscope):
  [roll, pitch, yaw](k+1) = [roll, pitch, yaw](k) + G * omega * dt

Where G transforms body rates to Euler rate.

MEASUREMENT MODELS:
==================
DVL: Measures velocity in body frame
  z_dvl = R^T * v + noise

Depth: Measures Z position
  z_depth = -pz + noise  (depth positive down)

Magnetometer: Provides heading
  z_mag = yaw + noise (simplified)

SENSOR FUSION:
==============
IMU:
  - High rate (100+ Hz)
  - Good short-term accuracy
  - Drifts over time (bias)
  - Used in PREDICTION step

DVL:
  - Lower rate (1-10 Hz)
  - Accurate velocity
  - Corrects IMU drift
  - Used in UPDATE step

Depth:
  - High rate, very accurate
  - Directly measures Z
  - Anchors vertical position
  - Used in UPDATE step

Magnetometer:
  - Provides absolute heading
  - Corrects yaw drift
  - Subject to interference
  - Used in UPDATE step

Topics:
  Subscribe:
    /imu/data (sensor_msgs/Imu)
    /dvl/velocity (geometry_msgs/TwistWithCovarianceStamped)
    /depth (std_msgs/Float64)
    /heading (std_msgs/Float64)
  Publish:
    /odom (nav_msgs/Odometry)
    /tf (odom -> base_link)
"""

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import TwistWithCovarianceStamped, TransformStamped
from std_msgs.msg import Float64
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
import transforms3d


class AUVEKF(Node):
    """Extended Kalman Filter for AUV state estimation."""

    def __init__(self):
        super().__init__('auv_ekf')

        # State vector: [px, py, pz, vx, vy, vz, roll, pitch, yaw, wx, wy, wz]
        self.x = np.zeros(12)
        self.x[2] = -5.0  # Start at 5m depth

        # State covariance
        self.P = np.eye(12) * 0.1

        # Process noise covariance
        self.Q = np.diag([
            0.01, 0.01, 0.001,   # Position (m²)
            0.1, 0.1, 0.1,      # Velocity (m²/s²)
            0.001, 0.001, 0.001, # Orientation (rad²)
            0.01, 0.01, 0.01    # Angular velocity (rad²/s²)
        ])

        # Measurement noise covariances
        self.R_dvl = np.eye(3) * 0.01      # DVL velocity (m²/s²)
        self.R_depth = np.array([[0.001]]) # Depth (m²)
        self.R_heading = np.array([[0.01]]) # Heading (rad²)

        # Timing
        self.last_time = self.get_clock().now()
        self.last_imu_time = None

        # Latest sensor data
        self.last_imu = None

        # TF broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)

        # Subscribers
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)
        self.dvl_sub = self.create_subscription(
            TwistWithCovarianceStamped, '/dvl/velocity', self.dvl_callback, 10)
        self.depth_sub = self.create_subscription(
            Float64, '/depth', self.depth_callback, 10)
        self.heading_sub = self.create_subscription(
            Float64, '/heading', self.heading_callback, 10)

        # Publisher
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)

        # Publish timer (50 Hz)
        self.timer = self.create_timer(0.02, self.publish_state)

        self.get_logger().info('AUV EKF started')

    def imu_callback(self, msg: Imu):
        """
        Process IMU data - runs the PREDICTION step.

        IMU provides:
        - Angular velocity (gyroscope): Used for orientation prediction
        - Linear acceleration: Used for velocity prediction
        """
        current_time = self.get_clock().now()

        if self.last_imu_time is not None:
            dt = (current_time - self.last_imu_time).nanoseconds * 1e-9
            if 0 < dt < 0.5:
                # Extract measurements
                omega = np.array([
                    msg.angular_velocity.x,
                    msg.angular_velocity.y,
                    msg.angular_velocity.z
                ])
                accel = np.array([
                    msg.linear_acceleration.x,
                    msg.linear_acceleration.y,
                    msg.linear_acceleration.z
                ])

                # Run prediction step
                self._predict(omega, accel, dt)

        self.last_imu_time = current_time
        self.last_imu = msg

    def dvl_callback(self, msg: TwistWithCovarianceStamped):
        """
        Process DVL data - runs UPDATE step for velocity.

        DVL measures velocity in BODY frame.
        We need to compare with our estimated body velocity.
        """
        # Measurement: velocity in body frame
        z = np.array([
            msg.twist.twist.linear.x,
            msg.twist.twist.linear.y,
            msg.twist.twist.linear.z
        ])

        # Measurement model: z = R^T * v_world
        # H = d(z)/d(x) - Jacobian of measurement wrt state
        R = self._rotation_matrix(self.x[6], self.x[7], self.x[8])

        # Expected measurement
        v_world = self.x[3:6]
        z_expected = R.T @ v_world

        # Innovation (measurement residual)
        y = z - z_expected

        # Measurement Jacobian (simplified: H w.r.t. velocity only)
        H = np.zeros((3, 12))
        H[0:3, 3:6] = R.T  # Velocity part

        # Kalman gain
        S = H @ self.P @ H.T + self.R_dvl
        K = self.P @ H.T @ np.linalg.inv(S)

        # Update state
        self.x = self.x + K @ y

        # Update covariance
        I = np.eye(12)
        self.P = (I - K @ H) @ self.P

    def depth_callback(self, msg: Float64):
        """
        Process depth sensor data - runs UPDATE step for Z position.

        Depth sensor gives direct measurement of depth.
        depth = -pz (since Z is up in ROS)
        """
        z = np.array([msg.data])

        # Expected measurement: depth = -pz
        z_expected = np.array([-self.x[2]])

        # Innovation
        y = z - z_expected

        # Measurement Jacobian
        H = np.zeros((1, 12))
        H[0, 2] = -1.0  # d(depth)/d(pz) = -1

        # Kalman gain
        S = H @ self.P @ H.T + self.R_depth
        K = self.P @ H.T @ np.linalg.inv(S)

        # Update state
        self.x = self.x + K.flatten() * y[0]

        # Update covariance
        I = np.eye(12)
        self.P = (I - K @ H) @ self.P

    def heading_callback(self, msg: Float64):
        """
        Process magnetometer heading - runs UPDATE step for yaw.

        Magnetometer provides absolute heading reference.
        """
        z = np.array([msg.data])

        # Expected measurement: heading = yaw
        z_expected = np.array([self.x[8]])

        # Innovation (with angle wrapping)
        y = self._wrap_angle(z - z_expected)

        # Measurement Jacobian
        H = np.zeros((1, 12))
        H[0, 8] = 1.0  # d(heading)/d(yaw) = 1

        # Kalman gain
        S = H @ self.P @ H.T + self.R_heading
        K = self.P @ H.T @ np.linalg.inv(S)

        # Update state
        self.x = self.x + K.flatten() * y[0]

        # Wrap yaw
        self.x[8] = self._wrap_angle(np.array([self.x[8]]))[0]

        # Update covariance
        I = np.eye(12)
        self.P = (I - K @ H) @ self.P

    def _predict(self, omega: np.ndarray, accel: np.ndarray, dt: float):
        """
        Prediction step using IMU data.

        omega: Angular velocity [wx, wy, wz] in body frame
        accel: Linear acceleration [ax, ay, az] in body frame
        dt: Time step
        """
        # Current state
        p = self.x[0:3]
        v = self.x[3:6]
        rpy = self.x[6:9]

        # Rotation matrix (body to world)
        R = self._rotation_matrix(rpy[0], rpy[1], rpy[2])

        # Gravity in world frame
        g = np.array([0, 0, -9.81])

        # ===== State prediction =====

        # Position: p += R * v * dt
        # (Note: using world velocity directly)
        self.x[0:3] = p + v * dt

        # Velocity: v += (R * a_body + g) * dt
        self.x[3:6] = v + (R @ accel + g) * dt

        # Orientation: rpy += G * omega * dt
        # G transforms body rates to Euler rates
        G = self._euler_rate_matrix(rpy[0], rpy[1])
        self.x[6:9] = rpy + G @ omega * dt

        # Wrap angles
        self.x[6] = self._wrap_angle(np.array([self.x[6]]))[0]
        self.x[7] = self._wrap_angle(np.array([self.x[7]]))[0]
        self.x[8] = self._wrap_angle(np.array([self.x[8]]))[0]

        # Angular velocity
        self.x[9:12] = omega

        # ===== Covariance prediction =====
        # Simplified: P = F * P * F^T + Q
        # Using identity approximation for F
        self.P = self.P + self.Q * dt

    def _rotation_matrix(self, roll: float, pitch: float, yaw: float) -> np.ndarray:
        """Compute rotation matrix from Euler angles (body to world)."""
        cr, sr = np.cos(roll), np.sin(roll)
        cp, sp = np.cos(pitch), np.sin(pitch)
        cy, sy = np.cos(yaw), np.sin(yaw)

        R = np.array([
            [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
            [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
            [-sp,   cp*sr,            cp*cr]
        ])
        return R

    def _euler_rate_matrix(self, roll: float, pitch: float) -> np.ndarray:
        """
        Matrix to convert body angular velocity to Euler angle rates.

        [roll_dot, pitch_dot, yaw_dot]^T = G * [wx, wy, wz]^T
        """
        cr, sr = np.cos(roll), np.sin(roll)
        cp, sp = np.cos(pitch), np.sin(pitch)

        # Avoid singularity at pitch = ±90°
        if abs(cp) < 1e-6:
            cp = 1e-6

        G = np.array([
            [1, sr*sp/cp, cr*sp/cp],
            [0, cr,       -sr],
            [0, sr/cp,    cr/cp]
        ])
        return G

    def _wrap_angle(self, angles: np.ndarray) -> np.ndarray:
        """Wrap angles to [-π, π]."""
        return np.arctan2(np.sin(angles), np.cos(angles))

    def publish_state(self):
        """Publish current state estimate as Odometry and TF."""
        current_time = self.get_clock().now()

        # Create quaternion from Euler angles
        quat = transforms3d.euler.euler2quat(self.x[6], self.x[7], self.x[8])

        # Publish Odometry
        odom = Odometry()
        odom.header.stamp = current_time.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'

        odom.pose.pose.position.x = self.x[0]
        odom.pose.pose.position.y = self.x[1]
        odom.pose.pose.position.z = self.x[2]
        odom.pose.pose.orientation.w = quat[0]
        odom.pose.pose.orientation.x = quat[1]
        odom.pose.pose.orientation.y = quat[2]
        odom.pose.pose.orientation.z = quat[3]

        odom.twist.twist.linear.x = self.x[3]
        odom.twist.twist.linear.y = self.x[4]
        odom.twist.twist.linear.z = self.x[5]
        odom.twist.twist.angular.x = self.x[9]
        odom.twist.twist.angular.y = self.x[10]
        odom.twist.twist.angular.z = self.x[11]

        self.odom_pub.publish(odom)

        # Publish TF
        t = TransformStamped()
        t.header.stamp = current_time.to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.x[0]
        t.transform.translation.y = self.x[1]
        t.transform.translation.z = self.x[2]
        t.transform.rotation.w = quat[0]
        t.transform.rotation.x = quat[1]
        t.transform.rotation.y = quat[2]
        t.transform.rotation.z = quat[3]

        self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = AUVEKF()
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
