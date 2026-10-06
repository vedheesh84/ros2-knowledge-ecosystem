#!/usr/bin/env python3
"""
Demo 06: Multimodal Interaction

LEARNING OBJECTIVES:
====================
1. Combining vision and audio inputs
2. Attention management
3. Sensor fusion concepts

WHAT THIS DEMO DOES:
====================
1. Process both face detection and audio
2. Coordinate gaze and expressions
3. Show attention switching

TRY THIS:
=========
- Move in front of camera while speaking
- Watch gaze track you
- See expression respond to tone

PREREQUISITE:
=============
    Multiple nodes running:
    - face_detector
    - audio_simulator
    - mood_engine
    - expression_renderer
    - gaze_controller
"""

import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class MultimodalDemo(Node):
    """Demo that combines vision and audio."""

    def __init__(self):
        super().__init__('demo_06_multimodal')

        self.face_detected = False
        self.current_mood = 'neutral'
        self.is_listening = False

        # Subscribers
        self.faces_sub = self.create_subscription(
            String, '/faces/detections', self.faces_callback, 10)
        self.wake_sub = self.create_subscription(
            Bool, '/audio/wake_word', self.wake_callback, 10)
        self.speech_sub = self.create_subscription(
            String, '/audio/speech', self.speech_callback, 10)
        self.mood_sub = self.create_subscription(
            String, '/mood/state', self.mood_callback, 10)

        self.get_logger().info('='*60)
        self.get_logger().info('DEMO 06: MULTIMODAL INTERACTION')
        self.get_logger().info('='*60)
        self.get_logger().info('')
        self.get_logger().info('This demo combines vision + audio processing.')
        self.get_logger().info('')
        self.get_logger().info('Required nodes:')
        self.get_logger().info('  ros2 run companion_head_sensors face_detector')
        self.get_logger().info('  ros2 run companion_head_sensors audio_simulator')
        self.get_logger().info('  ros2 run companion_head_behaviors mood_engine')
        self.get_logger().info('  ros2 run companion_head_expression expression_renderer')
        self.get_logger().info('  ros2 run companion_head_control gaze_controller')
        self.get_logger().info('')
        self.get_logger().info('Watching multimodal inputs...')
        self.get_logger().info('')

        # Status timer
        self.create_timer(3.0, self.print_status)

    def faces_callback(self, msg: String):
        """Process face detection."""
        try:
            data = json.loads(msg.data)
            face_detected = data.get('count', 0) > 0

            if face_detected != self.face_detected:
                self.face_detected = face_detected
                status = 'DETECTED' if face_detected else 'LOST'
                self.get_logger().info(f'[VISION] Face {status}')
        except json.JSONDecodeError:
            pass

    def wake_callback(self, msg: Bool):
        """Process wake word."""
        if msg.data:
            self.is_listening = True
            self.get_logger().info('[AUDIO] Wake word detected - LISTENING')

    def speech_callback(self, msg: String):
        """Process speech."""
        self.is_listening = False
        self.get_logger().info(f'[AUDIO] Speech: "{msg.data}"')

    def mood_callback(self, msg: String):
        """Track mood."""
        try:
            data = json.loads(msg.data)
            mood = data.get('mood', 'neutral')
            if mood != self.current_mood:
                self.current_mood = mood
                self.get_logger().info(f'[MOOD] Changed to: {mood}')
        except json.JSONDecodeError:
            pass

    def print_status(self):
        """Print current multimodal state."""
        self.get_logger().info(
            f'[STATUS] Face: {"YES" if self.face_detected else "NO"} | '
            f'Listening: {"YES" if self.is_listening else "NO"} | '
            f'Mood: {self.current_mood}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = MultimodalDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
