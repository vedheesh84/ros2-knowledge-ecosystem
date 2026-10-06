#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry

class Demo02MultiDroneNamespacing(Node):
    """
    Demo 02: Multi-Drone Namespacing & Topic Isolation.
    Demonstrates independent simultaneous trajectory dispatch across
    isolated namespaces (/drone_0, /drone_1, /drone_2).
    """
    def __init__(self):
        super().__init__('demo_02_multi_drone_namespacing')
        
        self.drones = ['drone_0', 'drone_1', 'drone_2']
        self.targets = {
            'drone_0': (1.0, 0.0, 1.5),
            'drone_1': (0.0, 1.5, 1.8),
            'drone_2': (-1.0, -1.5, 1.2),
        }

        self.pubs = {}
        self.subs = {}
        self.positions = {}

        for d in self.drones:
            self.pubs[d] = self.create_publisher(PoseStamped, f'/{d}/target_pose', 10)
            self.positions[d] = [0.0, 0.0, 0.0]
            # Create closure for each drone subscription
            self.subs[d] = self.create_subscription(
                Odometry,
                f'/{d}/odom',
                lambda msg, drone_id=d: self.odom_cb(msg, drone_id),
                10
            )

        self.step = 0
        self.timer = self.create_timer(1.5, self.dispatch_commands)
        self.get_logger().info('Demo 02: Multi-Drone Namespacing initialized. Managing 3 isolated namespaces.')

    def odom_cb(self, msg: Odometry, drone_id: str):
        self.positions[drone_id] = [
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z,
        ]

    def dispatch_commands(self):
        now = self.get_clock().now().to_msg()
        self.get_logger().info(f'--- Dispatch Cycle {self.step} ---')

        for d in self.drones:
            tx, ty, tz = self.targets[d]
            # Alternate slightly after step 2 to demonstrate dynamic isolation
            if self.step >= 3:
                tx += 0.5
            msg = PoseStamped()
            msg.header.stamp = now
            msg.header.frame_id = 'world'
            msg.pose.position.x = float(tx)
            msg.pose.position.y = float(ty)
            msg.pose.position.z = float(tz)
            msg.pose.orientation.w = 1.0
            self.pubs[d].publish(msg)

            curr = self.positions[d]
            self.get_logger().info(
                f'[{d}] Commanded: ({tx:.1f}, {ty:.1f}, {tz:.1f}) | '
                f'Telemetry: ({curr[0]:.2f}, {curr[1]:.2f}, {curr[2]:.2f})'
            )

        self.step += 1

def main(args=None):
    rclpy.init(args=args)
    node = Demo02MultiDroneNamespacing()
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
