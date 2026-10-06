#!/usr/bin/env python3
"""
pseudo_cps_network_emulator.py
Desktop Pseudo-Hardware & Network Emulator for Distributed Multi-Robot CPS.

Capabilities:
1. PTY Virtual Serial Port (/tmp/ttyCPS_EDGE) mimicking physical Arduino Edge Sensor Anchor.
2. ROS 2 Multi-Robot Fleet Telemetry Publisher (Robot 1 Explorer, Robot 2 Manipulator, Edge Anchor).
3. DDS Topic Latency & Network Jitter Emulation.
4. Watchdog Fault Injection: Simulates packet loss / network blackout to verify failover supervisor.
"""

import os
import pty
import tty
import termios
import select
import time
import math
import json
import threading
import argparse

import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import String, Float32
from geometry_msgs.msg import PoseStamped, Point
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import OccupancyGrid

try:
    from cps_msgs.msg import RobotHeartbeat, TaskAssignment, PeerState
    HAVE_CPS_MSGS = True
except ImportError:
    HAVE_CPS_MSGS = False


class PseudoCPSEmulator(Node):
    def __init__(self, port_path='/tmp/ttyCPS_EDGE'):
        super().__init__('pseudo_cps_network_emulator')
        
        self.port_path = port_path
        self.master_fd = None
        self.slave_fd = None
        self.running = True
        
        # ROS Publishers
        self.pub_r1_pose = self.create_publisher(PoseStamped, '/robot1/pose', 10)
        self.pub_r2_pose = self.create_publisher(PoseStamped, '/robot2/pose', 10)
        self.pub_r1_scan = self.create_publisher(LaserScan, '/robot1/scan', 10)
        self.pub_r1_status = self.create_publisher(String, '/robot1/status', 10)
        self.pub_r2_status = self.create_publisher(String, '/robot2/status', 10)
        self.pub_heartbeats_json = self.create_publisher(String, '/cps/heartbeats_json', 10)
        
        if HAVE_CPS_MSGS:
            self.pub_heartbeats = self.create_publisher(RobotHeartbeat, '/cps/heartbeats', 10)
            self.pub_r1_peer = self.create_publisher(PeerState, '/robot1/peer_state', 10)
            self.pub_r2_peer = self.create_publisher(PeerState, '/robot2/peer_state', 10)
        else:
            self.pub_heartbeats = None
            self.pub_r1_peer = None
            self.pub_r2_peer = None
            
        # Target detection event publisher
        self.pub_target_detect = self.create_publisher(PoseStamped, '/robot1/target_detected', 10)
        
        # Map publishers for Robot 1 and Robot 2
        self.pub_r1_map = self.create_publisher(OccupancyGrid, '/robot1/map', 10)
        self.pub_r2_map = self.create_publisher(OccupancyGrid, '/robot2/map', 10)
        
        # Subscriptions
        self.sub_tasks = self.create_subscription(String, '/cps/mission_state', self.mission_state_callback, 10)
        
        # State tracking
        self.sim_time = 0.0
        self.fault_active = False  # Set to True to simulate robot1 communication blackout
        self.estop_active = False
        
        # Setup Virtual Serial Port
        self.setup_virtual_serial()
        
        # Timers
        self.timer_telemetry = self.create_timer(0.5, self.publish_fleet_telemetry) # 2 Hz
        self.timer_scan = self.create_timer(0.1, self.publish_sensor_scan)          # 10 Hz
        
        self.get_logger().info(f'Pseudo CPS Emulator active. Virtual Serial: {self.port_path}')

    def mission_state_callback(self, msg: String):
        pass

    def setup_virtual_serial(self):
        try:
            self.master_fd, self.slave_fd = pty.openpty()
            slave_name = os.ttyname(self.slave_fd)
            
            # Set non-blocking & raw mode
            tty.setraw(self.master_fd)
            os.set_blocking(self.master_fd, False)
            
            if os.path.exists(self.port_path) or os.path.islink(self.port_path):
                os.unlink(self.port_path)
            os.symlink(slave_name, self.port_path)
            
            # Start serial worker thread
            self.serial_thread = threading.Thread(target=self.serial_io_loop, daemon=True)
            self.serial_thread.start()
        except Exception as e:
            self.get_logger().warn(f'Could not setup virtual serial port {self.port_path}: {e}')

    def serial_io_loop(self):
        last_tx = 0
        seq = 0
        while self.running and self.master_fd is not None:
            now = time.time()
            # 2 Hz telemetry transmit
            if now - last_tx >= 0.5:
                last_tx = now
                seq += 1
                v_bat = 12.2 + 0.2 * math.sin(self.sim_time * 0.1)
                pct = max(0.0, min(100.0, (v_bat - 11.1) / 1.5 * 100.0))
                payload = f"CPS,id=edge_anchor_1,seq={seq},v={v_bat:.2f},pct={pct:.1f},temp=26.4,dist=1.85,estop={1 if self.estop_active else 0}"
                
                # Checksum
                csum = 0
                for ch in payload:
                    csum ^= ord(ch)
                frame = f"${payload}*{csum:02X}\n"
                try:
                    os.write(self.master_fd, frame.encode('utf-8'))
                except OSError:
                    pass
            
            # Check Rx commands
            r, _, _ = select.select([self.master_fd], [], [], 0.05)
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
                        os.write(self.master_fd, b"$PONG,EDGE_ALIVE\n")
                except OSError:
                    pass
            time.sleep(0.02)

    def publish_fleet_telemetry(self):
        self.sim_time += 0.5
        stamp = self.get_clock().now().to_msg()
        
        # Robot 1 (Explorer) Motion Simulation
        r1_x = 2.0 * math.cos(self.sim_time * 0.2)
        r1_y = 1.5 * math.sin(self.sim_time * 0.2)
        
        p1 = PoseStamped()
        p1.header.stamp = stamp
        p1.header.frame_id = 'map'
        p1.pose.position.x = r1_x
        p1.pose.position.y = r1_y
        p1.pose.position.z = 0.0
        p1.pose.orientation.w = 1.0
        
        # Robot 2 (Manipulator) Motion Simulation
        r2_x = 4.0 + 1.0 * math.cos(self.sim_time * 0.1)
        r2_y = 0.5 * math.sin(self.sim_time * 0.1)
        
        p2 = PoseStamped()
        p2.header.stamp = stamp
        p2.header.frame_id = 'map'
        p2.pose.position.x = r2_x
        p2.pose.position.y = r2_y
        p2.pose.position.z = 0.0
        p2.pose.orientation.w = 1.0
        
        self.pub_r1_pose.publish(p1)
        self.pub_r2_pose.publish(p2)
        
        # Robot 1 status (unless fault blackout simulated)
        if not self.fault_active:
            r1_stat = String()
            r1_stat.data = json.dumps({'robot_id': 'robot1', 'state': 'EXPLORING', 'battery': 92.5, 'wifi_rssi_dbm': -54})
            self.pub_r1_status.publish(r1_stat)
            
            hb1_json = String()
            hb1_json.data = json.dumps({
                'robot_id': 'robot1',
                'lifecycle_state': 3,
                'battery_percentage': 92.5,
                'battery_voltage_v': 12.3,
                'cpu_utilization_percent': 24.5,
                'wifi_rssi_dbm': -54,
                'topic_latency_ms': 4.2
            })
            self.pub_heartbeats_json.publish(hb1_json)
            
            if HAVE_CPS_MSGS and self.pub_heartbeats is not None:
                hb1 = RobotHeartbeat()
                hb1.header.stamp = stamp
                hb1.robot_id = 'robot1'
                hb1.lifecycle_state = 3
                hb1.battery_voltage_v = 12.3
                hb1.battery_percentage = 92.5
                hb1.cpu_utilization_percent = 24.5
                hb1.wifi_rssi_dbm = -54
                hb1.topic_latency_ms = 4.2
                hb1.operational_mode = 'EXPLORATION'
                self.pub_heartbeats.publish(hb1)
                
        # Robot 2 status
        r2_stat = String()
        r2_stat.data = json.dumps({'robot_id': 'robot2', 'state': 'IDLE', 'battery': 88.0, 'wifi_rssi_dbm': -58})
        self.pub_r2_status.publish(r2_stat)
        
        hb2_json = String()
        hb2_json.data = json.dumps({
            'robot_id': 'robot2',
            'lifecycle_state': 3,
            'battery_percentage': 88.0,
            'battery_voltage_v': 12.1,
            'cpu_utilization_percent': 18.2,
            'wifi_rssi_dbm': -58,
            'topic_latency_ms': 5.8
        })
        self.pub_heartbeats_json.publish(hb2_json)
        
        if HAVE_CPS_MSGS and self.pub_heartbeats is not None:
            hb2 = RobotHeartbeat()
            hb2.header.stamp = stamp
            hb2.robot_id = 'robot2'
            hb2.lifecycle_state = 3
            hb2.battery_voltage_v = 12.1
            hb2.battery_percentage = 88.0
            hb2.cpu_utilization_percent = 18.2
            hb2.wifi_rssi_dbm = -58
            hb2.topic_latency_ms = 5.8
            hb2.operational_mode = 'MANIPULATION'
            self.pub_heartbeats.publish(hb2)

    def publish_sensor_scan(self):
        """Publishes synthetic 360-degree LaserScan with high-precision timestamp."""
        if self.fault_active:
            return
            
        scan = LaserScan()
        scan.header.stamp = self.get_clock().now().to_msg()
        scan.header.frame_id = 'robot1/base_laser'
        scan.angle_min = -math.pi
        scan.angle_max = math.pi
        scan.angle_increment = math.pi / 180.0 # 360 beams
        scan.time_increment = 0.0001
        scan.scan_time = 0.1
        scan.range_min = 0.1
        scan.range_max = 12.0
        # Synthetic obstacle distances
        scan.ranges = [3.5 + 0.5 * math.sin(i * 0.1 + self.sim_time) for i in range(360)]
        self.pub_r1_scan.publish(scan)

    def publish_sample_maps(self):
        """Generates and publishes sample local occupancy grids for Robot 1 and Robot 2."""
        stamp = self.get_clock().now().to_msg()
        
        # Grid 1 (50x50, resolution 0.1m, origin -2.5, -2.5)
        m1 = OccupancyGrid()
        m1.header.stamp = stamp
        m1.header.frame_id = 'map'
        m1.info.resolution = 0.1
        m1.info.width = 50
        m1.info.height = 50
        m1.info.origin.position.x = -2.5
        m1.info.origin.position.y = -2.5
        m1.info.origin.orientation.w = 1.0
        
        # Center free (0), outer unknown (-1), obstacle line (100)
        data1 = [-1] * (50 * 50)
        for r in range(10, 40):
            for c in range(10, 40):
                data1[r * 50 + c] = 0
        for c in range(15, 35):
            data1[30 * 50 + c] = 100
        m1.data = data1
        self.pub_r1_map.publish(m1)
        
        # Grid 2 (50x50, resolution 0.1m, origin -1.0, -2.5)
        m2 = OccupancyGrid()
        m2.header.stamp = stamp
        m2.header.frame_id = 'map'
        m2.info.resolution = 0.1
        m2.info.width = 50
        m2.info.height = 50
        m2.info.origin.position.x = -1.0
        m2.info.origin.position.y = -2.5
        m2.info.origin.orientation.w = 1.0
        
        data2 = [-1] * (50 * 50)
        for r in range(10, 40):
            for c in range(10, 40):
                data2[r * 50 + c] = 0
        for r in range(15, 35):
            data2[r * 50 + 25] = 100
        m2.data = data2
        self.pub_r2_map.publish(m2)

    def trigger_target_detection(self, x: float = 3.2, y: float = 1.8):
        """Simulates Robot 1 detecting a mission landmark or pick target."""
        target = PoseStamped()
        target.header.stamp = self.get_clock().now().to_msg()
        target.header.frame_id = 'map'
        target.pose.position.x = float(x)
        target.pose.position.y = float(y)
        target.pose.position.z = 0.0
        target.pose.orientation.w = 1.0
        self.pub_target_detect.publish(target)
        self.get_logger().info(f'Simulated target detection event dispatched at ({x}, {y}).')

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
    node = PseudoCPSEmulator()
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
