import rclpy
from rclpy.node import Node
from std_msgs.msg import Header
from sensor_msgs.msg import LaserScan
import time

class TopicDelayMonitor(Node):
    """
    TopicDelayMonitor: High-precision network latency and jitter measurement probe.
    
    Measures message propagation latency Delta t = t_{receive} - t_{header.stamp}
    across the wireless DDS bus to detect congested channels and packet dropouts.
    """
    def __init__(self):
        super().__init__('topic_delay_monitor')
        
        self.sub_scan = self.create_subscription(
            LaserScan, '/robot1/scan', self.scan_callback, 10
        )
        self.delays = []
        self.get_logger().info('Topic Delay Monitor initialized.')

    def scan_callback(self, msg: LaserScan):
        now_ns = self.get_clock().now().nanoseconds
        msg_ns = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
        
        if msg_ns > 0:
            delay_ms = (now_ns - msg_ns) / 1_000_000.0
            self.delays.append(delay_ms)
            if len(self.delays) >= 50:
                avg_delay = sum(self.delays) / len(self.delays)
                max_delay = max(self.delays)
                self.get_logger().info(
                    f'DDS Wi-Fi Latency: Avg={avg_delay:.2f}ms | Max={max_delay:.2f}ms over last 50 packets.'
                )
                self.delays.clear()

def main(args=None):
    rclpy.init(args=args)
    node = TopicDelayMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
