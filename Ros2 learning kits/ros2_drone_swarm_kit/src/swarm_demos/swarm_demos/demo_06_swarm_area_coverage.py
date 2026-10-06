#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry

class Demo06SwarmAreaCoverage(Node):
    """
    Demo 06: Coordinated Swarm Area Coverage & Search-and-Rescue Grid Sweep.
    Partitions a 6m x 6m search grid into 3 non-overlapping parallel sweep lanes
    assigned to drone_0 (center), drone_1 (north), and drone_2 (south).
    """
    def __init__(self):
        super().__init__('demo_06_swarm_area_coverage')

        self.pubs = {
            'drone_0': self.create_publisher(PoseStamped, '/drone_0/target_pose', 10),
            'drone_1': self.create_publisher(PoseStamped, '/drone_1/target_pose', 10),
            'drone_2': self.create_publisher(PoseStamped, '/drone_2/target_pose', 10),
        }

        # Lane Y-coordinates for each drone
        self.lane_y = {
            'drone_0': 0.0,
            'drone_1': 2.0,
            'drone_2': -2.0,
        }

        self.sweep_x = [-2.5, 2.5]
        self.sweep_alt = 1.8
        self.pass_idx = 0

        self.timer = self.create_timer(1.5, self.execute_sweep_pass)
        self.get_logger().info('Demo 06: Swarm Area Coverage initialized across 3 parallel lanes.')
        self.execute_sweep_pass()

    def execute_sweep_pass(self):
        target_x = self.sweep_x[self.pass_idx % 2]
        now = self.get_clock().now().to_msg()

        for d_id, pub in self.pubs.items():
            p = PoseStamped()
            p.header.stamp = now
            p.header.frame_id = 'world'
            p.pose.position.x = target_x
            p.pose.position.y = self.lane_y[d_id]
            p.pose.position.z = self.sweep_alt
            p.pose.orientation.w = 1.0
            pub.publish(p)

        self.get_logger().info(
            f'>>> Sweep Pass [{self.pass_idx + 1}]: Target X={target_x:+.1f}m | '
            f'Parallel Lanes: drone_1 (+2.0m), drone_0 (0.0m), drone_2 (-2.0m)'
        )
        self.pass_idx += 1

def main(args=None):
    rclpy.init(args=args)
    node = Demo06SwarmAreaCoverage()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
