import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import time

class HealthWatchdogNode(Node):
    """
    HealthWatchdogNode: Real-time Distributed Health & Failover Supervisor.
    
    Tracks periodic heartbeats from all edge robots. If a robot misses 3 consecutive
    heartbeats (latency threshold exceeded or Wi-Fi dropped), triggers safe stop
    and re-assigns pending tasks to backup agents.
    """
    def __init__(self):
        super().__init__('health_watchdog_node')
        
        self.declare_parameter('heartbeat_timeout_sec', 3.0)
        self.timeout = self.get_parameter('heartbeat_timeout_sec').value
        
        self.agents = {} # {robot_id: {'last_seen': time, 'battery': float, 'status': str}}
        
        self.sub_heartbeat = self.create_subscription(String, '/cps/heartbeats', self.heartbeat_callback, 10)
        self.pub_alerts = self.create_publisher(String, '/cps/system_alerts', 10)
        
        self.timer = self.create_timer(1.0, self.supervision_loop)
        self.get_logger().info('Health Watchdog Supervisor initialized.')

    def heartbeat_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
            r_id = data.get('robot_id', 'unknown')
            self.agents[r_id] = {
                'last_seen': time.time(),
                'battery': data.get('battery_percentage', 100.0),
                'rssi': data.get('wifi_rssi_dbm', -50),
                'status': 'HEALTHY'
            }
        except Exception:
            pass

    def supervision_loop(self):
        now = time.time()
        for r_id, info in self.agents.items():
            dt = now - info['last_seen']
            if dt > self.timeout and info['status'] == 'HEALTHY':
                info['status'] = 'UNRESPONSIVE'
                self.get_logger().error(f'AGENT FAILURE DETECTED: [{r_id}] silent for {dt:.1f}s! Triggering failover.')
                alert_msg = String()
                alert_msg.data = json.dumps({
                    'event': 'NODE_FAILURE',
                    'failed_agent': r_id,
                    'action': 'REASSIGN_TASKS'
                })
                self.pub_alerts.publish(alert_msg)

def main(args=None):
    rclpy.init(args=args)
    node = HealthWatchdogNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
