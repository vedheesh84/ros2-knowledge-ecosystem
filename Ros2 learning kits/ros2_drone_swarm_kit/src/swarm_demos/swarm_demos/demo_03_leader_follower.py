#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
import math

class Demo03LeaderFollower(Node):
    """
    Demo 03: Leader-Follower Swarm Formation Flight.
    Commands Leader (drone_0) along a dynamic trajectory while enforcing
    rigid geometric coordinate offsets for Follower 1 (drone_1) and Follower 2 (drone_2).
    """
    def __init__(self):
        super().__init__('demo_03_leader_follower')

        self.leader_pub = self.create_publisher(PoseStamped, '/drone_0/target_pose', 10)
        self.f1_pub = self.create_publisher(PoseStamped, '/drone_1/target_pose', 10)
        self.f2_pub = self.create_publisher(PoseStamped, '/drone_2/target_pose', 10)

        self.odom_subs = {
            'drone_0': self.create_subscription(Odometry, '/drone_0/odom', lambda m: self.odom_cb(m, 'drone_0'), 10),
            'drone_1': self.create_subscription(Odometry, '/drone_1/odom', lambda m: self.odom_cb(m, 'drone_1'), 10),
            'drone_2': self.create_subscription(Odometry, '/drone_2/odom', lambda m: self.odom_cb(m, 'drone_2'), 10),
        }

        self.positions = {
            'drone_0': [0.0, 0.0, 1.5],
            'drone_1': [-1.0, 1.0, 1.5],
            'drone_2': [-1.0, -1.0, 1.5],
        }

        # Follower relative offsets [dx, dy, dz] in body frame
        self.offset_1 = [-1.0, 1.0, 0.0]
        self.offset_2 = [-1.0, -1.0, 0.0]

        self.angle = 0.0
        self.timer = self.create_timer(0.2, self.control_loop) # 5 Hz loop
        self.get_logger().info('Demo 03: Leader-Follower formation flight active.')

    def odom_cb(self, msg: Odometry, drone_id: str):
        self.positions[drone_id] = [
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z,
        ]

    def control_loop(self):
        now = self.get_clock().now().to_msg()

        # Generate leader cruising path (e.g. circle with radius 1.5m at alt 1.8m)
        radius = 1.5
        lx = radius * math.cos(self.angle)
        ly = radius * math.sin(self.angle)
        lz = 1.8
        self.angle += 0.05

        # Leader Target Pose
        lp = PoseStamped()
        lp.header.stamp = now
        lp.header.frame_id = 'world'
        lp.pose.position.x = lx
        lp.pose.position.y = ly
        lp.pose.position.z = lz
        lp.pose.orientation.w = 1.0
        self.leader_pub.publish(lp)

        # Followers track leader with body-frame offsets
        # Desired yaw matches tangent of motion
        yaw = self.angle + math.pi / 2.0

        for pub, offset in [(self.f1_pub, self.offset_1), (self.f2_pub, self.offset_2)]:
            dx = math.cos(yaw) * offset[0] - math.sin(yaw) * offset[1]
            dy = math.sin(yaw) * offset[0] + math.cos(yaw) * offset[1]
            fp = PoseStamped()
            fp.header.stamp = now
            fp.header.frame_id = 'world'
            fp.pose.position.x = lx + dx
            fp.pose.position.y = ly + dy
            fp.pose.position.z = lz + offset[2]
            fp.pose.orientation.w = 1.0
            pub.publish(fp)

        # Log formation metrics periodically
        if int(self.angle * 10) % 20 == 0:
            d1_dist = math.hypot(self.positions['drone_1'][0] - self.positions['drone_0'][0],
                                 self.positions['drone_1'][1] - self.positions['drone_0'][1])
            d2_dist = math.hypot(self.positions['drone_2'][0] - self.positions['drone_0'][0],
                                 self.positions['drone_2'][1] - self.positions['drone_0'][1])
            self.get_logger().info(
                f'Leader: ({lx:.2f}, {ly:.2f}) | '
                f'Follower 1 Dist: {d1_dist:.2f}m | Follower 2 Dist: {d2_dist:.2f}m'
            )

def main(args=None):
    rclpy.init(args=args)
    node = Demo03LeaderFollower()
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
