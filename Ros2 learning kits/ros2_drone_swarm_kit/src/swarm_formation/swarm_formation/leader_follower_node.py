#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped

class LeaderFollowerNode(Node):
    """
    Subscribes to Leader Odometry and commands Follower target poses with fixed geometric offsets.
    """
    def __init__(self):
        super().__init__('leader_follower_node')
        self.declare_parameter('follower_id', 'drone_1')
        self.declare_parameter('offset_x', -1.0)
        self.declare_parameter('offset_y', 1.0)
        self.declare_parameter('offset_z', 0.0)

        self.follower_id = self.get_parameter('follower_id').value
        self.offset_x = float(self.get_parameter('offset_x').value)
        self.offset_y = float(self.get_parameter('offset_y').value)
        self.offset_z = float(self.get_parameter('offset_z').value)

        self.leader_sub = self.create_subscription(
            Odometry,
            '/drone_0/odom',
            self.leader_odom_cb,
            10
        )
        self.target_pub = self.create_publisher(
            PoseStamped,
            f'/{self.follower_id}/target_pose',
            10
        )
        self.get_logger().info(f'[{self.follower_id}] Tracking leader with offset ({self.offset_x}, {self.offset_y}, {self.offset_z}).')

    def leader_odom_cb(self, msg: Odometry):
        lx = msg.pose.pose.position.x
        ly = msg.pose.pose.position.y
        lz = msg.pose.pose.position.z

        target = PoseStamped()
        target.header.stamp = self.get_clock().now().to_msg()
        target.header.frame_id = 'world'
        target.pose.position.x = lx + self.offset_x
        target.pose.position.y = ly + self.offset_y
        target.pose.position.z = lz + self.offset_z
        self.target_pub.publish(target)

def main(args=None):
    rclpy.init(args=args)
    node = LeaderFollowerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
