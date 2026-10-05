import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import PoseStamped, Point
from std_msgs.msg import String
import json
import time

class BaseCoordinatorNode(Node):
    """
    BaseCoordinatorNode: Central Mission Dispatcher & Fleet State Machine.
    
    Responsibilities:
    1. Tracks online status and readiness of heterogeneous edge robots.
    2. Receives discovery events from Robot 1 (Explorer) when frontier goals or objects are found.
    3. Dispatches autonomous tasks (Navigate, Pick, Place) to Robot 2 (Transporter/Manipulator).
    4. Orchestrates global mission lifecycle with timeout supervision.
    """
    def __init__(self):
        super().__init__('base_coordinator_node')
        
        self.declare_parameter('mission_mode', 'AUTONOMOUS_COORDINATION')
        self.declare_parameter('task_timeout_sec', 120.0)
        
        self.reliable_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )
        
        # State tracking
        self.fleet_status = {
            'robot1': {'state': 'IDLE', 'battery': 100.0, 'last_seen': time.time()},
            'robot2': {'state': 'IDLE', 'battery': 100.0, 'last_seen': time.time()}
        }
        self.mission_phase = 'STANDBY'
        self.active_tasks = {}
        
        # Subscriptions
        self.sub_robot1_status = self.create_subscription(
            String, '/robot1/status', self.robot1_status_callback, 10
        )
        self.sub_robot2_status = self.create_subscription(
            String, '/robot2/status', self.robot2_status_callback, 10
        )
        self.sub_target_found = self.create_subscription(
            PoseStamped, '/robot1/target_detected', self.target_detected_callback, 10
        )
        
        # Publishers
        self.pub_robot1_cmd = self.create_publisher(String, '/robot1/task_command', self.reliable_qos)
        self.pub_robot2_goal = self.create_publisher(PoseStamped, '/robot2/goal_pose', self.reliable_qos)
        self.pub_global_mission_state = self.create_publisher(String, '/cps/mission_state', 10)
        
        # Coordination Timer (1 Hz)
        self.timer = self.create_timer(1.0, self.coordination_loop)
        self.get_logger().info('Base Coordinator Node initialized and listening for fleet events.')

    def robot1_status_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
            self.fleet_status['robot1']['state'] = data.get('state', 'UNKNOWN')
            self.fleet_status['robot1']['battery'] = data.get('battery', 100.0)
            self.fleet_status['robot1']['last_seen'] = time.time()
        except Exception:
            self.fleet_status['robot1']['state'] = msg.data
            self.fleet_status['robot1']['last_seen'] = time.time()

    def robot2_status_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
            self.fleet_status['robot2']['state'] = data.get('state', 'UNKNOWN')
            self.fleet_status['robot2']['battery'] = data.get('battery', 100.0)
            self.fleet_status['robot2']['last_seen'] = time.time()
        except Exception:
            self.fleet_status['robot2']['state'] = msg.data
            self.fleet_status['robot2']['last_seen'] = time.time()

    def target_detected_callback(self, msg: PoseStamped):
        self.get_logger().info(
            f'Target object detected by Explorer at x={msg.pose.position.x:.2f}, y={msg.pose.position.y:.2f}!'
        )
        if self.mission_phase == 'EXPLORING' or self.mission_phase == 'STANDBY':
            self.dispatch_manipulation_mission(msg)

    def dispatch_manipulation_mission(self, target_pose: PoseStamped):
        self.mission_phase = 'DISPATCHING_MANIPULATOR'
        self.get_logger().info('Dispatching Transporter/Manipulator (Robot 2) to target coordinates.')
        
        # Command Robot 2 to navigate to target pose
        self.pub_robot2_goal.publish(target_pose)
        
        # Notify Robot 1 to hold or continue perimeter scanning
        hold_msg = String()
        hold_msg.data = json.dumps({'action': 'PERIMETER_SURVEY', 'priority': 1})
        self.pub_robot1_cmd.publish(hold_msg)

    def coordination_loop(self):
        now = time.time()
        # Check fleet liveness
        for r_id, info in self.fleet_status.items():
            if now - info['last_seen'] > 5.0:
                info['state'] = 'OFFLINE'
                
        # Publish global state summary
        state_msg = String()
        state_msg.data = json.dumps({
            'phase': self.mission_phase,
            'fleet': self.fleet_status,
            'timestamp': now
        })
        self.pub_global_mission_state.publish(state_msg)

def main(args=None):
    rclpy.init(args=args)
    node = BaseCoordinatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
