import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import Header, Float32, String
from sensor_msgs.msg import LaserScan
import time
import json


class TopicDelayMonitor(Node):
    """
    TopicDelayMonitor: High-precision network latency and jitter measurement probe.
    
    Measures message propagation latency Delta t = t_{receive} - t_{header.stamp}
    across the wireless DDS bus to detect congested channels and packet dropouts (Article CPS-03 & 08).
    """
    def __init__(self):
        super().__init__('topic_delay_monitor')
        
        self.declare_parameter('monitored_topic', '/robot1/scan')
        self.declare_parameter('sample_window', 50)
        
        self.topic_name = str(self.get_parameter('monitored_topic').value)
        self.sample_window = int(self.get_parameter('sample_window').value)
        
        self.sub_scan = self.create_subscription(
            LaserScan, self.topic_name, self.scan_callback, 10
        )
        
        # Publishers
        self.pub_latency = self.create_publisher(Float32, '/cps/topic_latency', 10)
        self.pub_stats = self.create_publisher(String, '/cps/network_stats', 10)
        
        self.delays = []
        self.latest_delay_ms = 0.0
        self.get_logger().info(f'Topic Delay Monitor initialized on topic [{self.topic_name}].')

    def scan_callback(self, msg: LaserScan):
        now_ns = self.get_clock().now().nanoseconds
        msg_ns = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
        
        if msg_ns > 0:
            delay_ms = (now_ns - msg_ns) / 1_000_000.0
            # Guard against clock skew negative values
            delay_ms = max(0.0, delay_ms)
            self.delays.append(delay_ms)
            self.latest_delay_ms = delay_ms
            
            # Publish instantaneous latency
            lat_msg = Float32()
            lat_msg.data = float(delay_ms)
            self.pub_latency.publish(lat_msg)
            
            if len(self.delays) >= self.sample_window:
                avg_delay = sum(self.delays) / len(self.delays)
                max_delay = max(self.delays)
                min_delay = min(self.delays)
                jitter = max_delay - min_delay
                
                self.get_logger().info(
                    f'DDS Wi-Fi Latency: Avg={avg_delay:.2f}ms | Max={max_delay:.2f}ms | Jitter={jitter:.2f}ms'
                )
                
                # Publish JSON summary
                stats_msg = String()
                stats_msg.data = json.dumps({
                    'topic': self.topic_name,
                    'avg_latency_ms': round(avg_delay, 2),
                    'max_latency_ms': round(max_delay, 2),
                    'min_latency_ms': round(min_delay, 2),
                    'jitter_ms': round(jitter, 2),
                    'samples': len(self.delays)
                })
                self.pub_stats.publish(stats_msg)
                self.delays.clear()


def main(args=None):
    rclpy.init(args=args)
    node = TopicDelayMonitor()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
