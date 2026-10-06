#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, JointState
import tf2_ros
import math

class DroneFlightController(Node):
    """
    Flight dynamics simulator and position/attitude tracker for an aerial agent.
    Simulates 1st-order closed-loop flight dynamics, broadcasts TF, Odometry, IMU,
    and spins rotor visual joints.
    """
    def __init__(self):
        super().__init__('flight_controller')
        self.declare_parameter('drone_id', 'drone_0')
        self.declare_parameter('initial_x', 0.0)
        self.declare_parameter('initial_y', 0.0)
        self.declare_parameter('initial_z', 0.0)

        self.drone_id = self.get_parameter('drone_id').value
        self.pos_x = float(self.get_parameter('initial_x').value)
        self.pos_y = float(self.get_parameter('initial_y').value)
        self.pos_z = float(self.get_parameter('initial_z').value)

        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0

        self.target_x = self.pos_x
        self.target_y = self.pos_y
        self.target_z = self.pos_z

        self.rotor_angle = 0.0
        self.rotor_names = [
            'rotor_front_right_joint',
            'rotor_front_left_joint',
            'rotor_back_left_joint',
            'rotor_back_right_joint'
        ]

        # Publishers
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.imu_pub = self.create_publisher(Imu, 'imu', 10)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)

        # Subscriptions
        self.target_sub = self.create_subscription(PoseStamped, 'target_pose', self.target_cb, 10)
        self.cmd_vel_sub = self.create_subscription(Twist, 'cmd_vel', self.cmd_vel_cb, 10)

        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.timer = self.create_timer(0.02, self.update_physics) # 50 Hz loop
        self.get_logger().info(f'[{self.drone_id}] Flight Controller online at initial pose ({self.pos_x:.2f}, {self.pos_y:.2f}, {self.pos_z:.2f}).')

    def target_cb(self, msg: PoseStamped):
        self.target_x = msg.pose.position.x
        self.target_y = msg.pose.position.y
        self.target_z = max(0.0, msg.pose.position.z)

    def cmd_vel_cb(self, msg: Twist):
        self.target_x += msg.linear.x * 0.05
        self.target_y += msg.linear.y * 0.05
        self.target_z = max(0.0, self.target_z + msg.linear.z * 0.05)

    def update_physics(self):
        max_vel = 1.5 # m/s
        dt = 0.02
        gain = 2.0

        # Position tracking errors
        err_x = self.target_x - self.pos_x
        err_y = self.target_y - self.pos_y
        err_z = self.target_z - self.pos_z

        prev_vx, prev_vy, prev_vz = self.vx, self.vy, self.vz

        self.vx = max(-max_vel, min(max_vel, gain * err_x))
        self.vy = max(-max_vel, min(max_vel, gain * err_y))
        self.vz = max(-max_vel, min(max_vel, gain * err_z))

        self.pos_x += self.vx * dt
        self.pos_y += self.vy * dt
        self.pos_z = max(0.0, self.pos_z + self.vz * dt)

        # Linear accelerations (approx)
        ax = (self.vx - prev_vx) / dt
        ay = (self.vy - prev_vy) / dt
        az = (self.vz - prev_vz) / dt

        # Quadrotor tilt angles from acceleration (SE(3) differential flatness approximation)
        g = 9.81
        pitch = math.atan2(-ax, g) # nose down when accelerating forward (+x)
        roll = math.atan2(ay, g)   # bank right when accelerating right (+y)
        yaw = 0.0

        # Convert Euler to Quaternion
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy

        now = self.get_clock().now().to_msg()
        child_frame = f'{self.drone_id}/base_link'

        # 1. Odometry
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = 'world'
        odom.child_frame_id = child_frame
        odom.pose.pose.position.x = self.pos_x
        odom.pose.pose.position.y = self.pos_y
        odom.pose.pose.position.z = self.pos_z
        odom.pose.pose.orientation.w = qw
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.twist.twist.linear.x = self.vx
        odom.twist.twist.linear.y = self.vy
        odom.twist.twist.linear.z = self.vz
        self.odom_pub.publish(odom)

        # 2. IMU
        imu = Imu()
        imu.header.stamp = now
        imu.header.frame_id = f'{self.drone_id}/imu_link'
        imu.orientation.w = qw
        imu.orientation.x = qx
        imu.orientation.y = qy
        imu.orientation.z = qz
        imu.linear_acceleration.x = ax
        imu.linear_acceleration.y = ay
        imu.linear_acceleration.z = az + g
        self.imu_pub.publish(imu)

        # 3. TF Broadcast
        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = 'world'
        t.child_frame_id = child_frame
        t.transform.translation.x = self.pos_x
        t.transform.translation.y = self.pos_y
        t.transform.translation.z = self.pos_z
        t.transform.rotation.w = qw
        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        self.tf_broadcaster.sendTransform(t)

        # 4. Rotor Joint States
        if self.pos_z > 0.05:
            self.rotor_angle = (self.rotor_angle + 60.0 * dt) % (2.0 * math.pi)
        js = JointState()
        js.header.stamp = now
        js.name = self.rotor_names
        js.position = [
            self.rotor_angle,
            -self.rotor_angle,
            self.rotor_angle,
            -self.rotor_angle
        ]
        js.velocity = [60.0, -60.0, 60.0, -60.0] if self.pos_z > 0.05 else [0.0, 0.0, 0.0, 0.0]
        self.joint_pub.publish(js)

def main(args=None):
    rclpy.init(args=args)
    node = DroneFlightController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
