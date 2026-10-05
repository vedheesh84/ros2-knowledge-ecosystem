#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped, TransformStamped
from nav_msgs.msg import Odometry
import tf2_ros
import math

class DroneFlightController(Node):
    """
    Flight dynamics simulator and position tracker for an individual drone agent.
    """
    def __init__(self):
        super().__init__('flight_controller')
        self.declare_parameter('drone_id', 'drone_0')
        self.declare_parameter('initial_x', 0.0)
        self.declare_parameter('initial_y', 0.0)
        self.declare_parameter('initial_z', 0.0)

        self.drone_id = self.get_parameter('drone_id').value
        self.pos_x = float(self.get_parameter('initial_x').value)
        self.pos_y = float(self.get_parameter('initial_y').value)
        self.pos_z = float(self.get_parameter('initial_z').value)
        
        self.target_x = self.pos_x
        self.target_y = self.pos_y
        self.target_z = self.pos_z

        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.target_sub = self.create_subscription(PoseStamped, 'target_pose', self.target_cb, 10)
        self.cmd_vel_sub = self.create_subscription(Twist, 'cmd_vel', self.cmd_vel_cb, 10)
        
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        self.timer = self.create_timer(0.02, self.update_physics) # 50 Hz loop
        self.get_logger().info(f'[{self.drone_id}] Flight Controller online at initial pose ({self.pos_x}, {self.pos_y}, {self.pos_z}).')

    def target_cb(self, msg: PoseStamped):
        self.target_x = msg.pose.position.x
        self.target_y = msg.pose.position.y
        self.target_z = msg.pose.position.z

    def cmd_vel_cb(self, msg: Twist):
        self.target_x += msg.linear.x * 0.05
        self.target_y += msg.linear.y * 0.05
        self.target_z += msg.linear.z * 0.05

    def update_physics(self):
        # 1st-order position tracking dynamics with velocity saturation
        max_vel = 1.2 # m/s
        dt = 0.02
        
        err_x = self.target_x - self.pos_x
        err_y = self.target_y - self.pos_y
        err_z = self.target_z - self.pos_z
        
        vx = max(-max_vel, min(max_vel, 2.0 * err_x))
        vy = max(-max_vel, min(max_vel, 2.0 * err_y))
        vz = max(-max_vel, min(max_vel, 2.0 * err_z))
        
        self.pos_x += vx * dt
        self.pos_y += vy * dt
        self.pos_z += vz * dt

        # Publish Odometry
        odom = Odometry()
        odom.header.stamp = self.get_clock().now().to_msg()
        odom.header.frame_id = 'world'
        odom.child_frame_id = f'{self.drone_id}/base_link'
        odom.pose.pose.position.x = self.pos_x
        odom.pose.pose.position.y = self.pos_y
        odom.pose.pose.position.z = self.pos_z
        odom.twist.twist.linear.x = vx
        odom.twist.twist.linear.y = vy
        odom.twist.twist.linear.z = vz
        self.odom_pub.publish(odom)

        # Broadcast TF
        t = TransformStamped()
        t.header.stamp = odom.header.stamp
        t.header.frame_id = 'world'
        t.child_frame_id = f'{self.drone_id}/base_link'
        t.transform.translation.x = self.pos_x
        t.transform.translation.y = self.pos_y
        t.transform.translation.z = self.pos_z
        t.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = DroneFlightController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
