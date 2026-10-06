import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from nav_msgs.msg import OccupancyGrid
import numpy as np
import math


class MapMergerNode(Node):
    """
    MapMergerNode: Global 2D Occupancy Grid Fusion Engine.
    
    Fuses local /robot1/map and /robot2/map occupancy grids into a single,
    unified /map topic with coordinate transform reconciliation and Bayesian
    log-odds updating as formulated in Article CPS-05:
    
    L(m_fused(x, y)) = L(m_1(x, y)) + L(m_2(x, y)) - L_0
    where L(p) = ln(p / (1 - p)).
    """
    def __init__(self):
        super().__init__('map_merger_node')
        
        self.declare_parameter('fusion_method', 'log_odds')
        self.fusion_method = self.get_parameter('fusion_method').value
        
        self.latched_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )
        
        self.map1 = None
        self.map2 = None
        
        # Subscriptions
        self.sub_map1 = self.create_subscription(
            OccupancyGrid, '/robot1/map', self.map1_callback, self.latched_qos
        )
        self.sub_map2 = self.create_subscription(
            OccupancyGrid, '/robot2/map', self.map2_callback, self.latched_qos
        )
        
        # Merged Global Map Publisher
        self.pub_global_map = self.create_publisher(OccupancyGrid, '/map', self.latched_qos)
        
        # Fuse timer (1 Hz)
        self.timer = self.create_timer(1.0, self.fuse_and_publish)
        self.get_logger().info('Map Merger Node initialized for multi-robot spatial fusion.')

    def map1_callback(self, msg: OccupancyGrid):
        self.map1 = msg

    def map2_callback(self, msg: OccupancyGrid):
        self.map2 = msg

    @staticmethod
    def fuse_cell_log_odds(c1: int, c2: int) -> int:
        """Fuses two cell values using Bayesian log-odds formula."""
        if c1 < 0 and c2 < 0:
            return -1
        if c1 < 0:
            return c2
        if c2 < 0:
            return c1
            
        # Prior occupancy L_0 = 0 (P_0 = 0.5)
        # Convert ROS [0, 100] to probability in [0.01, 0.99] to prevent infinite log-odds
        p1 = max(0.01, min(0.99, c1 / 100.0))
        p2 = max(0.01, min(0.99, c2 / 100.0))
        
        l1 = math.log(p1 / (1.0 - p1))
        l2 = math.log(p2 / (1.0 - p2))
        l_fused = l1 + l2
        
        p_fused = 1.0 / (1.0 + math.exp(-l_fused))
        return int(round(p_fused * 100.0))

    def fuse_and_publish(self):
        if self.map1 is None and self.map2 is None:
            return
            
        if self.map1 is not None and self.map2 is None:
            self.pub_global_map.publish(self.map1)
            return
            
        if self.map2 is not None and self.map1 is None:
            self.pub_global_map.publish(self.map2)
            return
            
        info1 = self.map1.info
        info2 = self.map2.info
        
        # Fast path: matching geometry and resolution
        if (info1.width == info2.width and
            info1.height == info2.height and
            abs(info1.resolution - info2.resolution) < 1e-4 and
            abs(info1.origin.position.x - info2.origin.position.x) < 1e-4 and
            abs(info1.origin.position.y - info2.origin.position.y) < 1e-4):
            
            g1 = np.array(self.map1.data, dtype=np.int16)
            g2 = np.array(self.map2.data, dtype=np.int16)
            
            if self.fusion_method == 'max_likelihood':
                # Unknown (-1) handled: replace -1 with min value for comparison
                valid_g1 = np.where(g1 >= 0, g1, -1)
                valid_g2 = np.where(g2 >= 0, g2, -1)
                merged = np.maximum(valid_g1, valid_g2)
                merged = np.where((g1 < 0) & (g2 < 0), -1, merged)
            else:
                # Log-odds vectorization
                # Identify cells
                both_unknown = (g1 < 0) & (g2 < 0)
                g1_only = (g1 >= 0) & (g2 < 0)
                g2_only = (g2 >= 0) & (g1 < 0)
                both_valid = (g1 >= 0) & (g2 >= 0)
                
                merged = np.full_like(g1, -1, dtype=np.int8)
                merged[g1_only] = g1[g1_only]
                merged[g2_only] = g2[g2_only]
                
                if np.any(both_valid):
                    p1 = np.clip(g1[both_valid] / 100.0, 0.01, 0.99)
                    p2 = np.clip(g2[both_valid] / 100.0, 0.01, 0.99)
                    l1 = np.log(p1 / (1.0 - p1))
                    l2 = np.log(p2 / (1.0 - p2))
                    l_fused = l1 + l2
                    p_fused = 1.0 / (1.0 + np.exp(-l_fused))
                    merged[both_valid] = np.round(p_fused * 100.0).astype(np.int8)
            
            merged_map = OccupancyGrid()
            merged_map.header.stamp = self.get_clock().now().to_msg()
            merged_map.header.frame_id = 'map'
            merged_map.info = info1
            merged_map.data = merged.astype(np.int8).tolist()
            self.pub_global_map.publish(merged_map)
            return

        # General path: Reconcile bounding boxes across heterogeneous origin/dimension
        res = min(info1.resolution, info2.resolution)
        x_min = min(info1.origin.position.x, info2.origin.position.x)
        y_min = min(info1.origin.position.y, info2.origin.position.y)
        x_max = max(info1.origin.position.x + info1.width * info1.resolution,
                    info2.origin.position.x + info2.width * info2.resolution)
        y_max = max(info1.origin.position.y + info1.height * info1.resolution,
                    info2.origin.position.y + info2.height * info2.resolution)
        
        fused_w = int(math.ceil((x_max - x_min) / res))
        fused_h = int(math.ceil((y_max - y_min) / res))
        
        fused_grid = np.full((fused_h, fused_w), -1, dtype=np.int8)
        
        # Project map1
        g1_2d = np.array(self.map1.data, dtype=np.int8).reshape((info1.height, info1.width))
        off_x1 = int(round((info1.origin.position.x - x_min) / res))
        off_y1 = int(round((info1.origin.position.y - y_min) / res))
        fused_grid[off_y1:off_y1 + info1.height, off_x1:off_x1 + info1.width] = g1_2d
        
        # Project and fuse map2
        g2_2d = np.array(self.map2.data, dtype=np.int8).reshape((info2.height, info2.width))
        off_x2 = int(round((info2.origin.position.x - x_min) / res))
        off_y2 = int(round((info2.origin.position.y - y_min) / res))
        
        sub_fused = fused_grid[off_y2:off_y2 + info2.height, off_x2:off_x2 + info2.width]
        
        # Cell-by-cell fusion on subregion
        for r in range(info2.height):
            for c in range(info2.width):
                v1 = int(sub_fused[r, c])
                v2 = int(g2_2d[r, c])
                sub_fused[r, c] = self.fuse_cell_log_odds(v1, v2)
                
        fused_grid[off_y2:off_y2 + info2.height, off_x2:off_x2 + info2.width] = sub_fused
        
        merged_map = OccupancyGrid()
        merged_map.header.stamp = self.get_clock().now().to_msg()
        merged_map.header.frame_id = 'map'
        merged_map.info.resolution = float(res)
        merged_map.info.width = int(fused_w)
        merged_map.info.height = int(fused_h)
        merged_map.info.origin.position.x = float(x_min)
        merged_map.info.origin.position.y = float(y_min)
        merged_map.info.origin.position.z = 0.0
        merged_map.info.origin.orientation.w = 1.0
        merged_map.data = fused_grid.flatten().tolist()
        
        self.pub_global_map.publish(merged_map)


def main(args=None):
    rclpy.init(args=args)
    node = MapMergerNode()
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
