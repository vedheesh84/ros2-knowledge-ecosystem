#!/usr/bin/env python3
"""
mood_engine.py - Emotional state dynamics for Companion Head

LEARNING OBJECTIVES:
====================
1. Emotional state as continuous variables
2. Decay and excitation dynamics
3. Stimulus-response modeling
4. Mood-to-expression mapping

MOOD MODEL:
===========
The robot has continuous emotional dimensions:
- Valence: negative to positive (-1 to 1)
- Arousal: calm to excited (0 to 1)
- Engagement: bored to interested (0 to 1)

These are influenced by:
- User detected emotions (empathy)
- Speech tone analysis
- Interaction frequency
- Time decay

MOOD DYNAMICS:
==============
    mood[t+1] = mood[t] * decay + stimulus_effect + noise

TOPICS:
=======
    Subscribes:
    - /audio/tone (std_msgs/String): User speech tone
    - /faces/detections (std_msgs/String): Face detections

    Publishes:
    - /mood/state (std_msgs/String): Current mood as JSON
    - /expression/target (std_msgs/String): Recommended expression
"""

import json
import time
import random
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class MoodEngine(Node):
    """
    Manages the robot's internal emotional state.

    Uses continuous emotional dimensions that evolve over time
    based on inputs and natural decay.
    """

    def __init__(self):
        super().__init__('mood_engine')

        # Parameters
        self.declare_parameter('decay_rate', 0.98)
        self.declare_parameter('empathy_weight', 0.3)
        self.declare_parameter('interaction_boost', 0.1)
        self.declare_parameter('neutral_valence', 0.1)
        self.declare_parameter('neutral_arousal', 0.3)

        self.decay_rate = self.get_parameter('decay_rate').value
        self.empathy_weight = self.get_parameter('empathy_weight').value
        self.interaction_boost = self.get_parameter('interaction_boost').value
        self.neutral_valence = self.get_parameter('neutral_valence').value
        self.neutral_arousal = self.get_parameter('neutral_arousal').value

        # Emotional state
        self.valence = self.neutral_valence  # -1 to 1
        self.arousal = self.neutral_arousal  # 0 to 1
        self.engagement = 0.5  # 0 to 1

        # Tracking
        self.last_interaction = time.time()
        self.face_detected = False

        # Tone to mood mapping
        self.tone_effects = {
            'happy': {'valence': 0.3, 'arousal': 0.1},
            'excited': {'valence': 0.2, 'arousal': 0.3},
            'sad': {'valence': -0.3, 'arousal': -0.1},
            'angry': {'valence': -0.2, 'arousal': 0.2},
            'neutral': {'valence': 0.0, 'arousal': 0.0},
        }

        # Subscribers
        self.tone_sub = self.create_subscription(
            String, '/audio/tone', self.tone_callback, 10)
        self.faces_sub = self.create_subscription(
            String, '/faces/detections', self.faces_callback, 10)
        self.wake_sub = self.create_subscription(
            Bool, '/audio/wake_word', self.wake_callback, 10)

        # Publishers
        self.mood_pub = self.create_publisher(String, '/mood/state', 10)
        self.expression_pub = self.create_publisher(String, '/expression/target', 10)

        # Update timer
        self.create_timer(0.5, self.update_mood)  # 2 Hz

        self.get_logger().info('Mood Engine initialized')
        self.get_logger().info(f'  Decay rate: {self.decay_rate}')
        self.get_logger().info(f'  Empathy weight: {self.empathy_weight}')

    def tone_callback(self, msg: String):
        """Respond to detected speech tone."""
        tone = msg.data.lower()

        if tone in self.tone_effects:
            effect = self.tone_effects[tone]

            # Apply empathy effect
            self.valence += effect['valence'] * self.empathy_weight
            self.arousal += effect['arousal'] * self.empathy_weight

            # Interaction boosts engagement
            self.engagement = min(1.0, self.engagement + self.interaction_boost)
            self.last_interaction = time.time()

            self.get_logger().info(f'Tone effect: {tone} -> v:{effect["valence"]:.2f}, a:{effect["arousal"]:.2f}')

    def faces_callback(self, msg: String):
        """Track face presence."""
        try:
            data = json.loads(msg.data)
            self.face_detected = data.get('count', 0) > 0

            if self.face_detected:
                # Face presence slightly increases engagement
                self.engagement = min(1.0, self.engagement + 0.02)
        except json.JSONDecodeError:
            pass

    def wake_callback(self, msg: Bool):
        """Respond to wake word detection."""
        if msg.data:
            # Wake word increases arousal and engagement
            self.arousal = min(1.0, self.arousal + 0.2)
            self.engagement = min(1.0, self.engagement + 0.3)
            self.last_interaction = time.time()

    def update_mood(self):
        """Update mood with decay and publish state."""
        # Time since last interaction
        idle_time = time.time() - self.last_interaction

        # Apply decay towards neutral
        self.valence = self.valence * self.decay_rate + self.neutral_valence * (1 - self.decay_rate)
        self.arousal = self.arousal * self.decay_rate + self.neutral_arousal * (1 - self.decay_rate)

        # Engagement decays faster when no face detected
        engagement_decay = 0.95 if self.face_detected else 0.90
        self.engagement *= engagement_decay

        # Very long idle makes robot sleepy
        if idle_time > 30:
            self.arousal = max(0.1, self.arousal - 0.01)

        # Clamp values
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(0.0, min(1.0, self.arousal))
        self.engagement = max(0.1, min(1.0, self.engagement))

        # Add tiny random noise for liveliness
        self.valence += random.uniform(-0.01, 0.01)
        self.arousal += random.uniform(-0.01, 0.01)

        # Determine primary mood
        mood = self._classify_mood()

        # Publish mood state
        state = {
            'mood': mood,
            'valence': round(self.valence, 3),
            'arousal': round(self.arousal, 3),
            'engagement': round(self.engagement, 3),
            'idle_time': round(idle_time, 1),
        }

        mood_msg = String()
        mood_msg.data = json.dumps(state)
        self.mood_pub.publish(mood_msg)

        # Publish expression recommendation
        expression = self._mood_to_expression(mood)
        expr_msg = String()
        expr_msg.data = expression
        self.expression_pub.publish(expr_msg)

    def _classify_mood(self) -> str:
        """Classify continuous mood into discrete category."""
        v, a, e = self.valence, self.arousal, self.engagement

        # Decision tree for mood classification
        if a < 0.2:
            return 'sleepy'
        elif e < 0.2:
            return 'neutral'
        elif v > 0.3 and a > 0.5:
            return 'excited'
        elif v > 0.2:
            return 'happy'
        elif v < -0.3:
            return 'sad'
        elif v < -0.1 and a > 0.4:
            return 'confused'
        else:
            return 'neutral'

    def _mood_to_expression(self, mood: str) -> str:
        """Map mood to expression name."""
        mapping = {
            'sleepy': 'sleepy',
            'excited': 'excited',
            'happy': 'happy',
            'sad': 'sad',
            'confused': 'confused',
            'neutral': 'neutral',
        }
        return mapping.get(mood, 'neutral')


def main(args=None):
    rclpy.init(args=args)
    node = MoodEngine()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
