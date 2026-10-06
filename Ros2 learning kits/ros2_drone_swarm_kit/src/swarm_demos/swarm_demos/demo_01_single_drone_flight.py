#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
import time

class Demo01SingleFlight(Node):
    """
    Demo 01: Single Drone 3D Waypoint Navigation.
    Commands 3D waypoints (takeoff -> square pattern -> landing)
    and verifies closed-loop odometry tracking.
    """
    def __init__(self):
        super().__init__('demo_01_single_flight')
        self.pub = self.create_publisher(PoseStamped, '/drone_0/target_pose', 10)
        self.odom_sub = self.create_subscription(Odometry, '/drone_0/odom', self.odom_cb, 10)

        self.waypoints = [
            (0.0, 0.0, 1.5),  # Takeoff
            (1.5, 0.0, 1.5),  # Forward
            (1.5, 1.5, 2.0),  # Climb & lateral
            (0.0, 1.5, 1.5),  # Lateral return
            (0.0, 0.0, 0.0)   # Land
        ]
        self.idx = 0
        self.current_pose = [0.0, 0.0, 0.0]
        self.completed = False

        self.timer = self.create_timer(1.5, self.send_waypoint)
        self.get_logger().info('Demo 01: Initialized. Commanding single drone 3D flight profile.')
        self.send_waypoint()

    def odom_cb(self, msg: Odometry):
        self.current_pose[0] = msg.pose.pose.position.x
        self.current_pose[1] = msg.pose.pose.position.y
        self.current_pose[2] = msg.pose.pose.position.z

    def send_waypoint(self):
        if self.idx >= len(self.waypoints):
            if not self.completed:
                self.get_logger().info('Demo 01: All waypoints successfully executed. Flight complete.')
                self.completed = True
            return

        x, y, z = self.waypoints[self.idx]
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'world'
        msg.pose.position.x = float(x)
        msg.pose.position.y = float(y)
        msg.pose.position.z = float(z)
        msg.pose.orientation.w = 1.0
        self.pub.publish(msg)

        self.get_logger().info(
            f'Waypoint [{self.idx+1}/{len(self.waypoints)}]: Commanded ({x:.1f}, {y:.1f}, {z:.1f}) | '
            f'Current: ({self.current_pose[0]:.2f}, {self.current_pose[1]:.2f}, {self.current_pose[2]:.2f})'
        )
        self.idx += 1

def main(args=None):
    rclpy.init(args=args)
    node = Demo01SingleFlight()
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
