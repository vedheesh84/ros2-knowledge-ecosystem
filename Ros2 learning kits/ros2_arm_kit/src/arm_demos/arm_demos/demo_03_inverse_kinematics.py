#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from arm_kinematics.inverse_kinematics import InverseKinematics
from arm_kinematics.jacobian import ArmJacobian

class Demo03InverseKinematics(Node):
    """Demo 03: Cartesian Target Reaching via Analytical IK."""
    def __init__(self):
        super().__init__('demo_03_inverse_kinematics')
        self.ik = InverseKinematics()
        self.jac = ArmJacobian()
        self.pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.targets = [
            (0.18, 0.0, 0.12, -0.5),
            (0.15, 0.10, 0.15, -0.6),
            (0.15, -0.10, 0.15, -0.6),
            (0.20, 0.0, 0.08, -0.4)
        ]
        self.idx = 0
        self.timer = self.create_timer(3.0, self.reach_next_target)
        self.get_logger().info('Demo 03: Commanding Cartesian (X,Y,Z,Pitch) goals using Analytical IK.')

    def reach_next_target(self):
        tx, ty, tz, tp = self.targets[self.idx % len(self.targets)]
        sol = self.ik.solve(tx, ty, tz, target_pitch=tp)
        if sol:
            q1, q2, q3, q4 = sol
            manip = self.jac.manipulability_index(q2, q3, q4)
            self.get_logger().info(f'Target ({tx}, {ty}, {tz}) -> IK Solved! Joints: [{q1:.2f}, {q2:.2f}, {q3:.2f}, {q4:.2f}] | Manipulability: {manip:.4f}')
            
            traj = JointTrajectory()
            traj.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint']
            pt = JointTrajectoryPoint()
            pt.positions = [q1, q2, q3, q4, 0.0]
            pt.time_from_start.sec = 2
            traj.points.append(pt)
            self.pub.publish(traj)
        else:
            self.get_logger().warn(f'Target ({tx}, {ty}, {tz}) is UNREACHABLE!')
        self.idx += 1

def main(args=None):
    rclpy.init(args=args)
    node = Demo03InverseKinematics()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
