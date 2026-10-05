#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory
import time

class MockArmHardware(Node):
    """
    Mock hardware bridge simulating physical servos on PC.
    Subscribes to joint commands and publishes current positions on /joint_states.
    """
    def __init__(self):
        super().__init__('mock_arm_hardware')
        self.joint_names = [
            'joint_1', 'joint_2', 'joint_3', 'joint_4',
            'gripper_base_joint', 'left_gear_joint',
            'left_finger_joint', 'right_gear_joint',
            'right_finger_joint', 'left_joint', 'right_joint'
        ]
        self.current_positions = {name: 0.0 for name in self.joint_names}
        self.target_positions = {name: 0.0 for name in self.joint_names}
        
        self.js_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.cmd_sub = self.create_subscription(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            self.trajectory_callback,
            10
        )
        
        # 50 Hz simulation loop
        self.timer = self.create_timer(0.02, self.update_loop)
        self.get_logger().info('Mock Arm Hardware Bridge running (50 Hz update).')

    def trajectory_callback(self, msg: JointTrajectory):
        if not msg.points:
            return
        last_pt = msg.points[-1]
        for name, pos in zip(msg.joint_names, last_pt.positions):
            if name in self.target_positions:
                self.target_positions[name] = pos
                # Link mimic joints if controlling gripper
                if name == 'left_gear_joint':
                    self.target_positions['left_finger_joint'] = pos
                    self.target_positions['right_gear_joint'] = -pos
                    self.target_positions['right_finger_joint'] = pos
                    self.target_positions['left_joint'] = -pos
                    self.target_positions['right_joint'] = pos

    def update_loop(self):
        # Smooth interpolation to target positions
        alpha = 0.1
        for name in self.joint_names:
            diff = self.target_positions[name] - self.current_positions[name]
            self.current_positions[name] += alpha * diff
            
        js_msg = JointState()
        js_msg.header.stamp = self.get_clock().now().to_msg()
        js_msg.name = self.joint_names
        js_msg.position = [self.current_positions[name] for name in self.joint_names]
        js_msg.velocity = [0.0] * len(self.joint_names)
        js_msg.effort = [0.0] * len(self.joint_names)
        self.js_pub.publish(js_msg)

def main(args=None):
    rclpy.init(args=args)
    node = MockArmHardware()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
