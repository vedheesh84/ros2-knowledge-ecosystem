#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import math

class FormationManagerNode(Node):
    """
    Coordinates global swarm formation patterns (V-Formation, Line, Circle).
    """
    def __init__(self):
        super().__init__('formation_manager')
        self.pub_0 = self.create_publisher(PoseStamped, '/drone_0/target_pose', 10)
        self.pub_1 = self.create_publisher(PoseStamped, '/drone_1/target_pose', 10)
        self.pub_2 = self.create_publisher(PoseStamped, '/drone_2/target_pose', 10)
        
        self.mode_sub = self.create_subscription(String, '/swarm/formation_mode', self.mode_cb, 10)
        self.current_pattern = 'V_SHAPE'
        self.center_x = 0.0
        self.center_y = 0.0
        self.center_z = 1.5
        
        self.timer = self.create_timer(0.1, self.publish_formation) # 10 Hz
        self.get_logger().info('Formation Manager active. Default formation: V_SHAPE.')

    def mode_cb(self, msg: String):
        self.current_pattern = msg.data.upper()
        self.get_logger().info(f'Switching Swarm Formation to: {self.current_pattern}')

    def publish_formation(self):
        t0 = PoseStamped()
        t1 = PoseStamped()
        t2 = PoseStamped()
        now = self.get_clock().now().to_msg()
        for t in [t0, t1, t2]:
            t.header.stamp = now
            t.header.frame_id = 'world'

        if self.current_pattern == 'LINE':
            t0.pose.position.x, t0.pose.position.y, t0.pose.position.z = 0.0, 0.0, self.center_z
            t1.pose.position.x, t1.pose.position.y, t1.pose.position.z = 0.0, 1.2, self.center_z
            t2.pose.position.x, t2.pose.position.y, t2.pose.position.z = 0.0, -1.2, self.center_z
        elif self.current_pattern == 'CIRCLE':
            t0.pose.position.x, t0.pose.position.y, t0.pose.position.z = 1.2, 0.0, self.center_z
            t1.pose.position.x, t1.pose.position.y, t1.pose.position.z = -0.6, 1.0, self.center_z
            t2.pose.position.x, t2.pose.position.y, t2.pose.position.z = -0.6, -1.0, self.center_z
        else: # V_SHAPE
            t0.pose.position.x, t0.pose.position.y, t0.pose.position.z = 1.0, 0.0, self.center_z
            t1.pose.position.x, t1.pose.position.y, t1.pose.position.z = 0.0, 1.0, self.center_z
            t2.pose.position.x, t2.pose.position.y, t2.pose.position.z = 0.0, -1.0, self.center_z

        self.pub_0.publish(t0)
        self.pub_1.publish(t1)
        self.pub_2.publish(t2)

def main(args=None):
    rclpy.init(args=args)
    node = FormationManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
