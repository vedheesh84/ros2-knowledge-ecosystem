#!/usr/bin/env python3
"""
Sensor Fusion Node - Combining Multiple Data Sources
=====================================================

Demonstrates combining data from multiple simulated sensors
and publishing fused data to a single topic.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import random


class SensorFusionNode(Node):
    """Fuses data from multiple simulated sensors."""

    def __init__(self):
        super().__init__('sensor_fusion')
        self.get_logger().info('Sensor Fusion Node starting...')

        # Publisher for fused data
        self.fused_pub = self.create_publisher(String, '/sensor_data', 10)

        # Simulated sensor data
        self.sensor_a = 0.0
        self.sensor_b = 0.0

        # Timer for fusion
        self.timer = self.create_timer(0.5, self.fuse_sensors)

        self.get_logger().info('Publishing fused sensor data to /sensor_data')

    def fuse_sensors(self):
        """Simulate sensor readings and publish fused data."""
        # Simulate sensor readings
        self.sensor_a = 20.0 + random.uniform(-2, 2)  # Temperature-like
        self.sensor_b = 50.0 + random.uniform(-5, 5)  # Humidity-like

        # Simple fusion: average with weights
        fused_value = 0.6 * self.sensor_a + 0.4 * self.sensor_b

        # Publish
        msg = String()
        msg.data = f'Fused: {fused_value:.2f} (A:{self.sensor_a:.1f}, B:{self.sensor_b:.1f})'
        self.fused_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SensorFusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
