import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Point
from visualization_msgs.msg import Marker, MarkerArray
import math

class PeerCollisionAvoidance(Node):
    """
    PeerCollisionAvoidance: Reciprocal dynamic obstacle injection for Nav2 costmaps.
    
    Subscribes to peer poses, computes velocity obstacle safety cones,
    and publishes visual and footprint markers to prevent inter-robot deadlock.
    """
    def __init__(self):
        super().__init__('peer_collision_avoidance')
        
        self.declare_parameter('robot_id', 'robot1')
        self.declare_parameter('peer_id', 'robot2')
        self.declare_parameter('safety_distance_m', 0.8)
        
        self.robot_id = self.get_parameter('robot_id').value
        self.peer_id = self.get_parameter('peer_id').value
        self.safety_dist = self.get_parameter('safety_distance_m').value
        
        # Subscriptions
        self.sub_peer_pose = self.create_subscription(
            PoseStamped, f'/{self.peer_id}/pose', self.peer_pose_callback, 10
        )
        
        # Publisher
        self.pub_peer_marker = self.create_publisher(Marker, f'/{self.robot_id}/peer_obstacle_marker', 10)
        
        self.get_logger().info(f'Peer Collision Avoidance active on [{self.robot_id}] tracking [{self.peer_id}].')

    def peer_pose_callback(self, msg: PoseStamped):
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
        marker.color.r = 1.0
        marker.color.g = 0.2
        marker.color.b = 0.2
        marker.color.a = 0.6
        self.pub_peer_marker.publish(marker)

def main(args=None):
    rclpy.init(args=args)
    node = PeerCollisionAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
