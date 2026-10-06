#!/usr/bin/env python3
"""
Breaker: Trajectory Timing & Excessive Acceleration Fault Injection
===================================================================
Injects impossible dynamic demands by commanding large joint excursions with
nanosecond execution horizons, testing controller safety rejection and jitter.
"""
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class BreakTrajectoryTiming(Node):
    def __init__(self):
        super().__init__('break_trajectory_timing')
        self.pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.timer = self.create_timer(2.0, self.send_excessive_acceleration_trajectory)
        self.arm_joints = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint']
        self.get_logger().warn('BREAKER: Injected Trajectory Timing fault - 180-deg swing in 1 ms.')

    def send_excessive_acceleration_trajectory(self):
        traj = JointTrajectory()
        traj.header.stamp = self.get_clock().now().to_msg()
        traj.joint_names = self.arm_joints

        pt = JointTrajectoryPoint()
        # Request full 3.14 rad excursion
        pt.positions = [3.14, 1.57, -1.57, 1.57, 0.0]
        # Impossible 1 millisecond execution horizon
        pt.time_from_start = Duration(sec=0, nanosec=1000000)
        traj.points.append(pt)

        self.pub.publish(traj)
        self.get_logger().info('Dispatched impossible high-acceleration trajectory to controller.')

def main(args=None):
    rclpy.init(args=args)
    node = BreakTrajectoryTiming()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
