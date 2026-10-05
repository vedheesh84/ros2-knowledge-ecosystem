#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class BreakJointLimits(Node):
    """Breaker: Commands joints beyond physical servo bounds to test safety clamping."""
    def __init__(self):
        super().__init__('break_joint_limits')
        self.pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.timer = self.create_timer(2.0, self.send_illegal_joint_angle)
        self.get_logger().warn('BREAKER: Sending illegal joint angle (joint_2 = 4.0 rad).')

    def send_illegal_joint_angle(self):
        traj = JointTrajectory()
        traj.joint_names = ['joint_2']
        pt = JointTrajectoryPoint()
        pt.positions = [4.0]  # Beyond +/- 1.57 limit!
        pt.time_from_start.sec = 1
        traj.points.append(pt)
        self.pub.publish(traj)

def main(args=None):
    rclpy.init(args=args)
    node = BreakJointLimits()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
