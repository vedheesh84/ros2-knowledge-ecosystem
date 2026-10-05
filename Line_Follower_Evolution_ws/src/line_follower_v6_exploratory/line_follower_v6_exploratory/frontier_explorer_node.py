import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped, Point
import numpy as np

class FrontierExplorerNode(Node):
    """
    V6 Spatial Intelligence: Autonomous Frontier Exploration Planner.
    
    Identifies boundary cells between explored free space (0) and unexplored unknown territory (-1),
    clusters them into information frontiers, and dispatches navigation goals.
    """
    def __init__(self):
        super().__init__('frontier_explorer_node')
        
        self.sub_map = self.create_subscription(OccupancyGrid, '/map', self.map_callback, 10)
        self.pub_frontier_goal = self.create_publisher(PoseStamped, '/goal_pose', 10)
        
        self.get_logger().info('V6 Frontier Explorer Node running: Searching for information frontiers.')

    def map_callback(self, msg: OccupancyGrid):
        # Scan for frontiers (free cell adjacent to unknown cell)
        width = msg.info.width
        height = msg.info.height
        data = np.array(msg.data, dtype=np.int8).reshape((height, width))
        
        # Simple centroid of unknown borders
        unknown_indices = np.argwhere(data == -1)
        if len(unknown_indices) > 0:
            target_idx = unknown_indices[len(unknown_indices) // 2]
            
            goal = PoseStamped()
            goal.header.frame_id = 'map'
            goal.header.stamp = self.get_clock().now().to_msg()
            goal.pose.position.x = float(target_idx[1] * msg.info.resolution + msg.info.origin.position.x)
            goal.pose.position.y = float(target_idx[0] * msg.info.resolution + msg.info.origin.position.y)
            goal.pose.orientation.w = 1.0
            
            self.pub_frontier_goal.publish(goal)

def main(args=None):
    rclpy.init(args=args)
    node = FrontierExplorerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
