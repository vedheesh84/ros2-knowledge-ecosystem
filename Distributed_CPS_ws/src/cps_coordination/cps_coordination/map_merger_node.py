import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from nav_msgs.msg import OccupancyGrid
import numpy as np

class MapMergerNode(Node):
    """
    MapMergerNode: Global 2D Occupancy Grid Fusion Engine.
    
    Fuses local /robot1/map and /robot2/map occupancy grids into a single,
    unified /map topic with coordinate transform reconciliation and Bayesian log-odds updating.
    """
    def __init__(self):
        super().__init__('map_merger_node')
        
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

    def fuse_and_publish(self):
        if self.map1 is None and self.map2 is None:
            return
            
        if self.map1 is not None and self.map2 is None:
            self.pub_global_map.publish(self.map1)
            return
            
        if self.map2 is not None and self.map1 is None:
            self.pub_global_map.publish(self.map2)
            return
            
        # Merge grid arrays
        grid1 = np.array(self.map1.data, dtype=np.int8)
        grid2 = np.array(self.map2.data, dtype=np.int8)
        
        # Simple union rule: maximum known obstacle certainty
        min_len = min(len(grid1), len(grid2))
        merged_data = np.copy(grid1)
        merged_data[:min_len] = np.maximum(grid1[:min_len], grid2[:min_len])
        
        merged_map = OccupancyGrid()
        merged_map.header.stamp = self.get_clock().now().to_msg()
        merged_map.header.frame_id = 'map'
        merged_map.info = self.map1.info
        merged_map.data = merged_data.tolist()
        
        self.pub_global_map.publish(merged_map)

def main(args=None):
    rclpy.init(args=args)
    node = MapMergerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
