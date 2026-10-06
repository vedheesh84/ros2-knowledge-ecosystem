#!/usr/bin/env python3
"""
Demo 01: Buoyancy

LEARNING OBJECTIVES:
====================
1. Understand buoyancy force (Archimedes' principle)
2. Observe neutral buoyancy vs positive/negative buoyancy
3. See passive stability from CB above CM

WHAT THIS DEMO DOES:
====================
1. Spawns the AUV with thrusters OFF
2. Shows the robot slowly rising (positive buoyancy)
3. Demonstrates self-righting behavior

TRY THIS:
=========
- Watch the robot rise due to net positive buoyancy
- Tilt the robot (via Gazebo) and watch it self-right
- Calculate: What buoyancy force balances 11.5 kg weight?

PHYSICS BACKGROUND:
===================
Buoyancy force = rho * g * V
  = 1025 kg/m³ * 9.81 m/s² * 0.0114 m³
  = 114.6 N (upward)

Weight = m * g = 11.5 kg * 9.81 m/s² = 112.8 N (downward)

Net force = 114.6 - 112.8 = 1.8 N upward (positive buoyancy)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class Demo01Buoyancy(Node):
    """Demo 01: Observe buoyancy behavior with thrusters off."""

    def __init__(self):
        super().__init__('demo_01_buoyancy')

        # Publisher for thruster commands (all zeros = off)
        self.thruster_pub = self.create_publisher(
            Float64MultiArray, '/thrusters/cmd', 10)

        # Timer to keep publishing zero commands
        self.timer = self.create_timer(0.1, self.publish_zero_thrust)

        self.get_logger().info('=== Demo 01: Buoyancy ===')
        self.get_logger().info('')
        self.get_logger().info('WATCH: The AUV will slowly rise due to positive buoyancy.')
        self.get_logger().info('')
        self.get_logger().info('OBSERVE:')
        self.get_logger().info('  - Rising motion (buoyancy > weight)')
        self.get_logger().info('  - Self-righting if tilted (CB above CM)')
        self.get_logger().info('')
        self.get_logger().info('TRY: In Gazebo, manually tilt the robot and watch it recover.')
        self.get_logger().info('')
        self.get_logger().info('Press Ctrl+C to exit.')

    def publish_zero_thrust(self):
        """Publish zero thrust to all thrusters."""
        msg = Float64MultiArray()
        msg.data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.thruster_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = Demo01Buoyancy()
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
