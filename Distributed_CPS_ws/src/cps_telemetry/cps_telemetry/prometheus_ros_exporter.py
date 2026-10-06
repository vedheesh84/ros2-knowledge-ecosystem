import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import String
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    from cps_msgs.msg import RobotHeartbeat
    HAVE_CPS_MSGS = True
except ImportError:
    HAVE_CPS_MSGS = False


class MetricsHTTPRequestHandler(BaseHTTPRequestHandler):
    """Serves Prometheus exposition text format on GET /metrics."""
    
    def log_message(self, format, *args):
        # Suppress noisy HTTP request logging
        return

    def do_GET(self):
        if self.path in ('/metrics', '/'):
            exporter = self.server.exporter_node
            metrics_text = exporter.generate_prometheus_text()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; version=0.0.4; charset=utf-8')
            self.end_headers()
            self.wfile.write(metrics_text.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')


class PrometheusROSExporter(Node):
    """
    PrometheusROSExporter: Bridge connecting ROS 2 fleet telemetry to Prometheus/Grafana.
    
    Aggregates battery state, CPU load, and network link quality from distributed edge robots
    and exposes them over a standard HTTP /metrics endpoint for Prometheus scraping (Article CPS-08).
    """
    def __init__(self):
        super().__init__('prometheus_ros_exporter')
        
        self.declare_parameter('metrics_port', 9100)
        self.metrics_port = int(self.get_parameter('metrics_port').value)
        
        # In-memory metrics storage
        self.metrics_cache = {}  # {robot_id: {battery, cpu, rssi, last_seen, lifecycle}}
        self.lock = threading.Lock()
        
        # Subscriptions
        self.sub_heartbeats_json = self.create_subscription(
            String, '/cps/heartbeats_json', self.heartbeat_json_callback, 10
        )
        if HAVE_CPS_MSGS:
            self.sub_heartbeats_typed = self.create_subscription(
                RobotHeartbeat, '/cps/heartbeats', self.heartbeat_typed_callback, 10
            )
        else:
            self.sub_heartbeats_typed = None
            
        # Optional ROS 2 metrics topic publisher
        self.pub_fleet_metrics = self.create_publisher(String, '/cps/fleet_metrics', 10)
        
        # Periodic ROS topic publication
        self.timer = self.create_timer(2.0, self.publish_metrics_summary)
        
        # Launch embedded HTTP Server in background daemon thread
        self.http_server = None
        self.server_thread = None
        self.start_http_server()
        
        self.get_logger().info(
            f'Prometheus ROS Telemetry Exporter initialized on HTTP port {self.metrics_port} (endpoint /metrics).'
        )

    def start_http_server(self):
        try:
            self.http_server = HTTPServer(('0.0.0.0', self.metrics_port), MetricsHTTPRequestHandler)
            self.http_server.exporter_node = self
            self.server_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
            self.server_thread.start()
        except Exception as e:
            self.get_logger().error(f'Failed to bind Prometheus HTTP server on port {self.metrics_port}: {e}')

    def stop_http_server(self):
        if self.http_server:
            try:
                self.http_server.shutdown()
                self.http_server.server_close()
            except Exception:
                pass

    def heartbeat_typed_callback(self, msg: RobotHeartbeat):
        r_id = msg.robot_id if msg.robot_id else 'unknown'
        with self.lock:
            self.metrics_cache[r_id] = {
                'cpu_pct': float(msg.cpu_utilization_percent),
                'battery_pct': float(msg.battery_percentage),
                'battery_volts': float(msg.battery_voltage_v),
                'rssi_dbm': float(msg.wifi_rssi_dbm),
                'topic_latency_ms': float(msg.topic_latency_ms),
                'packets_dropped': int(msg.packets_dropped_count),
                'lifecycle': int(msg.lifecycle_state),
                'last_seen': time.time()
            }

    def heartbeat_json_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
            r_id = data.get('robot_id', 'unknown')
            with self.lock:
                self.metrics_cache[r_id] = {
                    'cpu_pct': float(data.get('cpu_utilization_percent', 0.0)),
                    'battery_pct': float(data.get('battery_percentage', 100.0)),
                    'battery_volts': float(data.get('battery_voltage_v', 12.0)),
                    'rssi_dbm': float(data.get('wifi_rssi_dbm', -50.0)),
                    'topic_latency_ms': float(data.get('topic_latency_ms', 0.0)),
                    'packets_dropped': int(data.get('packets_dropped_count', 0)),
                    'lifecycle': int(data.get('lifecycle_state', 3)),
                    'last_seen': time.time()
                }
        except Exception:
            pass

    def generate_prometheus_text(self) -> str:
        """Constructs Prometheus standard exposition format string."""
        lines = []
        with self.lock:
            # 1. Battery Percentage
            lines.append('# HELP robot_battery_percentage Current battery state of charge (percentage)')
            lines.append('# TYPE robot_battery_percentage gauge')
            for r_id, m in self.metrics_cache.items():
                lines.append(f'robot_battery_percentage{{robot_id="{r_id}"}} {m["battery_pct"]:.2f}')
                
            # 2. CPU Utilization
            lines.append('# HELP robot_cpu_utilization_percent Onboard SBC CPU load percentage')
            lines.append('# TYPE robot_cpu_utilization_percent gauge')
            for r_id, m in self.metrics_cache.items():
                lines.append(f'robot_cpu_utilization_percent{{robot_id="{r_id}"}} {m["cpu_pct"]:.2f}')
                
            # 3. Wi-Fi RSSI
            lines.append('# HELP robot_wifi_rssi_dbm RF link signal strength (dBm)')
            lines.append('# TYPE robot_wifi_rssi_dbm gauge')
            for r_id, m in self.metrics_cache.items():
                lines.append(f'robot_wifi_rssi_dbm{{robot_id="{r_id}"}} {m["rssi_dbm"]:.1f}')
                
            # 4. Latency
            lines.append('# HELP robot_topic_latency_ms End-to-end DDS topic latency (milliseconds)')
            lines.append('# TYPE robot_topic_latency_ms gauge')
            for r_id, m in self.metrics_cache.items():
                lines.append(f'robot_topic_latency_ms{{robot_id="{r_id}"}} {m.get("topic_latency_ms", 0.0):.2f}')
                
            # 5. Heartbeat timestamp
            lines.append('# HELP robot_heartbeat_timestamp_seconds Last heartbeat received epoch timestamp')
            lines.append('# TYPE robot_heartbeat_timestamp_seconds gauge')
            for r_id, m in self.metrics_cache.items():
                lines.append(f'robot_heartbeat_timestamp_seconds{{robot_id="{r_id}"}} {m["last_seen"]:.3f}')
                
        return '\n'.join(lines) + '\n'

    def publish_metrics_summary(self):
        msg = String()
        with self.lock:
            msg.data = json.dumps(self.metrics_cache)
        self.pub_fleet_metrics.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PrometheusROSExporter()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.stop_http_server()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
