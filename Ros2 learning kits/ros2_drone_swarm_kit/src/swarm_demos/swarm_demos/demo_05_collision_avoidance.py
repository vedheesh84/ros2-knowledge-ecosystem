#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
import math

class Demo05CollisionAvoidance(Node):
    """
    Demo 05: Decentralized Artificial Potential Field Collision Avoidance.
    Drones execute crossing trajectories while computing inter-agent repulsive forces
    F_rep to maintain a safety distance d_safe and avoid mid-air collision.
    """
    def __init__(self):
        super().__init__('demo_05_collision_avoidance')

        self.pub_1 = self.create_publisher(PoseStamped, '/drone_1/target_pose', 10)
        self.pub_2 = self.create_publisher(PoseStamped, '/drone_2/target_pose', 10)

        self.sub_1 = self.create_subscription(Odometry, '/drone_1/odom', lambda m: self.odom_cb(m, 1), 10)
        self.sub_2 = self.create_subscription(Odometry, '/drone_2/odom', lambda m: self.odom_cb(m, 2), 10)

        # Positions [x, y, z]
        self.p1 = [-2.0, 0.0, 1.5]
        self.p2 = [2.0, 0.0, 1.5]

        # Target goals (crossing paths)
        self.goal1 = [2.0, 0.0, 1.5]
        self.goal2 = [-2.0, 0.0, 1.5]

        self.d_safe = 1.2 # Safety threshold (meters)
        self.k_att = 0.5
        self.k_rep = 1.0

        self.timer = self.create_timer(0.1, self.apf_step) # 10 Hz
        self.get_logger().info('Demo 05: Artificial Potential Field collision avoidance active.')

    def odom_cb(self, msg: Odometry, drone_idx: int):
        p = [msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z]
        if drone_idx == 1:
            self.p1 = p
        else:
            self.p2 = p

    def apf_step(self):
        now = self.get_clock().now().to_msg()

        # Inter-agent distance
        dx = self.p1[0] - self.p2[0]
        dy = self.p1[1] - self.p2[1]
        dist = math.hypot(dx, dy)
        if dist < 0.001:
            dist = 0.001

        # Repulsive deflection vector
        rep_x = 0.0
        rep_y = 0.0
        rep_active = False

        if dist < self.d_safe:
            rep_active = True
            # Orthogonal lateral deflection to smoothly bypass
            mag = self.k_rep * (1.0 / dist - 1.0 / self.d_safe) / (dist * dist)
            # Deflect Drone 1 into +Y, Drone 2 into -Y
            rep_x = 0.0
            rep_y = min(1.0, mag * 0.5)

        # Compute next target pose for Drone 1
        t1 = PoseStamped()
        t1.header.stamp = now
        t1.header.frame_id = 'world'
        t1.pose.position.x = self.p1[0] + self.k_att * (self.goal1[0] - self.p1[0]) * 0.1
        t1.pose.position.y = self.p1[1] + (self.k_att * (self.goal1[1] - self.p1[1]) + rep_y) * 0.1
        t1.pose.position.z = 1.5
        t1.pose.orientation.w = 1.0
        self.pub_1.publish(t1)

        # Compute next target pose for Drone 2
        t2 = PoseStamped()
        t2.header.stamp = now
        t2.header.frame_id = 'world'
        t2.pose.position.x = self.p2[0] + self.k_att * (self.goal2[0] - self.p2[0]) * 0.1
        t2.pose.position.y = self.p2[1] + (self.k_att * (self.goal2[1] - self.p2[1]) - rep_y) * 0.1
        t2.pose.position.z = 1.5
        t2.pose.orientation.w = 1.0
        self.pub_2.publish(t2)

        if rep_active:
            self.get_logger().warn(
                f'APF Repulsion Active! Dist: {dist:.2f}m (< {self.d_safe}m) | Lateral deflection: {rep_y:.2f}'
            )

def main(args=None):
    rclpy.init(args=args)
    node = Demo05CollisionAvoidance()
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
