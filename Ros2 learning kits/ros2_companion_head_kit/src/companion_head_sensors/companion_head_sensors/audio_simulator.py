#!/usr/bin/env python3
"""
audio_simulator.py - Simulated audio processing for Companion Head

LEARNING OBJECTIVES:
====================
1. Audio processing concepts (without real implementation)
2. Wake-word detection pattern
3. Speech-to-text simulation
4. Tone analysis concepts

NOTE: This is a SIMULATED audio processor for learning purposes.
It doesn't actually process real audio - it generates fake events
for testing the behavior system.

TOPICS:
=======
    Subscribes:
    - /audio/simulate (std_msgs/String): Simulated audio events

    Publishes:
    - /audio/wake_word (std_msgs/Bool): Wake word detected
    - /audio/speech (std_msgs/String): Recognized speech
    - /audio/tone (std_msgs/String): Detected tone (happy, sad, neutral)
"""

import random
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class AudioSimulator(Node):
    """
    Simulates audio processing for learning and testing.

    Accepts simulated audio events via /audio/simulate topic
    and publishes wake word, speech, and tone detections.

    In real implementation, this would:
    1. Subscribe to actual audio stream
    2. Run wake-word detection (e.g., Porcupine, Snowboy)
    3. Run STT (e.g., Vosk, Whisper)
    4. Analyze tone from audio features
    """

    def __init__(self):
        super().__init__('audio_simulator')

        # Parameters
        self.declare_parameter('wake_word', 'hey companion')
        self.declare_parameter('auto_events', True)
        self.declare_parameter('event_interval', 10.0)

        self.wake_word = self.get_parameter('wake_word').value
        self.auto_events = self.get_parameter('auto_events').value
        self.event_interval = self.get_parameter('event_interval').value

        # State
        self.is_listening = False

        # Simulated phrases
        self.phrases = [
            ("hello", "happy"),
            ("how are you", "neutral"),
            ("good morning", "happy"),
            ("I'm sad", "sad"),
            ("tell me a joke", "excited"),
            ("thank you", "happy"),
            ("goodbye", "neutral"),
            ("what time is it", "neutral"),
        ]

        # Subscriber for manual simulation
        self.sim_sub = self.create_subscription(
            String,
            '/audio/simulate',
            self.simulate_callback,
            10
        )

        # Publishers
        self.wake_pub = self.create_publisher(Bool, '/audio/wake_word', 10)
        self.speech_pub = self.create_publisher(String, '/audio/speech', 10)
        self.tone_pub = self.create_publisher(String, '/audio/tone', 10)

        # Auto event timer (if enabled)
        if self.auto_events:
            self.create_timer(self.event_interval, self.auto_event)

        self.get_logger().info('Audio Simulator initialized')
        self.get_logger().info(f'  Wake word: "{self.wake_word}"')
        self.get_logger().info(f'  Auto events: {self.auto_events}')
        self.get_logger().info('')
        self.get_logger().info('To simulate audio, publish to /audio/simulate:')
        self.get_logger().info('  ros2 topic pub --once /audio/simulate std_msgs/String "data: wake"')
        self.get_logger().info('  ros2 topic pub --once /audio/simulate std_msgs/String "data: hello"')

    def simulate_callback(self, msg: String):
        """Handle simulated audio events."""
        text = msg.data.lower().strip()

        if text == 'wake' or self.wake_word in text:
            # Wake word detected
            self.get_logger().info(f'[WAKE WORD] "{self.wake_word}" detected!')
            self.is_listening = True

            wake_msg = Bool()
            wake_msg.data = True
            self.wake_pub.publish(wake_msg)

        elif self.is_listening:
            # Process as speech
            self.get_logger().info(f'[SPEECH] Recognized: "{text}"')

            speech_msg = String()
            speech_msg.data = text
            self.speech_pub.publish(speech_msg)

            # Determine tone (simple keyword matching)
            tone = self._analyze_tone(text)
            self.get_logger().info(f'[TONE] Detected: {tone}')

            tone_msg = String()
            tone_msg.data = tone
            self.tone_pub.publish(tone_msg)

            # Stop listening after processing
            self.is_listening = False

    def _analyze_tone(self, text: str) -> str:
        """
        Simple keyword-based tone analysis.

        In real implementation, this would analyze audio features:
        - Pitch variation
        - Speech rate
        - Energy levels
        """
        happy_words = ['happy', 'good', 'great', 'love', 'thanks', 'hello', 'hi', 'joke']
        sad_words = ['sad', 'sorry', 'bad', 'terrible', 'miss', 'lonely']
        excited_words = ['wow', 'amazing', 'awesome', 'exciting', 'cool']

        text_lower = text.lower()

        for word in excited_words:
            if word in text_lower:
                return 'excited'

        for word in happy_words:
            if word in text_lower:
                return 'happy'

        for word in sad_words:
            if word in text_lower:
                return 'sad'

        return 'neutral'

    def auto_event(self):
        """Generate automatic random events for demo."""
        if random.random() < 0.3:  # 30% chance per interval
            # Simulate wake word + random phrase
            phrase, tone = random.choice(self.phrases)

            # First, wake word
            wake_msg = Bool()
            wake_msg.data = True
            self.wake_pub.publish(wake_msg)

            self.get_logger().info(f'[AUTO] Wake word detected')

            # Then speech after a delay (use timer)
            def delayed_speech():
                speech_msg = String()
                speech_msg.data = phrase
                self.speech_pub.publish(speech_msg)

                tone_msg = String()
                tone_msg.data = tone
                self.tone_pub.publish(tone_msg)

                self.get_logger().info(f'[AUTO] Speech: "{phrase}" (tone: {tone})')

            self.create_timer(0.5, delayed_speech)


def main(args=None):
    rclpy.init(args=args)
    node = AudioSimulator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
