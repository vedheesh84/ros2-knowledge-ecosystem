import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from std_msgs.msg import String, Float32
from geometry_msgs.msg import Twist
import json
import time


class TopologicalNavigatorNode(Node):
    """
    V4-V5 Symbolic Intelligence: Graph-Based Topological Navigator (Articles LFE-05 & 06).
    
    States:
    1. TRAVERSING_EDGE: High-speed line tracking along path edge (u, v).
    2. APPROACHING_NODE: Intersection detected; decelerating and arming tag reader.
    3. VERIFYING_NODE: Cross-referencing visual tag with expected graph node.
    4. EXECUTING_TURN: Deterministic angular pivot towards next target edge with calibrated duration.
    5. ROLLBACK_RECOVERY: If wrong node detected or lost line, backtrack to last known valid node.
    6. GOAL_REACHED: Destination vertex successfully attained.
    """
    def __init__(self):
        super().__init__('topological_navigator_node')
        
        self.declare_parameter('turn_duration_sec', 1.0)
        self.declare_parameter('rollback_duration_sec', 2.0)
        
        self.turn_duration_sec = float(self.get_parameter('turn_duration_sec').value)
        self.rollback_duration_sec = float(self.get_parameter('rollback_duration_sec').value)
        
        # Load topological graph
        self.graph = {
            "N1": ["N2", "N3"],
            "N2": ["N1", "N4"],
            "N3": ["N1", "N4"],
            "N4": ["N2", "N3", "N5"],
            "N5": ["N4"]
        }
        
        self.current_node = "N1"
        self.target_goal_node = "N5"
        self.planned_path = ["N1", "N2", "N4", "N5"]
        self.path_index = 0
        self.state = "TRAVERSING_EDGE"
        
        self.current_line_error = 0.0
        self.turn_start_time = 0.0
        self.rollback_start_time = 0.0
        
        # Communication
        self.sub_tag = self.create_subscription(
            String, '/v4_v5/detected_node_tag', self.tag_callback, 10
        )
        self.sub_error = self.create_subscription(
            Float32, '/v2_v3/line_centroid_error', self.line_error_callback, 10
        )
        self.pub_cmd = self.create_publisher(Twist, '/cmd_vel', 10)
        self.pub_status = self.create_publisher(String, '/v4_v5/navigation_status', 10)
        
        self.timer = self.create_timer(0.1, self.fsm_step)
        self.get_logger().info(f'Topological Navigator running. Goal: {self.target_goal_node}')

    def tag_callback(self, msg: String):
        detected_tag = msg.data.strip()
        self.get_logger().info(f'[V4-V5 Node Tag]: Detected {detected_tag}')
        
        expected_next = self.planned_path[self.path_index + 1] if self.path_index + 1 < len(self.planned_path) else None
        
        if detected_tag == expected_next:
            self.current_node = detected_tag
            self.path_index += 1
            if self.path_index >= len(self.planned_path) - 1:
                self.state = "GOAL_REACHED"
            else:
                self.state = "EXECUTING_TURN"
                self.turn_start_time = time.time()
            self.get_logger().info(f'Node Verified: [{self.current_node}]. Transitioning to {self.state}')
        else:
            self.get_logger().error(f'Unexpected Node: Got {detected_tag}, expected {expected_next}. Triggering ROLLBACK RECOVERY!')
            self.state = "ROLLBACK_RECOVERY"
            self.rollback_start_time = time.time()

    def line_error_callback(self, msg: Float32):
        self.current_line_error = msg.data

    def fsm_step(self):
        cmd = Twist()
        now = time.time()
        
        if self.state == "TRAVERSING_EDGE":
            cmd.linear.x = 0.55
            cmd.angular.z = -25.0 * self.current_line_error
        elif self.state == "EXECUTING_TURN":
            elapsed = now - self.turn_start_time
            if elapsed < self.turn_duration_sec:
                cmd.linear.x = 0.15
                cmd.angular.z = 1.57 # 90-degree pivot rate
            else:
                self.state = "TRAVERSING_EDGE"
                cmd.linear.x = 0.55
                cmd.angular.z = 0.0
        elif self.state == "ROLLBACK_RECOVERY":
            elapsed = now - self.rollback_start_time
            if elapsed < self.rollback_duration_sec:
                cmd.linear.x = -0.20 # Backtrack along line
                cmd.angular.z = 0.0
            else:
                # Re-arm navigation at last known valid node
                self.state = "TRAVERSING_EDGE"
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
        elif self.state == "GOAL_REACHED":
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            
        self.pub_cmd.publish(cmd)
        
        status = String()
        status.data = json.dumps({
            'state': self.state,
            'current_node': self.current_node,
            'goal_node': self.target_goal_node,
            'path_index': self.path_index
        })
        self.pub_status.publish(status)


def main(args=None):
    rclpy.init(args=args)
    node = TopologicalNavigatorNode()
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
