#!/usr/bin/env python3
"""Spin drone propeller joints in RViz via /joint_states."""

from __future__ import annotations

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState


JOINT_NAMES = [
  'front_left_propeller_joint',
  'front_right_propeller_joint',
  'rear_left_propeller_joint',
  'rear_right_propeller_joint',
]

# Opposite diagonal pairs spin opposite directions (quadcopter style).
SPIN_SIGNS = [1.0, -1.0, -1.0, 1.0]


class PropellerSpinner(Node):
  def __init__(self) -> None:
    super().__init__('propeller_spinner')
    self.declare_parameter('update_rate', 40.0)
    self.declare_parameter('idle_spin_rate', 35.0)
    self.declare_parameter('command_spin_boost', 25.0)
    self.declare_parameter('command_topic', '/cmd_vel')
    self.declare_parameter('command_timeout', 0.6)

    self._angles = [0.0, 0.0, 0.0, 0.0]
    self._latest_cmd = Twist()
    self._last_cmd_time = self.get_clock().now()
    rate = max(float(self.get_parameter('update_rate').value), 1.0)
    self._dt = 1.0 / rate

    self._joint_pub = self.create_publisher(JointState, 'joint_states', 10)
    self.create_subscription(
      Twist,
      str(self.get_parameter('command_topic').value),
      self._on_cmd,
      10,
    )
    self.create_timer(self._dt, self._on_timer)
    self.get_logger().info('Propeller spinner publishing /joint_states for RViz')

  def _on_cmd(self, msg: Twist) -> None:
    self._latest_cmd = msg
    self._last_cmd_time = self.get_clock().now()

  def _command_active(self) -> bool:
    age = (self.get_clock().now() - self._last_cmd_time).nanoseconds * 1e-9
    if age > float(self.get_parameter('command_timeout').value):
      return False
    c = self._latest_cmd
    return any(abs(v) > 1e-3 for v in (c.linear.x, c.linear.y, c.linear.z, c.angular.z))

  def _on_timer(self) -> None:
    idle = float(self.get_parameter('idle_spin_rate').value)
    boost = float(self.get_parameter('command_spin_boost').value)
    speed = idle + (boost if self._command_active() else 0.0)

    for i, sign in enumerate(SPIN_SIGNS):
      self._angles[i] = math.fmod(self._angles[i] + sign * speed * self._dt, 2.0 * math.pi)

    js = JointState()
    js.header.stamp = self.get_clock().now().to_msg()
    js.name = list(JOINT_NAMES)
    js.position = list(self._angles)
    js.velocity = [sign * speed for sign in SPIN_SIGNS]
    self._joint_pub.publish(js)


def main() -> None:
  rclpy.init()
  node = PropellerSpinner()
  try:
    rclpy.spin(node)
  finally:
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
  main()
