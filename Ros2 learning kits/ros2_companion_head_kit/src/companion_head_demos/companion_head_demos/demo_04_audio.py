#!/usr/bin/env python3
"""
Demo 04: Audio Processing (Simulated)

LEARNING OBJECTIVES:
====================
1. Wake-word detection pattern
2. Speech-to-text concepts
3. Tone analysis

WHAT THIS DEMO DOES:
====================
1. Show simulated audio processing
2. Demonstrate wake-word → speech → response flow
3. Display tone analysis

NOTE: This uses simulated audio, not real microphone input.

TRY THIS:
=========
- Trigger wake word simulation
- Send different speech inputs
- See tone analysis results

COMMANDS:
=========
    # Run this demo
    ros2 run companion_head_demos demo_04_audio

    # Simulate wake word
    ros2 topic pub --once /audio/simulate std_msgs/String "data: wake"

    # Simulate speech (after wake word)
    ros2 topic pub --once /audio/simulate std_msgs/String "data: hello"
    ros2 topic pub --once /audio/simulate std_msgs/String "data: I am sad"

PREREQUISITE:
=============
    ros2 run companion_head_sensors audio_simulator
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class AudioDemo(Node):
    """Demo that shows audio processing concepts."""

    def __init__(self):
        super().__init__('demo_04_audio')

        self.wake_count = 0
        self.speech_count = 0

        # Subscribers
        self.wake_sub = self.create_subscription(
            Bool, '/audio/wake_word', self.wake_callback, 10)
        self.speech_sub = self.create_subscription(
            String, '/audio/speech', self.speech_callback, 10)
        self.tone_sub = self.create_subscription(
            String, '/audio/tone', self.tone_callback, 10)

        # Publisher for simulation
        self.sim_pub = self.create_publisher(String, '/audio/simulate', 10)

        self.get_logger().info('='*60)
        self.get_logger().info('DEMO 04: AUDIO PROCESSING (SIMULATED)')
        self.get_logger().info('='*60)
        self.get_logger().info('')
        self.get_logger().info('Make sure audio_simulator is running:')
        self.get_logger().info('  ros2 run companion_head_sensors audio_simulator')
        self.get_logger().info('')
        self.get_logger().info('Simulate audio by publishing to /audio/simulate:')
        self.get_logger().info('  Step 1: ros2 topic pub --once /audio/simulate std_msgs/String "data: wake"')
        self.get_logger().info('  Step 2: ros2 topic pub --once /audio/simulate std_msgs/String "data: hello"')
        self.get_logger().info('')
        self.get_logger().info('Waiting for audio events...')
        self.get_logger().info('')

        # Run automatic demo sequence
        self.create_timer(5.0, self.run_demo_sequence)
        self.demo_step = 0

    def run_demo_sequence(self):
        """Run automatic demo sequence."""
        demo_steps = [
            'wake',
            'hello how are you',
            'wake',
            'I feel sad today',
            'wake',
            'tell me a joke',
        ]

        if self.demo_step < len(demo_steps):
            msg = String()
            msg.data = demo_steps[self.demo_step]
            self.sim_pub.publish(msg)
            self.get_logger().info(f'[AUTO] Simulating: "{demo_steps[self.demo_step]}"')
            self.demo_step += 1

    def wake_callback(self, msg: Bool):
        """Handle wake word detection."""
        if msg.data:
            self.wake_count += 1
            self.get_logger().info(f'[WAKE WORD] Detected! (count: {self.wake_count})')
            self.get_logger().info('  Robot is now listening for speech...')

    def speech_callback(self, msg: String):
        """Handle recognized speech."""
        self.speech_count += 1
        self.get_logger().info(f'[SPEECH] Recognized: "{msg.data}" (count: {self.speech_count})')

    def tone_callback(self, msg: String):
        """Handle tone analysis."""
        self.get_logger().info(f'[TONE] Detected tone: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = AudioDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
