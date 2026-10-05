#!/usr/bin/env python3
"""
Demo 02: Thruster Control

LEARNING OBJECTIVES:
====================
1. Understand 6-thruster vectored configuration
2. See how individual thrusters affect motion
3. Learn thruster allocation basics

WHAT THIS DEMO DOES:
====================
1. Activates thrusters one at a time
2. Shows the resulting motion for each
3. Demonstrates combined thruster effects

THRUSTER LAYOUT:
================
T1: Front-left horizontal (45° forward-right)
T2: Front-right horizontal (45° forward-left)
T3: Rear-left horizontal (45° forward-left)
T4: Rear-right horizontal (45° forward-right)
T5: Vertical left (up)
T6: Vertical right (up)

COMBINED EFFECTS:
=================
Surge (forward):  T1+T2+T3+T4 all positive
Sway (right):     T2+T3 positive, T1+T4 negative
Yaw (rotate CW):  T1+T3 positive, T2+T4 negative
Heave (up):       T5+T6 positive
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import time


class Demo02ThrusterControl(Node):
    """Demo 02: Test individual and combined thruster effects."""

    def __init__(self):
        super().__init__('demo_02_thruster_control')

        self.thruster_pub = self.create_publisher(
            Float64MultiArray, '/thrusters/cmd', 10)

        self.get_logger().info('=== Demo 02: Thruster Control ===')
        self.get_logger().info('')
        self.get_logger().info('This demo will activate thrusters in sequence.')
        self.get_logger().info('Watch the robot\'s motion in Gazebo/RViz.')
        self.get_logger().info('')

        # Run demo sequence
        self.run_demo_sequence()

    def send_thrust(self, thrusts: list, description: str, duration: float = 3.0):
        """Send thrust command and hold for duration."""
        self.get_logger().info(f'>>> {description}')
        self.get_logger().info(f'    Thrusts: {thrusts}')

        msg = Float64MultiArray()
        end_time = time.time() + duration

        while time.time() < end_time:
            msg.data = thrusts
            self.thruster_pub.publish(msg)
            time.sleep(0.1)

        # Zero thrust
        msg.data = [0.0] * 6
        self.thruster_pub.publish(msg)
        time.sleep(1.0)  # Pause between tests

    def run_demo_sequence(self):
        """Run through thruster test sequence."""
        self.get_logger().info('Starting thruster test sequence...')
        self.get_logger().info('')

        # Individual thrusters
        self.send_thrust([0.3, 0, 0, 0, 0, 0], 'T1 only (front-left)')
        self.send_thrust([0, 0.3, 0, 0, 0, 0], 'T2 only (front-right)')
        self.send_thrust([0, 0, 0.3, 0, 0, 0], 'T3 only (rear-left)')
        self.send_thrust([0, 0, 0, 0.3, 0, 0], 'T4 only (rear-right)')
        self.send_thrust([0, 0, 0, 0, 0.5, 0], 'T5 only (vertical-left)')
        self.send_thrust([0, 0, 0, 0, 0, 0.5], 'T6 only (vertical-right)')

        # Combined motions
        self.get_logger().info('')
        self.get_logger().info('=== Combined motions ===')

        self.send_thrust([0.3, 0.3, 0.3, 0.3, 0, 0], 'SURGE: All horizontal forward')
        self.send_thrust([0.3, -0.3, -0.3, 0.3, 0, 0], 'SWAY: Move left')
        self.send_thrust([0.3, -0.3, 0.3, -0.3, 0, 0], 'YAW: Rotate')
        self.send_thrust([0, 0, 0, 0, 0.5, 0.5], 'HEAVE: Both vertical up')

        self.get_logger().info('')
        self.get_logger().info('Demo complete!')


def main(args=None):
    rclpy.init(args=args)
    node = Demo02ThrusterControl()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
