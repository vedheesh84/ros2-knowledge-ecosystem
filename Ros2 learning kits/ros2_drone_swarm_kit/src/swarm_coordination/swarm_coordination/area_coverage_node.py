#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String

class AreaCoverageNode(Node):
    """
    Decentralized area coverage and grid sweep partitioning node.
    Partitions a rectangular search region into parallel lanes across N drones
    and sequences lawnmower search waypoints.
    """
    def __init__(self):
        super().__init__('area_coverage_node')
        self.declare_parameter('area_min_x', -3.0)
        self.declare_parameter('area_max_x', 3.0)
        self.declare_parameter('area_min_y', -3.0)
        self.declare_parameter('area_max_y', 3.0)
        self.declare_parameter('sweep_altitude', 1.8)

        self.min_x = float(self.get_parameter('area_min_x').value)
        self.max_x = float(self.get_parameter('area_max_x').value)
        self.min_y = float(self.get_parameter('area_min_y').value)
        self.max_y = float(self.get_parameter('area_max_y').value)
        self.alt = float(self.get_parameter('sweep_altitude').value)

        # Drone publishers
        self.pubs = {
            'drone_0': self.create_publisher(PoseStamped, '/drone_0/target_pose', 10),
            'drone_1': self.create_publisher(PoseStamped, '/drone_1/target_pose', 10),
            'drone_2': self.create_publisher(PoseStamped, '/drone_2/target_pose', 10),
        }
        self.status_pub = self.create_publisher(String, '/swarm/coverage_status', 10)

        # Plan lanes: Drone 0 center, Drone 1 North (+Y), Drone 2 South (-Y)
        y_span = (self.max_y - self.min_y) / 3.0
        self.lanes = {
            'drone_0': 0.0,
            'drone_1': self.min_y + 2.5 * y_span,
            'drone_2': self.min_y + 0.5 * y_span,
        }

        self.step = 0
        self.timer = self.create_timer(1.0, self.dispatch_sweep_step)
        self.get_logger().info(
            f'Area Coverage Node online. Region: [{self.min_x}, {self.max_x}] x [{self.min_y}, {self.max_y}] at {self.alt}m.'
        )
        self.dispatch_sweep_step()

    def dispatch_sweep_step(self):
        # Sweep back and forth along X for each drone's assigned Y lane
        x_target = self.min_x if (self.step % 2 == 0) else self.max_x
        now = self.get_clock().now().to_msg()

        for drone_id, pub in self.pubs.items():
            pose = PoseStamped()
            pose.header.stamp = now
            pose.header.frame_id = 'world'
            pose.pose.position.x = x_target
            pose.pose.position.y = self.lanes[drone_id]
            pose.pose.position.z = self.alt
            pose.pose.orientation.w = 1.0
            pub.publish(pose)

        status_msg = String()
        status_msg.data = f'STEP_{self.step}: X={x_target:.1f}, Lanes={self.lanes}'
        self.status_pub.publish(status_msg)
        self.get_logger().info(f'Coverage Sweep Step {self.step}: Dispatched X={x_target:.1f} to 3 drones.')
        self.step += 1

def main(args=None):
    rclpy.init(args=args)
    node = AreaCoverageNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
