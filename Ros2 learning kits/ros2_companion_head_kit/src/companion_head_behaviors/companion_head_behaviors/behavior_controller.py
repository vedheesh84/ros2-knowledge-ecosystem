#!/usr/bin/env python3
"""
behavior_controller.py - Main behavior state machine for Companion Head

LEARNING OBJECTIVES:
====================
1. Behavior state machines
2. Event-driven transitions
3. Coordinating expressions, gestures, and gaze
4. Priority handling

STATE MACHINE:
==============
    IDLE ──────────────► GREETING
      │   (face detected)     │
      │                       │ (greeting done)
      │                       ▼
      │                    TRACKING
      │                       │
      │   ◄───────────────────┘
      │   (face lost)
      │
      └──────────────────► LISTENING
          (wake word)          │
                               │ (speech received)
                               ▼
                           RESPONDING
                               │
                               │ (response done)
                               ▼
                             IDLE

TOPICS:
=======
    Subscribes:
    - /faces/detections
    - /audio/wake_word
    - /audio/speech
    - /mood/state

    Publishes:
    - /behavior/state (current state)
    - /expression/target
    - /gesture/command
    - /gaze/target
"""

import json
import time
from enum import Enum, auto
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import PointStamped


class BehaviorState(Enum):
    """High-level behavior states."""
    IDLE = auto()
    GREETING = auto()
    TRACKING = auto()
    LISTENING = auto()
    RESPONDING = auto()
    SLEEPING = auto()


