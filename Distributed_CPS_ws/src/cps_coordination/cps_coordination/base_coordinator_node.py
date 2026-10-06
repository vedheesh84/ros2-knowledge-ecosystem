import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from geometry_msgs.msg import PoseStamped, Point
from std_msgs.msg import String
import json
import time

try:
    from cps_msgs.msg import RobotHeartbeat, TaskAssignment
    from cps_msgs.srv import RequestTask
    HAVE_CPS_MSGS = True
except ImportError:
    HAVE_CPS_MSGS = False


class BaseCoordinatorNode(Node):
    """
    BaseCoordinatorNode: Central Mission Dispatcher & Fleet State Machine.
    
    Responsibilities:
    1. Tracks online status and readiness of heterogeneous edge robots.
    2. Receives discovery events from Robot 1 (Explorer) when frontier goals or objects are found.
    3. Dispatches autonomous tasks (Navigate, Pick, Place) to Robot 2 (Transporter/Manipulator).
    4. Orchestrates global mission lifecycle with timeout supervision.
    5. Implements RequestTask service and publishes strongly-typed TaskAssignment messages.
    """
    def __init__(self):
        super().__init__('base_coordinator_node')
        
        self.declare_parameter('mission_mode', 'AUTONOMOUS_COORDINATION')
        self.declare_parameter('task_timeout_sec', 120.0)
        
        self.mission_mode = self.get_parameter('mission_mode').value
        self.task_timeout_sec = self.get_parameter('task_timeout_sec').value
        
        self.reliable_qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )
        
        # State tracking
        self.fleet_status = {
            'robot1': {'state': 'IDLE', 'battery': 100.0, 'last_seen': time.time(), 'mode': 'EXPLORATION'},
            'robot2': {'state': 'IDLE', 'battery': 100.0, 'last_seen': time.time(), 'mode': 'MANIPULATION'}
        }
        self.mission_phase = 'STANDBY'
        self.pending_tasks = []
        self.active_tasks = {}
        
        # Subscriptions - String compatibility
        self.sub_robot1_status = self.create_subscription(
            String, '/robot1/status', self.robot1_status_callback, 10
        )
        self.sub_robot2_status = self.create_subscription(
            String, '/robot2/status', self.robot2_status_callback, 10
        )
        self.sub_target_found = self.create_subscription(
            PoseStamped, '/robot1/target_detected', self.target_detected_callback, 10
        )
        
        # Subscriptions - Strongly typed RobotHeartbeat
        if HAVE_CPS_MSGS:
            self.sub_heartbeats = self.create_subscription(
                RobotHeartbeat, '/cps/heartbeats', self.heartbeat_callback, 10
            )
            # Service: RequestTask
            self.srv_request_task = self.create_service(
                RequestTask, '/cps/request_task', self.request_task_callback
            )
            # Publisher: TaskAssignment
            self.pub_task_assignment = self.create_publisher(
                TaskAssignment, '/cps/tasks', self.reliable_qos
            )
        else:
            self.sub_heartbeats = None
            self.srv_request_task = None
            self.pub_task_assignment = None
        
        # Publishers
        self.pub_robot1_cmd = self.create_publisher(String, '/robot1/task_command', self.reliable_qos)
        self.pub_robot2_goal = self.create_publisher(PoseStamped, '/robot2/goal_pose', self.reliable_qos)
        self.pub_global_mission_state = self.create_publisher(String, '/cps/mission_state', 10)
        
        # Coordination Timer (1 Hz)
        self.timer = self.create_timer(1.0, self.coordination_loop)
        self.get_logger().info('Base Coordinator Node initialized and listening for fleet events.')

    def heartbeat_callback(self, msg: RobotHeartbeat):
        """Processes strongly-typed RobotHeartbeat telemetry from edge robots."""
        r_id = msg.robot_id if msg.robot_id else 'unknown'
        self.fleet_status[r_id] = {
            'state': 'ACTIVE' if msg.lifecycle_state == 3 else 'INACTIVE',
            'battery': float(msg.battery_percentage),
            'voltage_v': float(msg.battery_voltage_v),
            'cpu_pct': float(msg.cpu_utilization_percent),
            'rssi_dbm': int(msg.wifi_rssi_dbm),
            'mode': msg.operational_mode if msg.operational_mode else 'AUTONOMOUS',
            'last_seen': time.time()
        }

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
        if self.mission_phase in ('EXPLORING', 'STANDBY', 'IDLE'):
            self.dispatch_manipulation_mission(msg)

    def dispatch_manipulation_mission(self, target_pose: PoseStamped):
        self.mission_phase = 'DISPATCHING_MANIPULATOR'
        self.get_logger().info('Dispatching Transporter/Manipulator (Robot 2) to target coordinates.')
        
        # Command Robot 2 to navigate to target pose
        self.pub_robot2_goal.publish(target_pose)
        
        # Publish strongly-typed TaskAssignment if cps_msgs available
        if HAVE_CPS_MSGS and self.pub_task_assignment is not None:
            task = TaskAssignment()
            task.header.stamp = self.get_clock().now().to_msg()
            task.header.frame_id = target_pose.header.frame_id if target_pose.header.frame_id else 'map'
            task.task_id = f'task_pick_{int(time.time())}'
            task.assigned_robot_id = 'robot2'
            task.task_type = TaskAssignment.TASK_TYPE_NAVIGATE_TO_POSE
            task.target_pose = target_pose
            task.priority = 50
            task.timeout_seconds = float(self.task_timeout_sec)
            task.task_parameters = json.dumps({'action': 'PICK_OBJECT', 'object_label': 'sample_box'})
            self.pub_task_assignment.publish(task)
            self.active_tasks[task.task_id] = task
        
        # Notify Robot 1 to hold or continue perimeter scanning
        hold_msg = String()
        hold_msg.data = json.dumps({'action': 'PERIMETER_SURVEY', 'priority': 1})
        self.pub_robot1_cmd.publish(hold_msg)

    def request_task_callback(self, request: RequestTask.Request, response: RequestTask.Response):
        """Handles RequestTask service calls from edge robots requesting missions."""
        self.get_logger().info(f'Task request received from agent [{request.robot_id}]')
        
        if self.pending_tasks:
            next_task = self.pending_tasks.pop(0)
            response.task_available = True
            response.assigned_task = next_task
            response.message = f'Assigned pending task {next_task.task_id}'
        else:
            # Standby/Station-keeping task
            response.task_available = True
            task = TaskAssignment()
            task.header.stamp = self.get_clock().now().to_msg()
            task.header.frame_id = 'map'
            task.task_id = f'standby_{int(time.time())}'
            task.assigned_robot_id = request.robot_id
            task.task_type = TaskAssignment.TASK_TYPE_STATION_KEEPING
            task.target_pose.pose = request.current_pose
            task.priority = 10
            task.timeout_seconds = 60.0
            task.task_parameters = json.dumps({'mode': 'HOLD_POSITION'})
            response.assigned_task = task
            response.message = 'No priority missions pending; assigned station keeping.'
            
        return response

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
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
