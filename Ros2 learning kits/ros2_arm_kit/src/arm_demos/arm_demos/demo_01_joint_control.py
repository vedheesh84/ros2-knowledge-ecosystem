#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import math

class Demo01JointControl(Node):
    """Demo 01: Direct Joint Angle Trajectory Control."""
    def __init__(self):
        super().__init__('demo_01_joint_control')
        self.pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.timer = self.create_timer(3.0, self.send_wave_trajectory)
        self.step = 0
        self.get_logger().info('Demo 01: Sending sinusoidal joint trajectories to arm.')

    def send_wave_trajectory(self):
        traj = JointTrajectory()
        traj.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint']
        pt = JointTrajectoryPoint()
        
        if self.step % 2 == 0:
            pt.positions = [0.5, -0.3, 0.6, -0.3, 0.0]
            self.get_logger().info('Pose A: [0.5, -0.3, 0.6, -0.3, 0.0]')
        else:
            pt.positions = [-0.5, 0.2, 0.4, 0.2, 0.0]
            self.get_logger().info('Pose B: [-0.5, 0.2, 0.4, 0.2, 0.0]')
            
        pt.time_from_start.sec = 2
        traj.points.append(pt)
        self.pub.publish(traj)
        self.step += 1

def main(args=None):
    rclpy.init(args=args)
    node = Demo01JointControl()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
