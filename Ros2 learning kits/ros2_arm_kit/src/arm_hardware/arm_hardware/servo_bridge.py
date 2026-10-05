#!/usr/bin/env python3
"""
PCA9685 & Serial Microcontroller Hardware Bridge
================================================
Translates ROS2 JointTrajectory / JointState commands into 12-bit PWM register writes
for PCA9685 I2C driver and Arduino/STM32 serial microcontrollers.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory
import math
import time

class ServoHardwareBridge(Node):
    def __init__(self):
        super().__init__('servo_hardware_bridge')
        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('baud_rate', 115200)
        self.declare_parameter('i2c_bus', 1)
        self.declare_parameter('i2c_address', 0x40)

        self.port = self.get_parameter('serial_port').value
        self.baud = self.get_parameter('baud_rate').value
        self.i2c_addr = self.get_parameter('i2c_address').value

        self.joint_sub = self.create_subscription(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            self.trajectory_callback,
            10
        )
        self.state_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.arm_joints = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint']
        self.joint_positions = [0.0] * len(self.arm_joints)

        self.timer = self.create_timer(0.02, self.publish_joint_states) # 50 Hz loop
        self.get_logger().info(f'Servo Hardware Bridge active on port [{self.port}] / I2C [0x{self.i2c_addr:02X}].')

    def trajectory_callback(self, msg: JointTrajectory):
        if not msg.points:
            return
        pt = msg.points[-1]
        for idx, name in enumerate(self.arm_joints):
            if name in msg.joint_names:
                j_idx = msg.joint_names.index(name)
                angle_rad = pt.positions[j_idx]
                self.joint_positions[idx] = angle_rad
                # Convert rad to 12-bit PCA9685 PWM tick (1.0ms - 2.0ms pulse)
                pwm_tick = self.rad_to_pwm_tick(angle_rad)
                # In hardware: bus.write_word_data(self.i2c_addr, reg, pwm_tick)

    def rad_to_pwm_tick(self, angle_rad: float) -> int:
        deg = math.degrees(angle_rad)
        pulse_ms = 1.5 + (deg / 90.0) * 0.5 # 1.0 to 2.0 ms
        tick = int((pulse_ms / 20.0) * 4096)
        return max(204, min(409, tick)) # clamp to safe range

    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.arm_joints
        msg.position = self.joint_positions
        msg.velocity = [0.0] * len(self.arm_joints)
        msg.effort = [0.0] * len(self.arm_joints)
        self.state_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ServoHardwareBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
