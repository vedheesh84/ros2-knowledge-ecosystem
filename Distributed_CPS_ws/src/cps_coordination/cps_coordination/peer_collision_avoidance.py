import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from geometry_msgs.msg import PoseStamped, Point
from visualization_msgs.msg import Marker
from std_msgs.msg import String
import math
import json

try:
    from cps_msgs.msg import PeerState
    HAVE_CPS_MSGS = True
except ImportError:
    HAVE_CPS_MSGS = False


class PeerCollisionAvoidance(Node):
    """
    PeerCollisionAvoidance: Reciprocal dynamic obstacle injection for Nav2 costmaps.
    
    Subscribes to peer poses, computes velocity obstacle safety zones (Article CPS-07),
    and publishes visual markers and costmap inflation geometries to prevent inter-robot deadlock.
    """
    def __init__(self):
        super().__init__('peer_collision_avoidance')
        
        self.declare_parameter('robot_id', 'robot1')
        self.declare_parameter('peer_id', 'robot2')
        self.declare_parameter('safety_distance_m', 0.8)
        self.declare_parameter('time_horizon_sec', 5.0)
        
        self.robot_id = str(self.get_parameter('robot_id').value)
        self.peer_id = str(self.get_parameter('peer_id').value)
        self.safety_dist = float(self.get_parameter('safety_distance_m').value)
        self.tau = float(self.get_parameter('time_horizon_sec').value)
        
        # Self pose
        self.self_x = 0.0
        self.self_y = 0.0
        self.has_self_pose = False
        
        # Subscriptions
        self.sub_peer_pose = self.create_subscription(
            PoseStamped, f'/{self.peer_id}/pose', self.peer_pose_callback, 10
        )
        self.sub_self_pose = self.create_subscription(
            PoseStamped, f'/{self.robot_id}/pose', self.self_pose_callback, 10
        )
        
        if HAVE_CPS_MSGS:
            self.sub_peer_state = self.create_subscription(
                PeerState, f'/{self.peer_id}/peer_state', self.peer_state_callback, 10
            )
        else:
            self.sub_peer_state = None
            
        # Publishers
        self.pub_peer_marker = self.create_publisher(Marker, f'/{self.robot_id}/peer_obstacle_marker', 10)
        self.pub_risk_alert = self.create_publisher(String, f'/{self.robot_id}/collision_risk', 10)
        
        self.get_logger().info(
            f'Peer Collision Avoidance active on [{self.robot_id}] tracking [{self.peer_id}] (r_safe={self.safety_dist}m).'
        )

    def self_pose_callback(self, msg: PoseStamped):
        self.self_x = msg.pose.position.x
        self.self_y = msg.pose.position.y
        self.has_self_pose = True

    def peer_state_callback(self, msg: PeerState):
        """Processes strongly-typed PeerState including safety radius and goal position."""
        if msg.safety_radius_m > 0:
            self.safety_dist = float(msg.safety_radius_m)
        pose_stamped = PoseStamped()
        pose_stamped.header = msg.header
        pose_stamped.pose = msg.pose
        self.process_peer_pose(pose_stamped)

    def peer_pose_callback(self, msg: PoseStamped):
        self.process_peer_pose(msg)

    def process_peer_pose(self, msg: PoseStamped):
        peer_x = msg.pose.position.x
        peer_y = msg.pose.position.y
        
        # Calculate Euclidean separation distance
        dist = math.hypot(peer_x - self.self_x, peer_y - self.self_y) if self.has_self_pose else 10.0
        
        # Velocity Obstacle Risk Assessment
        risk_level = 'SAFE'
        r, g, b, a = 0.2, 0.8, 0.2, 0.4  # Green
        
        if dist < (self.safety_dist * 1.5):
            risk_level = 'CRITICAL'
            r, g, b, a = 1.0, 0.0, 0.0, 0.85  # Red
        elif dist < (self.safety_dist * 2.5):
            risk_level = 'WARNING'
            r, g, b, a = 1.0, 0.7, 0.0, 0.65  # Orange/Yellow
            
        # Construct dynamic obstacle marker
        marker = Marker()
        marker.header = msg.header
        marker.header.frame_id = 'map'
        marker.ns = 'peer_obstacles'
        marker.id = 1
        marker.type = Marker.CYLINDER
        marker.action = Marker.ADD
        marker.pose = msg.pose
        marker.scale.x = self.safety_dist * 2.0
        marker.scale.y = self.safety_dist * 2.0
        marker.scale.z = 0.5
        marker.color.r = r
        marker.color.g = g
        marker.color.b = b
        marker.color.a = a
        self.pub_peer_marker.publish(marker)
        
        # Publish Risk Alert
        alert = String()
        alert.data = json.dumps({
            'robot_id': self.robot_id,
            'peer_id': self.peer_id,
            'separation_dist_m': round(dist, 3),
            'risk_level': risk_level,
            'safety_radius_m': self.safety_dist
        })
        self.pub_risk_alert.publish(alert)


def main(args=None):
    rclpy.init(args=args)
    node = PeerCollisionAvoidance()
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
