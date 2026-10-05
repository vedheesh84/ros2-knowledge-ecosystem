#!/usr/bin/env python3
"""
Demo 07: Leader-Follower Teleoperation & Remote Mirroring
=========================================================
Demonstrates real-time kinematic mirroring from a Leader arm (e.g. teleoperated/manual puppet)
to a Follower robotic arm over low-latency ROS2 DDS topic streaming with bilateral feedback.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class TeleoperationMirroringNode(Node):
    def __init__(self):
        super().__init__('teleop_mirroring_node')
        self.declare_parameter('leader_topic', '/leader/joint_states')
        self.declare_parameter('follower_cmd_topic', '/arm_controller/joint_trajectory')

        leader_topic = self.get_parameter('leader_topic').value
        follower_cmd_topic = self.get_parameter('follower_cmd_topic').value

        self.leader_sub = self.create_subscription(
            JointState,
            leader_topic,
            self.leader_callback,
            10
        )
        self.follower_pub = self.create_publisher(
            JointTrajectory,
            follower_cmd_topic,
            10
        )
        self.arm_joints = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint']
        self.get_logger().info('Teleoperation Mirroring Node Active.')
        self.get_logger().info(f'Mirroring from [{leader_topic}] to [{follower_cmd_topic}].')

    def leader_callback(self, msg: JointState):
        pos_dict = dict(zip(msg.name, msg.position))
        cmd = JointTrajectory()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.joint_names = self.arm_joints

        point = JointTrajectoryPoint()
        point.positions = [pos_dict.get(j, 0.0) for j in self.arm_joints]
        point.time_from_start = Duration(sec=0, nanosec=20000000) # 20ms execution horizon (50 Hz)
        cmd.points.append(point)

        self.follower_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = TeleoperationMirroringNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
