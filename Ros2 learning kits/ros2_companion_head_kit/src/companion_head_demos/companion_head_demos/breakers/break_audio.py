#!/usr/bin/env python3
"""
break_audio.py - Audio Failure Injection

LEARNING OBJECTIVES:
====================
1. Audio robustness testing
2. Noise handling
3. Dropout recovery

FAILURE MODES:
==============
- noise: Add random noise to speech recognition
- dropout: Randomly drop speech events
- wrong_tone: Publish wrong tone analysis
- delay: Add latency to audio events

USAGE:
======
    ros2 run companion_head_demos break_audio --ros-args -p mode:=dropout -p probability:=0.5
"""

import random
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class BreakAudio(Node):
    """Injects failures into audio stream."""

    def __init__(self):
        super().__init__('break_audio')

        # Parameters
        self.declare_parameter('mode', 'dropout')
        self.declare_parameter('probability', 0.3)

        self.mode = self.get_parameter('mode').value
        self.probability = self.get_parameter('probability').value

        # Subscribers
        self.wake_sub = self.create_subscription(
            Bool, '/audio/wake_word', self.wake_callback, 10)
        self.speech_sub = self.create_subscription(
            String, '/audio/speech', self.speech_callback, 10)
        self.tone_sub = self.create_subscription(
            String, '/audio/tone', self.tone_callback, 10)

        # Publishers
        self.wake_pub = self.create_publisher(Bool, '/audio/wake_word_broken', 10)
        self.speech_pub = self.create_publisher(String, '/audio/speech_broken', 10)
        self.tone_pub = self.create_publisher(String, '/audio/tone_broken', 10)

        self.get_logger().info('='*60)
        self.get_logger().info('BREAKER: Audio Failure Injection')
        self.get_logger().info('='*60)
        self.get_logger().info(f'  Mode: {self.mode}')
        self.get_logger().info(f'  Probability: {self.probability}')
        self.get_logger().info('')
        self.get_logger().info('Publishing broken audio to *_broken topics')

    def wake_callback(self, msg: Bool):
        """Process wake word with failures."""
        if self.mode == 'dropout' and random.random() < self.probability:
            self.get_logger().warn('[BREAK] Dropping wake word event!')
            return

        self.wake_pub.publish(msg)

    def speech_callback(self, msg: String):
        """Process speech with failures."""
        if self.mode == 'dropout' and random.random() < self.probability:
            self.get_logger().warn('[BREAK] Dropping speech event!')
            return

        if self.mode == 'noise':
            # Garble the text
            chars = list(msg.data)
            for i in range(len(chars)):
                if random.random() < self.probability:
                    chars[i] = random.choice('abcdefghijklmnopqrstuvwxyz ')
            msg.data = ''.join(chars)
            self.get_logger().warn(f'[BREAK] Garbled speech: {msg.data}')

        self.speech_pub.publish(msg)

    def tone_callback(self, msg: String):
        """Process tone with failures."""
        if self.mode == 'wrong_tone' and random.random() < self.probability:
            tones = ['happy', 'sad', 'angry', 'neutral', 'excited']
            wrong_tone = random.choice([t for t in tones if t != msg.data])
            self.get_logger().warn(f'[BREAK] Wrong tone: {msg.data} -> {wrong_tone}')
            msg.data = wrong_tone

        self.tone_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = BreakAudio()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
