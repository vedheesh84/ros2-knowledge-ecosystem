#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
import math

class LeaderFollowerNode(Node):
    """
    Subscribes to Leader Odometry and commands Follower target poses with
    heading-aligned geometric coordinate offsets (SE(3) relative formation law).
    """
    def __init__(self):
        super().__init__('leader_follower_node')
        self.declare_parameter('leader_id', 'drone_0')
        self.declare_parameter('follower_id', 'drone_1')
        self.declare_parameter('offset_x', -1.0)
        self.declare_parameter('offset_y', 1.0)
        self.declare_parameter('offset_z', 0.0)

        self.leader_id = self.get_parameter('leader_id').value
        self.follower_id = self.get_parameter('follower_id').value
        self.offset_x = float(self.get_parameter('offset_x').value)
        self.offset_y = float(self.get_parameter('offset_y').value)
        self.offset_z = float(self.get_parameter('offset_z').value)

        self.leader_sub = self.create_subscription(
            Odometry,
            f'/{self.leader_id}/odom',
            self.leader_odom_cb,
            10
        )
        self.target_pub = self.create_publisher(
            PoseStamped,
            f'/{self.follower_id}/target_pose',
            10
        )
        self.get_logger().info(
            f'[{self.follower_id}] Tracking leader [{self.leader_id}] with body-frame offset ({self.offset_x}, {self.offset_y}, {self.offset_z}).'
        )

    def leader_odom_cb(self, msg: Odometry):
        lx = msg.pose.pose.position.x
        ly = msg.pose.pose.position.y
        lz = msg.pose.pose.position.z

        # Extract yaw angle from leader orientation quaternion
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        # Rotate offset vector by leader yaw R(psi)
        dx = math.cos(yaw) * self.offset_x - math.sin(yaw) * self.offset_y
        dy = math.sin(yaw) * self.offset_x + math.cos(yaw) * self.offset_y
        dz = self.offset_z

        target = PoseStamped()
        target.header.stamp = self.get_clock().now().to_msg()
        target.header.frame_id = 'world'
        target.pose.position.x = lx + dx
        target.pose.position.y = ly + dy
        target.pose.position.z = max(0.2, lz + dz)
        target.pose.orientation = q # Match leader heading

        self.target_pub.publish(target)

def main(args=None):
    rclpy.init(args=args)
    node = LeaderFollowerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
