#!/usr/bin/env python3
"""
PCA9685 & Serial Microcontroller Hardware Bridge
================================================
Translates ROS2 JointTrajectory / JointState commands into serial ASCII packets
(and PCA9685 I2C writes if available) for physical Arduino/microcontroller servos,
or connects to the pseudo_arm_emulator PTY bridge for testing.

Serial Protocol:
  TX -> Microcontroller: ANGLES,<j1>,<j2>,<j3>,<j4>,<j5>\\n
  RX <- Microcontroller: POS,<j1>,<j2>,<j3>,<j4>,<j5>\\n (50 Hz)
"""
import os
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory
import math
import time
import threading

try:
    import serial
except ImportError:
    serial = None


class ServoHardwareBridge(Node):
    def __init__(self):
        super().__init__('servo_hardware_bridge')
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('baud_rate', 115200)
        self.declare_parameter('i2c_bus', 1)
        self.declare_parameter('i2c_address', 0x40)
        self.declare_parameter('enable_serial', True)

        self.port = self.get_parameter('serial_port').value
        self.baud = self.get_parameter('baud_rate').value
        self.i2c_addr = self.get_parameter('i2c_address').value
        self.enable_serial = self.get_parameter('enable_serial').value

        self.arm_joints = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint']
        self.all_joints = [
            'joint_1', 'joint_2', 'joint_3', 'joint_4',
            'gripper_base_joint', 'left_gear_joint',
            'left_finger_joint', 'right_gear_joint',
            'right_finger_joint', 'left_joint', 'right_joint'
        ]

        self.joint_positions = {j: 0.0 for j in self.all_joints}
        self.target_positions = {j: 0.0 for j in self.all_joints}

        self.ser = None
        self.rx_thread = None
        self.running = True

        if self.enable_serial and serial is not None:
            self._connect_serial()

        self.joint_sub = self.create_subscription(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            self.trajectory_callback,
            10
        )
        self.state_pub = self.create_publisher(JointState, '/joint_states', 10)

        # 50 Hz timer loop
        self.timer = self.create_timer(0.02, self.update_and_publish)
        self.get_logger().info(f'Servo Hardware Bridge active on port [{self.port}] at [{self.baud}] baud.')

    def _connect_serial(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.05)
            self.get_logger().info(f'Successfully opened serial port: {self.port}')
            # Send test/handshake mode
            self.ser.write(b"TEST,ON\n")
            self.rx_thread = threading.Thread(target=self._serial_rx_worker, daemon=True)
            self.rx_thread.start()
        except Exception as e:
            self.get_logger().warn(
                f'Failed to open serial port [{self.port}]: {e}. Running in internal fallback mode.'
            )
            self.ser = None

    def _serial_rx_worker(self):
        buf = ""
        while self.running:
            try:
                if not self.ser or not self.ser.is_open:
                    break
                raw = self.ser.read(64).decode('utf-8', errors='ignore')
                if not raw:
                    continue
                buf += raw
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if line.startswith("POS,"):
                        parts = line[4:].split(",")
                        for i, name in enumerate(self.arm_joints):
                            if i < len(parts):
                                try:
                                    self.joint_positions[name] = float(parts[i])
                                except ValueError:
                                    pass
                    elif line.startswith("STATUS,"):
                        self.get_logger().debug(f'Microcontroller Status: {line}')
            except Exception:
                break

    def trajectory_callback(self, msg: JointTrajectory):
        if not msg.points:
            return
        pt = msg.points[-1]
        for name, pos in zip(msg.joint_names, pt.positions):
            if name in self.target_positions:
                self.target_positions[name] = pos
                if name == 'left_gear_joint':
                    self.target_positions['left_finger_joint'] = pos
                    self.target_positions['right_gear_joint'] = -pos
                    self.target_positions['right_finger_joint'] = pos
                    self.target_positions['left_joint'] = -pos
                    self.target_positions['right_joint'] = pos

        # If serial is connected, send command to hardware
        if self.ser and self.ser.is_open:
            q1 = self.target_positions['joint_1']
            q2 = self.target_positions['joint_2']
            q3 = self.target_positions['joint_3']
            q4 = self.target_positions['joint_4']
            q5 = self.target_positions['gripper_base_joint']
            cmd = f"ANGLES,{q1:.4f},{q2:.4f},{q3:.4f},{q4:.4f},{q5:.4f}\n"
            try:
                self.ser.write(cmd.encode('ascii'))
            except Exception as e:
                self.get_logger().warn(f'Serial write error: {e}')

    def update_and_publish(self):
        # If no serial, smoothly interpolate positions
        if not self.ser or not self.ser.is_open:
            alpha = 0.15
            for name in self.all_joints:
                diff = self.target_positions[name] - self.joint_positions[name]
                self.joint_positions[name] += alpha * diff
        else:
            # Update mimic joints based on target/simulated gripper
            g_pos = self.target_positions.get('left_gear_joint', 0.0)
            self.joint_positions['left_gear_joint'] = g_pos
            self.joint_positions['left_finger_joint'] = g_pos
            self.joint_positions['right_gear_joint'] = -g_pos
            self.joint_positions['right_finger_joint'] = g_pos
            self.joint_positions['left_joint'] = -g_pos
            self.joint_positions['right_joint'] = g_pos

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.all_joints
        msg.position = [self.joint_positions[j] for j in self.all_joints]
        msg.velocity = [0.0] * len(self.all_joints)
        msg.effort = [0.0] * len(self.all_joints)
        self.state_pub.publish(msg)

    def destroy_node(self):
        self.running = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ServoHardwareBridge()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
