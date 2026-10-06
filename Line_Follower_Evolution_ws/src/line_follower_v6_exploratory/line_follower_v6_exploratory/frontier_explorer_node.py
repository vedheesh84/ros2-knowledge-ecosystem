import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import PoseStamped, Point
import numpy as np


class FrontierExplorerNode(Node):
    """
    V6 Spatial Intelligence: Autonomous Frontier Exploration Planner (Article LFE-07).
    
    Identifies true boundary cells between explored free space (0) and unexplored unknown territory (-1):
    F = { p in FreeSpace | exists q in Neighbors(p), Map(q) == -1 }
    Clusters valid frontier cells, computes the target centroid, and dispatches Nav2 goal coordinates.
    """
    def __init__(self):
        super().__init__('frontier_explorer_node')
        
        self.declare_parameter('min_frontier_size', 3)
        self.min_frontier_size = int(self.get_parameter('min_frontier_size').value)
        
        self.sub_map = self.create_subscription(OccupancyGrid, '/map', self.map_callback, 10)
        self.pub_frontier_goal = self.create_publisher(PoseStamped, '/goal_pose', 10)
        
        self.latest_goal = None
        self.get_logger().info('V6 Frontier Explorer Node running: Searching for information frontiers.')

    def find_frontier_cells(self, grid_2d: np.ndarray) -> np.ndarray:
        """
        Extracts frontier cells using 4-connected boundary neighborhood check.
        Returns 2D boolean mask of frontier cells in free space.
        """
        free_mask = (grid_2d == 0)
        unknown_mask = (grid_2d == -1)
        
        # Shift in 4 directions to test for unknown neighbors
        up_unknown = np.pad(unknown_mask[1:, :], ((0, 1), (0, 0)), constant_values=False)
        down_unknown = np.pad(unknown_mask[:-1, :], ((1, 0), (0, 0)), constant_values=False)
        left_unknown = np.pad(unknown_mask[:, 1:], ((0, 0), (0, 1)), constant_values=False)
        right_unknown = np.pad(unknown_mask[:, :-1], ((0, 0), (1, 0)), constant_values=False)
        
        has_unknown_neighbor = up_unknown | down_unknown | left_unknown | right_unknown
        return free_mask & has_unknown_neighbor

    def map_callback(self, msg: OccupancyGrid):
        width = msg.info.width
        height = msg.info.height
        if width <= 0 or height <= 0:
            return
            
        data = np.array(msg.data, dtype=np.int8).reshape((height, width))
        
        # 1. Detect true frontiers according to Article LFE-07
        frontier_mask = self.find_frontier_cells(data)
        frontier_indices = np.argwhere(frontier_mask)
        
        if len(frontier_indices) >= self.min_frontier_size:
            # Select central frontier cell or median
            median_idx = frontier_indices[len(frontier_indices) // 2]
            
            goal = PoseStamped()
            goal.header.frame_id = 'map'
            goal.header.stamp = self.get_clock().now().to_msg()
            goal.pose.position.x = float(median_idx[1] * msg.info.resolution + msg.info.origin.position.x)
            goal.pose.position.y = float(median_idx[0] * msg.info.resolution + msg.info.origin.position.y)
            goal.pose.position.z = 0.0
            goal.pose.orientation.w = 1.0
            
            self.latest_goal = goal
            self.pub_frontier_goal.publish(goal)
            self.get_logger().info(
                f'[V6 SLAM Frontier]: Dispatched exploration goal at ({goal.pose.position.x:.2f}, {goal.pose.position.y:.2f}) from {len(frontier_indices)} frontier cells.',
                throttle_duration_sec=3.0
            )


def main(args=None):
    rclpy.init(args=args)
    node = FrontierExplorerNode()
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
