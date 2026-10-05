#!/usr/bin/env python3
"""
state_estimator.py - Floating Base State Estimator for Quadruped

LEARNING OBJECTIVES:
- Understanding floating-base state estimation
- EKF fusion of IMU + leg kinematics
- Why quadrupeds are different from wheeled robots

WHY FLOATING BASE?
Unlike wheeled robots fixed to the ground, quadrupeds "float" in 3D space.
We must estimate 18 states:
- Position (x, y, z): 3
- Orientation (quaternion): 4
- Linear velocity: 3
- Angular velocity: 3
- IMU biases: 6 (gyro + accel)

SENSOR FUSION:
1. IMU provides high-rate orientation and acceleration
2. Leg kinematics provide velocity when feet are in contact
3. Contact provides "pseudo-GPS" for drift correction

This is a simplified EKF for learning. Production systems use
factor graphs (GTSAM) or more sophisticated estimators.
"""

import numpy as np
from typing import Optional, Tuple

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from std_msgs.msg import Bool
from tf2_ros import TransformBroadcaster


class StateEstimator(Node):
    """
    Extended Kalman Filter for quadruped floating-base estimation.

    Fuses:
    - IMU (orientation, angular velocity, linear acceleration)
    - Leg kinematics (foot positions from joint angles)
    - Contact detection (which feet are on ground)

    Publishes:
    - /odom (nav_msgs/Odometry)
    - TF: odom -> base_link
    """

    def __init__(self):
        super().__init__('state_estimator')

        # Parameters
        self.declare_parameter('update_rate', 200.0)  # Hz
        self.declare_parameter('imu_topic', '/imu/data')
        self.declare_parameter('joint_states_topic', '/joint_states')

        self.update_rate = self.get_parameter('update_rate').value

        # ==================== STATE VECTOR ====================
        # [x, y, z, qx, qy, qz, qw, vx, vy, vz, wx, wy, wz, bg1, bg2, bg3, ba1, ba2, ba3]
        # Position (3) + Quaternion (4) + Linear vel (3) + Angular vel (3) + Biases (6) = 19
        self.state = np.zeros(19)
        self.state[6] = 1.0  # qw = 1 (identity quaternion)

        # Initial standing height
        self.state[2] = 0.3  # z = 0.3m (approximate standing height)

        # Covariance matrix (19x19)
        self.P = np.eye(19) * 0.01

        # Process noise
        self.Q = np.eye(19) * 0.001
        self.Q[13:16, 13:16] *= 0.0001  # Lower noise for gyro bias
        self.Q[16:19, 16:19] *= 0.0001  # Lower noise for accel bias

        # Measurement noise
        self.R_imu = np.eye(6) * 0.01  # IMU measurement noise
        self.R_kinematics = np.eye(3) * 0.05  # Leg kinematics noise

        # ==================== LEG KINEMATICS ====================
        # Hip, upper leg, lower leg lengths (from URDF)
        self.hip_offset = 0.08
        self.upper_leg = 0.20
        self.lower_leg = 0.20

        # Leg mounting positions (relative to body center)
        self.leg_origins = {
            'FL': np.array([0.15, -0.08, 0]),
            'FR': np.array([0.15, 0.08, 0]),
            'RL': np.array([-0.15, -0.08, 0]),
            'RR': np.array([-0.15, 0.08, 0]),
        }

        # ==================== CONTACT STATE ====================
        self.contact_state = {'FL': False, 'FR': False, 'RL': False, 'RR': False}

        # ==================== SUBSCRIBERS ====================
        self.imu_sub = self.create_subscription(
            Imu,
            self.get_parameter('imu_topic').value,
            self.imu_callback,
            10
        )

        self.joint_sub = self.create_subscription(
            JointState,
            self.get_parameter('joint_states_topic').value,
            self.joint_callback,
            10
        )

        # Contact subscriptions (one per foot)
        for leg in ['FL', 'FR', 'RL', 'RR']:
            self.create_subscription(
                Bool,
                f'/contact/{leg}',
                lambda msg, l=leg: self.contact_callback(msg, l),
                10
            )

        # ==================== PUBLISHERS ====================
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        # ==================== TIMER ====================
        self.create_timer(1.0 / self.update_rate, self.update_loop)

        # Last sensor data
        self.last_imu: Optional[Imu] = None
        self.last_joints: Optional[JointState] = None
        self.last_time = self.get_clock().now()

        self.get_logger().info('State Estimator initialized')

    def imu_callback(self, msg: Imu):
        """Store latest IMU data for EKF update."""
        self.last_imu = msg

    def joint_callback(self, msg: JointState):
        """Store latest joint states for leg kinematics."""
        self.last_joints = msg

    def contact_callback(self, msg: Bool, leg: str):
        """Update contact state for a leg."""
        self.contact_state[leg] = msg.data

    def leg_forward_kinematics(self, leg: str, q_haa: float, q_hfe: float, q_kfe: float) -> np.ndarray:
        """
        Compute foot position in body frame.

        Args:
            leg: Leg identifier (FL, FR, RL, RR)
            q_haa: Hip abduction/adduction angle
            q_hfe: Hip flexion/extension angle
            q_kfe: Knee flexion/extension angle

        Returns:
            Foot position [x, y, z] in body frame
        """
        # Get leg origin
        origin = self.leg_origins[leg]

        # Determine side multiplier (left legs have negative y offset)
        side = -1 if leg[1] == 'L' else 1

        # Hip abduction rotates about X
        c_haa, s_haa = np.cos(q_haa), np.sin(q_haa)

        # Hip offset in Y
        hip_pos = np.array([0, side * self.hip_offset, 0])

        # Hip flexion rotates about Y
        c_hfe, s_hfe = np.cos(q_hfe), np.sin(q_hfe)

        # Knee flexion rotates about Y
        c_kfe, s_kfe = np.cos(q_kfe), np.sin(q_kfe)

        # Upper leg vector
        upper = np.array([
            -self.upper_leg * s_hfe,
            0,
            -self.upper_leg * c_hfe
        ])

        # Lower leg (relative to knee)
        total_angle = q_hfe + q_kfe
        c_total, s_total = np.cos(total_angle), np.sin(total_angle)
        lower = np.array([
            -self.lower_leg * s_total,
            0,
            -self.lower_leg * c_total
        ])

        # Apply hip abduction rotation to leg
        leg_local = hip_pos + upper + lower
        # Rotate about X by q_haa
        rotated = np.array([
            leg_local[0],
            c_haa * leg_local[1] - s_haa * leg_local[2],
            s_haa * leg_local[1] + c_haa * leg_local[2]
        ])

        return origin + rotated

    def predict(self, dt: float):
        """
        EKF prediction step using IMU data.

        Propagates state forward using:
        - Angular velocity (integrated for orientation)
        - Linear acceleration (integrated for velocity, double for position)
        """
        if self.last_imu is None:
            return

        # Extract IMU data
        gyro = np.array([
            self.last_imu.angular_velocity.x,
            self.last_imu.angular_velocity.y,
            self.last_imu.angular_velocity.z
        ])
        accel = np.array([
            self.last_imu.linear_acceleration.x,
            self.last_imu.linear_acceleration.y,
            self.last_imu.linear_acceleration.z
        ])

        # Remove biases
        gyro_corrected = gyro - self.state[13:16]
        accel_corrected = accel - self.state[16:19]

        # Current orientation as quaternion
        q = self.state[3:7]

        # Rotate acceleration to world frame and remove gravity
        R = self.quaternion_to_rotation(q)
        accel_world = R @ accel_corrected - np.array([0, 0, 9.81])

        # ==================== STATE PROPAGATION ====================
        # Position: x += v * dt + 0.5 * a * dt^2
        self.state[0:3] += self.state[7:10] * dt + 0.5 * accel_world * dt ** 2

        # Velocity: v += a * dt
        self.state[7:10] += accel_world * dt

        # Angular velocity (store for use)
        self.state[10:13] = gyro_corrected

        # Orientation: integrate gyro
        q_dot = 0.5 * self.quaternion_multiply(q, np.array([*gyro_corrected, 0]))
        self.state[3:7] += q_dot * dt
        self.state[3:7] /= np.linalg.norm(self.state[3:7])  # Normalize

        # ==================== COVARIANCE PROPAGATION ====================
        # Simplified: P = P + Q * dt
        self.P += self.Q * dt

    def update_with_kinematics(self):
        """
        EKF update using leg kinematics when foot is in contact.

        When a foot is in contact with ground:
        - Foot velocity should be zero in world frame
        - This provides a constraint for velocity estimation
        """
        if self.last_joints is None:
            return

        # Parse joint states
        joints = {}
        for i, name in enumerate(self.last_joints.name):
            joints[name] = self.last_joints.position[i] if self.last_joints.position else 0.0

        # For each foot in contact
        for leg in ['FL', 'FR', 'RL', 'RR']:
            if not self.contact_state.get(leg, False):
                continue

            # Get joint angles
            try:
                q_haa = joints.get(f'{leg}_HAA', 0.0)
                q_hfe = joints.get(f'{leg}_HFE', 0.0)
                q_kfe = joints.get(f'{leg}_KFE', 0.0)
            except KeyError:
                continue

            # Compute foot position in body frame
            foot_body = self.leg_forward_kinematics(leg, q_haa, q_hfe, q_kfe)

            # Contact constraint: foot is on ground
            # z_world of foot should be 0
            # This simplifies velocity estimation

            # For now, just constrain Z velocity when in contact
            # (Full implementation would use Jacobian-based update)
            contact_factor = 0.95
            self.state[9] *= contact_factor  # Reduce Z velocity

    def quaternion_to_rotation(self, q: np.ndarray) -> np.ndarray:
        """Convert quaternion [x, y, z, w] to 3x3 rotation matrix."""
        x, y, z, w = q
        return np.array([
            [1 - 2*y*y - 2*z*z, 2*x*y - 2*w*z, 2*x*z + 2*w*y],
            [2*x*y + 2*w*z, 1 - 2*x*x - 2*z*z, 2*y*z - 2*w*x],
            [2*x*z - 2*w*y, 2*y*z + 2*w*x, 1 - 2*x*x - 2*y*y]
        ])

    def quaternion_multiply(self, q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
        """Multiply two quaternions [x, y, z, w]."""
        x1, y1, z1, w1 = q1
        x2, y2, z2, w2 = q2
        return np.array([
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2,
            w1*w2 - x1*x2 - y1*y2 - z1*z2
        ])

    def update_loop(self):
        """Main EKF loop: predict, update, publish."""
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds * 1e-9
        self.last_time = current_time

        if dt <= 0 or dt > 0.1:  # Skip bad dt
            return

        # EKF steps
        self.predict(dt)
        self.update_with_kinematics()

        # Publish odometry
        self.publish_odometry(current_time)

    def publish_odometry(self, stamp):
        """Publish estimated state as Odometry and TF."""
        odom = Odometry()
        odom.header.stamp = stamp.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'

        # Position
        odom.pose.pose.position.x = self.state[0]
        odom.pose.pose.position.y = self.state[1]
        odom.pose.pose.position.z = self.state[2]

        # Orientation
        odom.pose.pose.orientation.x = self.state[3]
        odom.pose.pose.orientation.y = self.state[4]
        odom.pose.pose.orientation.z = self.state[5]
        odom.pose.pose.orientation.w = self.state[6]

        # Velocity
        odom.twist.twist.linear.x = self.state[7]
        odom.twist.twist.linear.y = self.state[8]
        odom.twist.twist.linear.z = self.state[9]
        odom.twist.twist.angular.x = self.state[10]
        odom.twist.twist.angular.y = self.state[11]
        odom.twist.twist.angular.z = self.state[12]

        self.odom_pub.publish(odom)

        # TF
        tf = TransformStamped()
        tf.header = odom.header
        tf.child_frame_id = 'base_link'
        tf.transform.translation.x = self.state[0]
        tf.transform.translation.y = self.state[1]
        tf.transform.translation.z = self.state[2]
        tf.transform.rotation = odom.pose.pose.orientation

        self.tf_broadcaster.sendTransform(tf)


def main(args=None):
    rclpy.init(args=args)
    node = StateEstimator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
