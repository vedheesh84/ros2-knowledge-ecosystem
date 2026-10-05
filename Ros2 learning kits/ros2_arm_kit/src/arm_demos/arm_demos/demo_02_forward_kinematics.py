#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from arm_kinematics.forward_kinematics import ForwardKinematics

class Demo02ForwardKinematics(Node):
    """Demo 02: Real-time Forward Kinematics End-Effector Tracking."""
    def __init__(self):
        super().__init__('demo_02_forward_kinematics')
        self.fk = ForwardKinematics()
        self.sub = self.create_subscription(JointState, '/joint_states', self.cb, 10)
        self.get_logger().info('Demo 02: Calculating Cartesian End-Effector Pose from /joint_states.')

    def cb(self, msg: JointState):
        name_map = dict(zip(msg.name, msg.position))
        q1 = name_map.get('joint_1', 0.0)
        q2 = name_map.get('joint_2', 0.0)
        q3 = name_map.get('joint_3', 0.0)
        q4 = name_map.get('joint_4', 0.0)
        x, y, z, pitch = self.fk.compute_fk(q1, q2, q3, q4)
        self.get_logger().info(f'Calculated End-Effector: X={x:.3f}m, Y={y:.3f}m, Z={z:.3f}m, Pitch={pitch:.2f}rad', throttle_duration_sec=1.0)

def main(args=None):
    rclpy.init(args=args)
    node = Demo02ForwardKinematics()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
