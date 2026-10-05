#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

class Demo01SingleFlight(Node):
    """Demo 01: Single Drone 3D Waypoint Navigation."""
    def __init__(self):
        super().__init__('demo_01_single_flight')
        self.pub = self.create_publisher(PoseStamped, '/drone_0/target_pose', 10)
        self.waypoints = [
            (0.0, 0.0, 1.5),
            (1.5, 0.0, 1.5),
            (1.5, 1.5, 2.0),
            (0.0, 1.5, 1.5),
            (0.0, 0.0, 0.0) # Land
        ]
        self.idx = 0
        self.timer = self.create_timer(3.5, self.send_waypoint)
        self.get_logger().info('Demo 01: Commanding single drone square flight pattern.')

    def send_waypoint(self):
        x, y, z = self.waypoints[self.idx % len(self.waypoints)]
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'world'
        msg.pose.position.x = float(x)
        msg.pose.position.y = float(y)
        msg.pose.position.z = float(z)
        self.pub.publish(msg)
        self.get_logger().info(f'Commanded Waypoint: ({x}, {y}, {z})')
        self.idx += 1

def main(args=None):
    rclpy.init(args=args)
    node = Demo01SingleFlight()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
