import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import String
import json
import time

try:
    from cps_msgs.msg import RobotHeartbeat
    HAVE_CPS_MSGS = True
except ImportError:
    HAVE_CPS_MSGS = False


class HealthWatchdogNode(Node):
    """
    HealthWatchdogNode: Real-time Distributed Health & Failover Supervisor.
    
    Tracks periodic heartbeats from all edge robots. If a robot misses heartbeats
    (timeout exceeded or Wi-Fi dropped), triggers safe stop alerts and re-assigns
    pending tasks to backup agents.
    """
    def __init__(self):
        super().__init__('health_watchdog_node')
        
        self.declare_parameter('heartbeat_timeout_sec', 3.0)
        self.timeout = float(self.get_parameter('heartbeat_timeout_sec').value)
        
        # State: {robot_id: {'last_seen': float, 'battery': float, 'cpu': float, 'rssi': int, 'status': str}}
        self.agents = {}
        
        # Subscriptions
        self.sub_heartbeat_json = self.create_subscription(
            String, '/cps/heartbeats_json', self.heartbeat_json_callback, 10
        )
        if HAVE_CPS_MSGS:
            self.sub_heartbeat_typed = self.create_subscription(
                RobotHeartbeat, '/cps/heartbeats', self.heartbeat_typed_callback, 10
            )
        else:
            self.sub_heartbeat_typed = None
            
        # Publishers
        self.pub_alerts = self.create_publisher(String, '/cps/system_alerts', 10)
        self.pub_fleet_health = self.create_publisher(String, '/cps/fleet_health', 10)
        
        # 1 Hz Watchdog Timer
        self.timer = self.create_timer(1.0, self.supervision_loop)
        self.get_logger().info(f'Health Watchdog Supervisor initialized (timeout={self.timeout}s).')

    def heartbeat_typed_callback(self, msg: RobotHeartbeat):
        r_id = msg.robot_id if msg.robot_id else 'unknown'
        self.agents[r_id] = {
            'last_seen': time.time(),
            'battery': float(msg.battery_percentage),
            'cpu': float(msg.cpu_utilization_percent),
            'rssi': int(msg.wifi_rssi_dbm),
            'lifecycle': int(msg.lifecycle_state),
            'status': 'HEALTHY'
        }

    def heartbeat_json_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
            r_id = data.get('robot_id', 'unknown')
            self.agents[r_id] = {
                'last_seen': time.time(),
                'battery': float(data.get('battery_percentage', 100.0)),
                'cpu': float(data.get('cpu_utilization_percent', 0.0)),
                'rssi': int(data.get('wifi_rssi_dbm', -50)),
                'lifecycle': int(data.get('lifecycle_state', 3)),
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
                    'silent_duration_sec': round(dt, 2),
                    'action': 'REASSIGN_TASKS',
                    'timestamp': now
                })
                self.pub_alerts.publish(alert_msg)
                
        # Publish fleet health summary
        health_summary = String()
        health_summary.data = json.dumps({
            'total_agents': len(self.agents),
            'agents': self.agents,
            'timestamp': now
        })
        self.pub_fleet_health.publish(health_summary)


def main(args=None):
    rclpy.init(args=args)
    node = HealthWatchdogNode()
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
