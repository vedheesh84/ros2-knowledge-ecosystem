#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32, Bool
import tf2_ros
import serial
import math
import time

class FlightControllerBridge(Node):
    """
    Serial telemetry & control bridge interfacing ROS 2 with physical
    or simulated flight controller firmware over serial/UART.
    """
    def __init__(self):
        super().__init__('flight_controller_bridge')
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)
        self.declare_parameter('drone_id', 'drone_0')
        self.declare_parameter('publish_tf', True)

        self.port_name = self.get_parameter('serial_port').value
        self.baud = int(self.get_parameter('baud_rate').value)
        self.drone_id = self.get_parameter('drone_id').value
        self.pub_tf = bool(self.get_parameter('publish_tf').value)

        prefix = f"/{self.drone_id.lstrip('/')}"
        # Publishers
        self.imu_pub = self.create_publisher(Imu, f'{prefix}/imu', 10)
        self.odom_pub = self.create_publisher(Odometry, f'{prefix}/odom', 10)
        self.battery_pub = self.create_publisher(Float32, f'{prefix}/battery', 10)
        self.armed_pub = self.create_publisher(Bool, f'{prefix}/armed', 10)

        # Subscriptions
        self.cmd_vel_sub = self.create_subscription(Twist, f'{prefix}/cmd_vel', self.cmd_vel_cb, 10)
        self.arm_sub = self.create_subscription(Bool, f'{prefix}/arm_cmd', self.arm_cb, 10)

        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.ser = None
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0
        self.last_time = time.time()

        self.connect_serial()
        self.timer = self.create_timer(0.02, self.serial_loop) # 50 Hz loop
        self.get_logger().info(f'[{self.drone_id}] Hardware Bridge online. Port: {self.port_name} @ {self.baud} baud.')

    def connect_serial(self):
        try:
            self.ser = serial.Serial(self.port_name, self.baud, timeout=0.01)
            self.get_logger().info(f'Connected to flight controller on {self.port_name}')
        except Exception as e:
            self.get_logger().warn(f'Could not open serial port {self.port_name}: {e}. Will retry...')
            self.ser = None

    def cmd_vel_cb(self, msg: Twist):
        if not self.ser or not self.ser.is_open:
            return
        try:
            # Map linear velocities to attitude angles & thrust command
            # Roll ~ vy, Pitch ~ vx, Yaw ~ angular.z, Thrust ~ linear.z + base
            roll = msg.linear.y * 15.0 # deg
            pitch = -msg.linear.x * 15.0 # deg
            yaw_rate = msg.angular.z * 45.0 # deg/s
            thrust = max(0.0, min(100.0, 50.0 + msg.linear.z * 25.0)) # %
            cmd_line = f'CMD,{roll:.2f},{pitch:.2f},{yaw_rate:.2f},{thrust:.2f}\n'
            self.ser.write(cmd_line.encode('ascii'))
        except Exception as e:
            self.get_logger().error(f'Error writing to serial: {e}')

    def arm_cb(self, msg: Bool):
        if not self.ser or not self.ser.is_open:
            return
        try:
            cmd = b'ARM\n' if msg.data else b'DISARM\n'
            self.ser.write(cmd)
            self.get_logger().info(f'Sent {"ARM" if msg.data else "DISARM"} command to flight controller.')
        except Exception as e:
            self.get_logger().error(f'Error sending arm command: {e}')

    def serial_loop(self):
        if not self.ser or not self.ser.is_open:
            if int(time.time()) % 3 == 0: # retry periodically
                self.connect_serial()
            return

        try:
            while self.ser.in_waiting > 0:
                line = self.ser.readline().decode('ascii', errors='ignore').strip()
                if not line:
                    continue
                self.process_telemetry_line(line)
        except Exception as e:
            self.get_logger().warn(f'Serial communication error: {e}')
            self.ser = None

    def process_telemetry_line(self, line: str):
        # Format: TELEM,roll,pitch,yaw,alt,vx,vy,vz,armed,battery
        parts = line.split(',')
        if len(parts) < 10 or parts[0] != 'TELEM':
            return

        try:
            roll = math.radians(float(parts[1]))
            pitch = math.radians(float(parts[2]))
            yaw = math.radians(float(parts[3]))
            alt = float(parts[4])
            vx = float(parts[5])
            vy = float(parts[6])
            vz = float(parts[7])
            is_armed = bool(int(parts[8]))
            battery_v = float(parts[9])
        except ValueError:
            return

        now_ros = self.get_clock().now().to_msg()
        dt = 0.02
        self.pos_z = alt
        self.pos_x += vx * dt
        self.pos_y += vy * dt

        # Euler to Quaternion
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

        child_frame = f'{self.drone_id}/base_link'

        # 1. IMU
        imu = Imu()
        imu.header.stamp = now_ros
        imu.header.frame_id = f'{self.drone_id}/imu_link'
        imu.orientation.w = qw
        imu.orientation.x = qx
        imu.orientation.y = qy
        imu.orientation.z = qz
        imu.linear_acceleration.z = 9.81
        self.imu_pub.publish(imu)

        # 2. Odometry
        odom = Odometry()
        odom.header.stamp = now_ros
        odom.header.frame_id = 'world'
        odom.child_frame_id = child_frame
        odom.pose.pose.position.x = self.pos_x
        odom.pose.pose.position.y = self.pos_y
        odom.pose.pose.position.z = self.pos_z
        odom.pose.pose.orientation = imu.orientation
        odom.twist.twist.linear.x = vx
        odom.twist.twist.linear.y = vy
        odom.twist.twist.linear.z = vz
        self.odom_pub.publish(odom)

        # 3. Battery & Armed
        b_msg = Float32()
        b_msg.data = battery_v
        self.battery_pub.publish(b_msg)

        arm_msg = Bool()
        arm_msg.data = is_armed
        self.armed_pub.publish(arm_msg)

        # 4. TF Broadcast
        if self.pub_tf:
            t = TransformStamped()
            t.header.stamp = now_ros
            t.header.frame_id = 'world'
            t.child_frame_id = child_frame
            t.transform.translation.x = self.pos_x
            t.transform.translation.y = self.pos_y
            t.transform.translation.z = self.pos_z
            t.transform.rotation = imu.orientation
            self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = FlightControllerBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
