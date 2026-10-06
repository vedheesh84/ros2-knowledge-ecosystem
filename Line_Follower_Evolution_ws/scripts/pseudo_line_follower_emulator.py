#!/usr/bin/env python3
"""
pseudo_line_follower_emulator.py
Desktop Pseudo-Hardware & Track Emulator for Line Follower Evolution (V1 through V6).

Capabilities:
1. PTY Virtual Serial Port (/tmp/ttyLFE_ROBOT) running physical Arduino NMEA protocol.
2. Synthesizes 2-Channel IR (/v1/ir_raw) and 8-Channel IR Array (/v2_v3/ir_raw_array).
3. Synthesizes 6-DOF IMU (/v2_v3/imu) with dynamic yaw rate damping feedback.
4. Synthesizes AprilTag visual landmark events (/v4_v5/detected_node_tag) at graph nodes.
5. Generates 2D SLAM Occupancy Grids (/map) with unmapped frontier boundaries for V6 exploration.
"""

import os
import pty
import tty
import select
import time
import math
import random
import threading

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Float32MultiArray, String
from sensor_msgs.msg import Imu
from geometry_msgs.msg import Twist
from nav_msgs.msg import OccupancyGrid


class PseudoLineFollowerEmulator(Node):
    def __init__(self, port_path='/tmp/ttyLFE_ROBOT'):
        super().__init__('pseudo_line_follower_emulator')
        
        self.port_path = port_path
        self.master_fd = None
        self.slave_fd = None
        self.running = True
        self.estop_active = False
        
        # Simulated Robot Physical State
        self.sim_time = 0.0
        self.lateral_pos = 0.0      # meters off center
        self.yaw_rate = 0.0         # rad/s
        self.cmd_v = 0.0
        self.cmd_omega = 0.0
        
        # Publishers
        self.pub_v1_ir = self.create_publisher(Float32MultiArray, '/v1/ir_raw', 10)
        self.pub_v2_v3_array = self.create_publisher(Float32MultiArray, '/v2_v3/ir_raw_array', 10)
        self.pub_imu = self.create_publisher(Imu, '/v2_v3/imu', 10)
        self.pub_tag = self.create_publisher(String, '/v4_v5/detected_node_tag', 10)
        self.pub_map = self.create_publisher(OccupancyGrid, '/map', 10)
        
        # Subscriptions
        self.sub_cmd = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        
        # Virtual Serial Port
        self.setup_virtual_serial()
        
        # Timers
        self.timer_sensors = self.create_timer(0.02, self.update_and_publish_sensors) # 50 Hz
        self.timer_map = self.create_timer(1.0, self.publish_sample_frontier_map)      # 1 Hz
        
        self.get_logger().info(f'Pseudo Line Follower Emulator active. Virtual Serial: {self.port_path}')

    def cmd_vel_callback(self, msg: Twist):
        self.cmd_v = msg.linear.x
        self.cmd_omega = msg.angular.z

    def setup_virtual_serial(self):
        try:
            self.master_fd, self.slave_fd = pty.openpty()
            slave_name = os.ttyname(self.slave_fd)
            
            tty.setraw(self.master_fd)
            os.set_blocking(self.master_fd, False)
            
            if os.path.exists(self.port_path) or os.path.islink(self.port_path):
                os.unlink(self.port_path)
            os.symlink(slave_name, self.port_path)
            
            self.serial_thread = threading.Thread(target=self.serial_io_loop, daemon=True)
            self.serial_thread.start()
        except Exception as e:
            self.get_logger().warn(f'Could not setup virtual serial port {self.port_path}: {e}')

    def serial_io_loop(self):
        last_tx = 0
        seq = 0
        while self.running and self.master_fd is not None:
            now = time.time()
            if now - last_tx >= 0.02:  # 50 Hz
                last_tx = now
                seq += 1
                payload = f"LFE,seq={seq},e={self.lateral_pos:.4f},int=0,el={seq*10},er={seq*10},estop={1 if self.estop_active else 0}"
                csum = 0
                for ch in payload:
                    csum ^= ord(ch)
                frame = f"${payload}*{csum:02X}\n"
                try:
                    os.write(self.master_fd, frame.encode('utf-8'))
                except OSError:
                    pass
            
            r, _, _ = select.select([self.master_fd], [], [], 0.02)
            if r:
                try:
                    data = os.read(self.master_fd, 256).decode('utf-8', errors='ignore')
                    if "$CMD,ESTOP" in data:
                        self.estop_active = True
                        os.write(self.master_fd, b"$ACK,ESTOP_ENGAGED\n")
                    elif "$CMD,RESUME" in data:
                        self.estop_active = False
                        os.write(self.master_fd, b"$ACK,NORMAL_OPERATION_RESUMED\n")
                    elif "$CMD,PING" in data:
                        os.write(self.master_fd, b"$PONG,LFE_CONTROLLER_ALIVE\n")
                except OSError:
                    pass
            time.sleep(0.01)

    def update_and_publish_sensors(self):
        dt = 0.02
        self.sim_time += dt
        
        # Synthetic Track Equation: S-curve line position y_track(t) = 0.025 * sin(1.2 * t)
        track_center = 0.025 * math.sin(1.2 * self.sim_time)
        
        # Integrate differential drive response if command received
        if abs(self.cmd_omega) > 0.001:
            self.lateral_pos += self.cmd_omega * 0.01 * dt
        else:
            self.lateral_pos = track_center
            
        error = track_center - self.lateral_pos
        self.yaw_rate = self.cmd_omega + random.gauss(0, 0.01)
        
        # 1. Generation 1: 2-Channel IR Sensors
        dist_left = abs(0.025 - error)
        dist_right = abs(-0.025 - error)
        w1 = 0.015
        l_ir = math.exp(-(dist_left / w1)**2)
        r_ir = math.exp(-(dist_right / w1)**2)
        v1_msg = Float32MultiArray()
        v1_msg.data = [float(max(0.0, min(1.0, l_ir))), float(max(0.0, min(1.0, r_ir)))]
        self.pub_v1_ir.publish(v1_msg)
        
        # 2. Generation 2 & 3: 8-Channel IR Array (70mm wide)
        weights = [-0.035, -0.025, -0.015, -0.005, 0.005, 0.015, 0.025, 0.035]
        v2_readings = []
        for x_s in weights:
            d = abs(x_s - error)
            intensity = math.exp(-(d / 0.012)**2) + random.gauss(0, 0.01)
            v2_readings.append(float(max(0.0, min(1.0, intensity))))
        v2_msg = Float32MultiArray()
        v2_msg.data = v2_readings
        self.pub_v2_v3_array.publish(v2_msg)
        
        # 3. IMU Gyro Telemetry
        imu_msg = Imu()
        imu_msg.header.stamp = self.get_clock().now().to_msg()
        imu_msg.header.frame_id = 'imu_link'
        imu_msg.angular_velocity.z = float(self.yaw_rate)
        self.pub_imu.publish(imu_msg)

    def trigger_visual_tag(self, tag_id: str):
        """Dispatches visual landmark recognition event."""
        tag_msg = String()
        tag_msg.data = str(tag_id)
        self.pub_tag.publish(tag_msg)

    def publish_sample_frontier_map(self):
        """Generates 20x20 OccupancyGrid with known free room and unmapped borders."""
        grid = OccupancyGrid()
        grid.header.stamp = self.get_clock().now().to_msg()
        grid.header.frame_id = 'map'
        grid.info.resolution = 0.1
        grid.info.width = 20
        grid.info.height = 20
        grid.info.origin.position.x = -1.0
        grid.info.origin.position.y = -1.0
        grid.info.origin.orientation.w = 1.0
        
        # Interior free space (0) from [5..15], exterior unknown (-1)
        data = [-1] * 400
        for r in range(5, 15):
            for c in range(5, 15):
                data[r * 20 + c] = 0
        # Wall obstacles
        for c in range(5, 15):
            data[5 * 20 + c] = 100
        grid.data = data
        self.pub_map.publish(grid)

    def destroy_node(self):
        self.running = False
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
        if self.slave_fd is not None:
            try:
                os.close(self.slave_fd)
            except OSError:
                pass
        if os.path.exists(self.port_path) or os.path.islink(self.port_path):
            try:
                os.unlink(self.port_path)
            except OSError:
                pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = PseudoLineFollowerEmulator()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
