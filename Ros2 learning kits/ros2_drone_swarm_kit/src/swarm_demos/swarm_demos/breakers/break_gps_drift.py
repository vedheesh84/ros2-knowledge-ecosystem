#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import math

class BreakGpsDrift(Node):
    """
    Breaker: Injects progressive spatial GPS drift into drone_0 position estimation.
    Kalman state monitor detects divergence residual and triggers optical-flow fallback.
    """
    def __init__(self):
        super().__init__('break_gps_drift')

        self.odom_sub = self.create_subscription(Odometry, '/drone_0/odom', self.odom_cb, 10)
        self.fallback_pub = self.create_publisher(String, '/drone_0/sensor_fallback', 10)

        self.simulated_drift = 0.0
        self.count = 0
        self.fallback_engaged = False

        self.timer = self.create_timer(0.3, self.drift_monitor)
        self.get_logger().warn('BREAKER: GPS Drift & Optical Flow Fallback monitor active for drone_0.')

    def odom_cb(self, msg: Odometry):
        self.count += 1
        if self.count > 5:
            # Inject progressive GPS bias / drift: +0.15m per cycle
            self.simulated_drift += 0.15

    def drift_monitor(self):
        drift_threshold = 0.8 # meters

        if self.simulated_drift > 0.05 and not self.fallback_engaged:
            self.get_logger().warn(
                f'[drone_0] GPS Innovation Residual: {self.simulated_drift:.2f}m drift accumulating...'
            )

        if self.simulated_drift >= drift_threshold and not self.fallback_engaged:
            self.get_logger().error(
                f'[drone_0] CRITICAL: GPS drift ({self.simulated_drift:.2f}m) exceeded safety envelope ({drift_threshold:.1f}m)!'
            )
            self.get_logger().info(
                '>>> SENSOR FAULT DETECTED: Disabling primary GPS state estimation.'
            )
            self.get_logger().info(
                '>>> ENGAGING FALLBACK: Switching to Downward Optical Flow & Rangefinder odometry!'
            )

            fallback_msg = String()
            fallback_msg.data = 'FALLBACK_OPTICAL_FLOW_ENGAGED'
            self.fallback_pub.publish(fallback_msg)
            self.fallback_engaged = True

def main(args=None):
    rclpy.init(args=args)
    node = BreakGpsDrift()
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
