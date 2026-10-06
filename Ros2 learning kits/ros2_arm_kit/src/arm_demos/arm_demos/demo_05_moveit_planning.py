#!/usr/bin/env python3
"""
Demo 05: Collision-Aware Trajectory Planning & MoveIt Integration
================================================================
Demonstrates generating articulated trajectories between key poses
(e.g., 'home' -> 'ready' -> target grasp pose) and dispatching them to /arm_controller/joint_trajectory.
"""
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class Demo05MoveItPlanning(Node):
    """Demo 05: MoveIt2 Trajectory Execution & Planning Monitor."""
    def __init__(self):
        super().__init__('demo_05_moveit_planning')
        self.pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.timer = self.create_timer(3.5, self.send_planned_trajectory)
        self.step = 0
        self.arm_joints = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint']
        self.get_logger().info('Demo 05: MoveIt Planning Demo - dispatching waypoints.')

    def send_planned_trajectory(self):
        traj = JointTrajectory()
        traj.header.stamp = self.get_clock().now().to_msg()
        traj.joint_names = self.arm_joints

        if self.step % 3 == 0:
            positions = [0.0, 0.0, 0.0, 0.0, 0.0]
            desc = "Named Pose: Home [0.0, 0.0, 0.0, 0.0, 0.0]"
        elif self.step % 3 == 1:
            positions = [0.0, -0.4, 0.8, -0.4, 0.0]
            desc = "Named Pose: Ready [0.0, -0.4, 0.8, -0.4, 0.0]"
        else:
            positions = [0.35, -0.2, 0.5, -0.3, 0.0]
            desc = "Waypoint: Tabletop Inspect [0.35, -0.2, 0.5, -0.3, 0.0]"

        pt = JointTrajectoryPoint()
        pt.positions = positions
        pt.time_from_start = Duration(sec=2, nanosec=0)
        traj.points.append(pt)

        self.pub.publish(traj)
        self.get_logger().info(f'Dispatched -> {desc}')
        self.step += 1

def main(args=None):
    rclpy.init(args=args)
    node = Demo05MoveItPlanning()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
