#!/usr/bin/env python3
"""
Demo 05: Mood Engine

LEARNING OBJECTIVES:
====================
1. Emotional state as continuous variables
2. Decay and excitation dynamics
3. Stimulus-response modeling
4. Mood-to-expression mapping

MOOD MODEL:
===========
    mood[t+1] = mood[t] * decay + stimulus_effect

WHAT THIS DEMO DOES:
====================
1. Display mood state in real-time
2. Show how stimuli affect mood
3. Demonstrate decay to neutral

TRY THIS:
=========
- Send positive tone (happy) - watch valence increase
- Send negative tone (sad) - watch valence decrease
- Wait and watch decay to neutral

COMMANDS:
=========
    # Run this demo
    ros2 run companion_head_demos demo_05_mood

    # Send tones to affect mood
    ros2 topic pub --once /audio/tone std_msgs/String "data: happy"
    ros2 topic pub --once /audio/tone std_msgs/String "data: sad"
    ros2 topic pub --once /audio/tone std_msgs/String "data: excited"

PREREQUISITE:
=============
    ros2 run companion_head_behaviors mood_engine
"""

import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MoodDemo(Node):
    """Demo that visualizes mood dynamics."""

    def __init__(self):
        super().__init__('demo_05_mood')

        self.last_mood = None

        # Publisher for tones
        self.tone_pub = self.create_publisher(String, '/audio/tone', 10)

        # Subscribe to mood
        self.mood_sub = self.create_subscription(
            String, '/mood/state', self.mood_callback, 10)

        self.get_logger().info('='*60)
        self.get_logger().info('DEMO 05: MOOD ENGINE')
        self.get_logger().info('='*60)
        self.get_logger().info('')
        self.get_logger().info('Make sure mood_engine is running:')
        self.get_logger().info('  ros2 run companion_head_behaviors mood_engine')
        self.get_logger().info('')
        self.get_logger().info('Mood Dimensions:')
        self.get_logger().info('  Valence:    -1 (sad) to +1 (happy)')
        self.get_logger().info('  Arousal:     0 (sleepy) to 1 (excited)')
        self.get_logger().info('  Engagement:  0 (bored) to 1 (interested)')
        self.get_logger().info('')
        self.get_logger().info('Watching mood state...')
        self.get_logger().info('')

        # Demo sequence
        self.create_timer(5.0, self.send_stimulus)
        self.demo_step = 0

    def send_stimulus(self):
        """Send mood stimuli."""
        stimuli = [
            ('happy', 'Sending HAPPY tone...'),
            ('excited', 'Sending EXCITED tone...'),
            ('sad', 'Sending SAD tone...'),
            ('neutral', 'Sending NEUTRAL tone (waiting for decay)...'),
        ]

        if self.demo_step < len(stimuli):
            tone, description = stimuli[self.demo_step]
            self.get_logger().info(f'[STIMULUS] {description}')

            msg = String()
            msg.data = tone
            self.tone_pub.publish(msg)

            self.demo_step += 1

    def mood_callback(self, msg: String):
        """Display mood state."""
        try:
            data = json.loads(msg.data)
            mood = data.get('mood', 'unknown')
            valence = data.get('valence', 0)
            arousal = data.get('arousal', 0)
            engagement = data.get('engagement', 0)

            # Create visual bar
            def bar(val, width=20, min_v=-1, max_v=1):
                normalized = (val - min_v) / (max_v - min_v)
                filled = int(normalized * width)
                return '[' + '=' * filled + ' ' * (width - filled) + ']'

            if mood != self.last_mood:
                self.get_logger().info(f'')
                self.get_logger().info(f'[MOOD] {mood.upper()}')
                self.last_mood = mood

            self.get_logger().info(
                f'  V: {bar(valence)} {valence:+.2f} | '
                f'A: {bar(arousal, min_v=0)} {arousal:.2f} | '
                f'E: {bar(engagement, min_v=0)} {engagement:.2f}'
            )

        except json.JSONDecodeError:
            pass


def main(args=None):
    rclpy.init(args=args)
    node = MoodDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
