#!/usr/bin/env python3
"""
flight_bridge_node.py - ROS 2 Hardware Bridge Node for Reef Drone AUV

Bridges ROS 2 topics with the physical microcontroller or desktop pseudo-emulator over serial.

Topics:
  - Subscribes: /thrusters/cmd (std_msgs/Float64MultiArray)
  - Publishes:  /depth (std_msgs/Float64)
  - Publishes:  /pressure (std_msgs/Float64)
  - Publishes:  /hardware/status (std_msgs/String)

Protocol:
  - Commands:   "<T1,T2,T3,T4,T5,T6>\n" (floats in [-1.0, 1.0])
  - Telemetry:  "$TELEM,DEPTH:<m>,PRESS:<Pa>,TEMP:<C>,STATUS:<ARMED/FAILSAFE>\n"
"""

import os
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, Float64, String
import serial
import serial.tools.list_ports


class FlightBridgeNode(Node):
    def __init__(self):
        super().__init__('flight_bridge_node')

        self.declare_parameter('port', '/tmp/ttyAUV_SIM')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('timeout', 0.1)

        self.port_name = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value
        self.timeout = self.get_parameter('timeout').value

        self.serial_conn = None
        self._try_connect()

        # Subscribers
        self.cmd_sub = self.create_subscription(
            Float64MultiArray,
            '/thrusters/cmd',
            self.cmd_callback,
            10
        )

        # Publishers
        self.depth_pub = self.create_publisher(Float64, '/depth', 10)
        self.press_pub = self.create_publisher(Float64, '/pressure', 10)
        self.status_pub = self.create_publisher(String, '/hardware/status', 10)

        # Read serial loop timer (50 Hz)
        self.read_timer = self.create_timer(0.02, self.read_serial_data)

        self.get_logger().info(f'FlightBridgeNode initialized on port {self.port_name} @ {self.baudrate}')

    def _try_connect(self):
        try:
            if os.path.exists(self.port_name):
                self.serial_conn = serial.Serial(
                    self.port_name,
                    self.baudrate,
                    timeout=self.timeout
                )
                self.get_logger().info(f'Successfully connected to serial device {self.port_name}')
            else:
                self.serial_conn = None
        except Exception as e:
            self.serial_conn = None
            self.get_logger().warn(f'Could not connect to {self.port_name}: {e}')

    def cmd_callback(self, msg: Float64MultiArray):
        if not self.serial_conn or not self.serial_conn.is_open:
            self._try_connect()
            if not self.serial_conn:
                return

        # Ensure 6 thruster values
        cmds = list(msg.data)
        while len(cmds) < 6:
            cmds.append(0.0)
        cmds = cmds[:6]

        packet = f"<{cmds[0]:.2f},{cmds[1]:.2f},{cmds[2]:.2f},{cmds[3]:.2f},{cmds[4]:.2f},{cmds[5]:.2f}>\n"
        try:
            self.serial_conn.write(packet.encode('utf-8'))
        except Exception as e:
            self.get_logger().warn(f'Serial write error: {e}')
            self.serial_conn = None

    def read_serial_data(self):
        if not self.serial_conn or not self.serial_conn.is_open:
            self._try_connect()
            return

        try:
            while self.serial_conn.in_waiting > 0:
                line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith('$TELEM'):
                    self._parse_telemetry(line)
        except Exception as e:
            self.get_logger().warn(f'Serial read error: {e}')
            self.serial_conn = None

    def _parse_telemetry(self, line: str):
        # Format: "$TELEM,DEPTH:5.000,PRESS:151600.0,TEMP:22.5,STATUS:ARMED"
        parts = line.split(',')
        for part in parts[1:]:
            if ':' in part:
                k, v = part.split(':', 1)
                k = k.strip().upper()
                v = v.strip()
                if k == 'DEPTH':
                    try:
                        d_msg = Float64()
                        d_msg.data = float(v)
                        self.depth_pub.publish(d_msg)
                    except ValueError:
                        pass
                elif k == 'PRESS':
                    try:
                        p_msg = Float64()
                        p_msg.data = float(v)
                        self.press_pub.publish(p_msg)
                    except ValueError:
                        pass
                elif k == 'STATUS':
                    s_msg = String()
                    s_msg.data = v
                    self.status_pub.publish(s_msg)


def main(args=None):
    rclpy.init(args=args)
    node = FlightBridgeNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException, Exception):
        pass
    finally:
        try:
            node.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
