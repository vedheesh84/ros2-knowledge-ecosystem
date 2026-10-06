#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from nav_msgs.msg import Odometry
import math

class Demo04DynamicFormation(Node):
    """
    Demo 04: Dynamically Switching Swarm Formations.
    Cycles through V_SHAPE -> LINE -> CIRCLE formations via /swarm/formation_mode
    and monitors real-time swarm geometric morphing.
    """
    def __init__(self):
        super().__init__('demo_04_dynamic_formation')
        self.pub = self.create_publisher(String, '/swarm/formation_mode', 10)
        self.modes = ['V_SHAPE', 'LINE', 'CIRCLE']
        self.idx = 0

        self.positions = {
            'drone_0': [0.0, 0.0, 0.0],
            'drone_1': [0.0, 0.0, 0.0],
            'drone_2': [0.0, 0.0, 0.0],
        }

        self.subs = [
            self.create_subscription(Odometry, f'/{d}/odom', lambda m, did=d: self.odom_cb(m, did), 10)
            for d in ['drone_0', 'drone_1', 'drone_2']
        ]

        self.timer = self.create_timer(4.0, self.cycle_mode)
        self.get_logger().info('Demo 04: Cycling swarm formation modes (V_SHAPE -> LINE -> CIRCLE).')

    def odom_cb(self, msg: Odometry, drone_id: str):
        self.positions[drone_id] = [
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z,
        ]

    def cycle_mode(self):
        mode = self.modes[self.idx % len(self.modes)]
        msg = String()
        msg.data = mode
        self.pub.publish(msg)

        # Calculate swarm centroid
        cx = sum(p[0] for p in self.positions.values()) / 3.0
        cy = sum(p[1] for p in self.positions.values()) / 3.0
        cz = sum(p[2] for p in self.positions.values()) / 3.0

        self.get_logger().info(
            f'>>> Swarm Formation Commanded: [{mode}] | Centroid: ({cx:.2f}, {cy:.2f}, {cz:.2f})'
        )
        self.idx += 1

def main(args=None):
    rclpy.init(args=args)
    node = Demo04DynamicFormation()
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
