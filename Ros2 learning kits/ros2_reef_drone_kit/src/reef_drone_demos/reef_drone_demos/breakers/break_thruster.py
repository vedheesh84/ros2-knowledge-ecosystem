#!/usr/bin/env python3
"""
break_thruster.py - Thruster Failure Injection

LEARNING OBJECTIVES:
====================
1. Understand thruster redundancy
2. See fault-tolerant control in action
3. Learn degraded mode operation

WHAT THIS BREAKER DOES:
=======================
Simulates thruster failures:
  - disable: One thruster produces no thrust
  - reduced: One thruster at reduced power
  - stuck: One thruster stuck at fixed output

FAULT-TOLERANT CONTROL:
=======================
With 6 thrusters, the AUV can tolerate some failures:
  - 1 horizontal thruster: Reduced maneuverability
  - 1 vertical thruster: Reduced heave + roll coupling
  - Multiple failures: Severely degraded

Usage:
  ros2 run reef_drone_demos break_thruster --ros-args -p thruster:=1 -p mode:=disable
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class BreakThruster(Node):
    """Injects thruster failures."""

    def __init__(self):
        super().__init__('break_thruster')

        self.declare_parameter('thruster', 1)  # 1-6
        self.declare_parameter('mode', 'disable')  # disable, reduced, stuck
        self.declare_parameter('stuck_value', 0.3)
        self.declare_parameter('reduction', 0.5)

        self.thruster = self.get_parameter('thruster').value - 1  # 0-indexed
        self.mode = self.get_parameter('mode').value
        self.stuck_value = self.get_parameter('stuck_value').value
        self.reduction = self.get_parameter('reduction').value

        self.sub = self.create_subscription(
            Float64MultiArray, '/thrusters/cmd', self.cmd_callback, 10)
        self.pub = self.create_publisher(
            Float64MultiArray, '/thrusters/cmd_broken', 10)

        self.get_logger().info(
            f'Breaking thruster {self.thruster + 1} with mode: {self.mode}')
        self.get_logger().info(
            'Publishing to /thrusters/cmd_broken')
        self.get_logger().info(
            '(Remap this to /thrusters/cmd for the thruster plugin)')

    def cmd_callback(self, msg: Float64MultiArray):
        broken = Float64MultiArray()
        broken.data = list(msg.data)

        if 0 <= self.thruster < len(broken.data):
            if self.mode == 'disable':
                broken.data[self.thruster] = 0.0
            elif self.mode == 'reduced':
                broken.data[self.thruster] *= self.reduction
            elif self.mode == 'stuck':
                broken.data[self.thruster] = self.stuck_value

        self.pub.publish(broken)


def main(args=None):
    rclpy.init(args=args)
    node = BreakThruster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
