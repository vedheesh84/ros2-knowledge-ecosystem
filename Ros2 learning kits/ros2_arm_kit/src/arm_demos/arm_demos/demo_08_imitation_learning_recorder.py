#!/usr/bin/env python3
"""
Demo 08: Imitation Learning - Multimodal Demonstration Recorder
===============================================================
Records human-guided demonstrations (joint trajectories, velocities, gripper efforts, timestamps)
into structured JSON/HDF5 episodic demonstration datasets for Behavioral Cloning / Policy Learning.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import json
import time

class DemonstrationRecorderNode(Node):
    def __init__(self):
        super().__init__('demo_recorder_node')
        self.declare_parameter('output_file', 'demonstration_episode_01.json')
        self.output_file = self.get_parameter('output_file').value

        self.sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.state_callback,
            50
        )
        self.episode_data = {
            'metadata': {'recorded_at': time.time(), 'joint_names': []},
            'trajectory': []
        }
        self.is_recording = True
        self.get_logger().info(f'Demonstration Recorder active. Logging to [{self.output_file}]...')

    def state_callback(self, msg: JointState):
        if not self.is_recording:
            return
        if not self.episode_data['metadata']['joint_names']:
            self.episode_data['metadata']['joint_names'] = list(msg.name)

        frame = {
            'timestamp': self.get_clock().now().nanoseconds / 1e9,
            'positions': list(msg.position),
            'velocities': list(msg.velocity) if msg.velocity else [],
            'efforts': list(msg.effort) if msg.effort else []
        }
        self.episode_data['trajectory'].append(frame)

    def save_and_close(self):
        self.is_recording = False
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.episode_data, f, indent=2)
        self.get_logger().info(f'Saved {len(self.episode_data["trajectory"])} frames to {self.output_file}.')

def main(args=None):
    rclpy.init(args=args)
    node = DemonstrationRecorderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.save_and_close()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