class BehaviorController(Node):
    """
    Main behavior coordinator for the companion head.

    Orchestrates expressions, gestures, and gaze based on
    inputs from perception and mood systems.
    """

    def __init__(self):
        super().__init__('behavior_controller')

        # Parameters
        self.declare_parameter('idle_timeout', 60.0)
        self.declare_parameter('greeting_duration', 2.0)
        self.declare_parameter('response_duration', 3.0)

        self.idle_timeout = self.get_parameter('idle_timeout').value
        self.greeting_duration = self.get_parameter('greeting_duration').value
        self.response_duration = self.get_parameter('response_duration').value

        # State
        self.state = BehaviorState.IDLE
        self.state_start_time = time.time()
        self.last_activity = time.time()

        # Perception state
        self.face_detected = False
        self.face_count = 0
        self.current_mood = 'neutral'
        self.last_speech = ""

        # Subscribers
        self.faces_sub = self.create_subscription(
            String, '/faces/detections', self.faces_callback, 10)
        self.wake_sub = self.create_subscription(
            Bool, '/audio/wake_word', self.wake_callback, 10)
        self.speech_sub = self.create_subscription(
            String, '/audio/speech', self.speech_callback, 10)
        self.mood_sub = self.create_subscription(
            String, '/mood/state', self.mood_callback, 10)

        # Publishers
        self.state_pub = self.create_publisher(String, '/behavior/state', 10)
        self.expression_pub = self.create_publisher(String, '/expression/target', 10)
        self.gesture_pub = self.create_publisher(String, '/gesture/command', 10)

        # State machine timer
        self.create_timer(0.1, self.update_state)  # 10 Hz

        self.get_logger().info('Behavior Controller initialized')
        self._enter_state(BehaviorState.IDLE)

    def faces_callback(self, msg: String):
        """Handle face detection updates."""
        try:
            data = json.loads(msg.data)
            prev_detected = self.face_detected
            self.face_count = data.get('count', 0)
            self.face_detected = self.face_count > 0

            # Trigger greeting on new face
            if self.face_detected and not prev_detected:
                if self.state == BehaviorState.IDLE:
                    self._enter_state(BehaviorState.GREETING)
        except json.JSONDecodeError:
            pass

    def wake_callback(self, msg: Bool):
        """Handle wake word detection."""
        if msg.data:
            self.last_activity = time.time()
            if self.state not in [BehaviorState.LISTENING, BehaviorState.RESPONDING]:
                self._enter_state(BehaviorState.LISTENING)

    def speech_callback(self, msg: String):
        """Handle recognized speech."""
        self.last_speech = msg.data
        self.last_activity = time.time()

        if self.state == BehaviorState.LISTENING:
            self._enter_state(BehaviorState.RESPONDING)

    def mood_callback(self, msg: String):
        """Update current mood."""
        try:
            data = json.loads(msg.data)
            self.current_mood = data.get('mood', 'neutral')
        except json.JSONDecodeError:
            pass

    def _enter_state(self, new_state: BehaviorState):
        """Transition to a new state."""
        old_state = self.state
        self.state = new_state
        self.state_start_time = time.time()

        self.get_logger().info(f'State: {old_state.name} -> {new_state.name}')

        # Publish state
        state_msg = String()
        state_msg.data = new_state.name
        self.state_pub.publish(state_msg)

        # Execute entry actions
        if new_state == BehaviorState.IDLE:
            self._publish_expression('neutral')

        elif new_state == BehaviorState.GREETING:
            self._publish_expression('happy')
            self._publish_gesture('greet')

        elif new_state == BehaviorState.TRACKING:
            self._publish_expression('curious')

        elif new_state == BehaviorState.LISTENING:
            self._publish_expression('attentive')
            self._publish_gesture('attentive')

        elif new_state == BehaviorState.RESPONDING:
            self._respond_to_speech()

        elif new_state == BehaviorState.SLEEPING:
            self._publish_expression('sleepy')

    def _publish_expression(self, name: str):
        """Publish expression command."""
        msg = String()
        msg.data = name
        self.expression_pub.publish(msg)

    def _publish_gesture(self, name: str):
        """Publish gesture command."""
        msg = String()
        msg.data = name
        self.gesture_pub.publish(msg)

    def _respond_to_speech(self):
        """Generate response to recognized speech."""
        speech = self.last_speech.lower()

        # Simple keyword responses
        if 'hello' in speech or 'hi' in speech:
            self._publish_expression('happy')
            self._publish_gesture('nod_yes')

        elif 'sad' in speech or 'unhappy' in speech:
            self._publish_expression('sad')
            self._publish_gesture('sad')

        elif 'joke' in speech or 'funny' in speech:
            self._publish_expression('excited')
            self._publish_gesture('curious_tilt')

        elif 'thank' in speech:
            self._publish_expression('happy')
            self._publish_gesture('acknowledge')

        elif 'bye' in speech or 'goodbye' in speech:
            self._publish_expression('sad')
            self._publish_gesture('shake_no')

        else:
            # Default: curious response
            self._publish_expression('curious')
            self._publish_gesture('think')

    def update_state(self):
        """State machine update."""
        elapsed = time.time() - self.state_start_time
        idle_time = time.time() - self.last_activity

        # State transitions
        if self.state == BehaviorState.IDLE:
            if idle_time > self.idle_timeout:
                self._enter_state(BehaviorState.SLEEPING)

        elif self.state == BehaviorState.GREETING:
            if elapsed > self.greeting_duration:
                if self.face_detected:
                    self._enter_state(BehaviorState.TRACKING)
                else:
                    self._enter_state(BehaviorState.IDLE)

        elif self.state == BehaviorState.TRACKING:
            if not self.face_detected:
                self._enter_state(BehaviorState.IDLE)
            # Expression follows mood while tracking
            elif elapsed > 2.0:
                self._publish_expression(self.current_mood)

        elif self.state == BehaviorState.LISTENING:
            # Timeout back to tracking/idle
            if elapsed > 10.0:
                if self.face_detected:
                    self._enter_state(BehaviorState.TRACKING)
                else:
                    self._enter_state(BehaviorState.IDLE)

        elif self.state == BehaviorState.RESPONDING:
            if elapsed > self.response_duration:
                if self.face_detected:
                    self._enter_state(BehaviorState.TRACKING)
                else:
                    self._enter_state(BehaviorState.IDLE)

        elif self.state == BehaviorState.SLEEPING:
            if self.face_detected or idle_time < 5.0:
                self._enter_state(BehaviorState.GREETING)


def main(args=None):
    rclpy.init(args=args)
    node = BehaviorController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
