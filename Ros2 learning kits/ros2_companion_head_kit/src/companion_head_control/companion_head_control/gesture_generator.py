#!/usr/bin/env python3
"""
gesture_generator.py - Predefined gesture motions for Companion Head

LEARNING OBJECTIVES:
====================
1. Gesture as motion sequences
2. State machine for animation
3. Timing and interpolation

GESTURES:
=========
- nod_yes: Tilt up/down sequence (agreement)
- shake_no: Pan left/right sequence (disagreement)
- curious_tilt: Tilt head to one side (interest)
- attentive: Slight forward lean + look up
- acknowledge: Quick small nod
- think: Look up and to the side
- greet: Wave motion (pan + tilt combo)

TOPICS:
=======
    Subscribes:
    - /gesture/command (std_msgs/String): Gesture name to execute

    Publishes:
    - /joint_trajectory_controller/joint_trajectory: Joint commands
"""

import math
from enum import Enum, auto
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class GestureState(Enum):
    """Gesture execution states."""
    IDLE = auto()
    EXECUTING = auto()
    RETURNING = auto()


class GestureGenerator(Node):
    """
    Generates predefined gestures for the companion head.

    Each gesture is a sequence of joint positions with timing.
    """

    def __init__(self):
        super().__init__('gesture_generator')

        # Parameters
        self.declare_parameter('gesture_speed', 1.0)  # Speed multiplier
        self.speed = self.get_parameter('gesture_speed').value

        # State
        self.state = GestureState.IDLE
        self.current_gesture = None
        self.gesture_index = 0
        self.start_time = None

        # Define gestures as sequences of (pan, tilt, duration) tuples
        self.gestures = {
            'nod_yes': [
                (0.0, 0.3, 0.3),   # Look up
                (0.0, -0.2, 0.3),  # Look down
                (0.0, 0.2, 0.2),   # Up again
                (0.0, -0.1, 0.2),  # Down
                (0.0, 0.0, 0.3),   # Return to center
            ],
            'shake_no': [
                (-0.4, 0.0, 0.25),  # Left
                (0.4, 0.0, 0.35),   # Right
                (-0.3, 0.0, 0.3),   # Left
                (0.3, 0.0, 0.3),    # Right
                (0.0, 0.0, 0.3),    # Center
            ],
            'curious_tilt': [
                (0.0, 0.0, 0.1),
                (0.2, -0.3, 0.4),   # Tilt right and look down slightly
                (0.2, -0.3, 0.8),   # Hold
                (0.0, 0.0, 0.4),    # Return
            ],
            'attentive': [
                (0.0, 0.15, 0.3),   # Look up slightly
                (0.0, 0.15, 0.5),   # Hold
                (0.0, 0.0, 0.3),    # Return
            ],
            'acknowledge': [
                (0.0, 0.1, 0.15),   # Quick up
                (0.0, -0.05, 0.15), # Quick down
                (0.0, 0.0, 0.2),    # Return
            ],
            'think': [
                (0.3, 0.25, 0.5),   # Look up-right
                (0.3, 0.25, 1.0),   # Hold (thinking)
                (0.0, 0.0, 0.4),    # Return
            ],
            'greet': [
                (0.0, 0.1, 0.2),    # Look up
                (-0.2, 0.1, 0.2),   # Wave left
                (0.2, 0.1, 0.3),    # Wave right
                (-0.1, 0.05, 0.2),  # Wave left
                (0.1, 0.05, 0.2),   # Wave right
                (0.0, 0.0, 0.3),    # Return
            ],
            'sad': [
                (0.0, -0.3, 0.5),   # Look down
                (0.0, -0.3, 1.0),   # Hold
                (0.0, 0.0, 0.5),    # Return slowly
            ],
            'surprised': [
                (0.0, 0.35, 0.15),  # Quick look up
                (0.0, 0.35, 0.4),   # Hold
                (0.0, 0.0, 0.3),    # Return
            ],
            'idle_sway': [
                (0.1, 0.05, 1.0),   # Slight right
                (-0.1, -0.05, 2.0), # Slight left
                (0.05, 0.0, 1.5),   # Back
                (0.0, 0.0, 1.0),    # Center
            ],
        }

        # Subscriber
        self.command_sub = self.create_subscription(
            String,
            '/gesture/command',
            self.command_callback,
            10
        )

        # Publisher
        self.trajectory_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )

        # Execution timer
        self.create_timer(0.1, self.execute_gesture)

        self.get_logger().info('Gesture Generator initialized')
        self.get_logger().info(f'Available gestures: {list(self.gestures.keys())}')

    def command_callback(self, msg: String):
        """Handle gesture command."""
        gesture_name = msg.data.lower().strip()

        if gesture_name not in self.gestures:
            self.get_logger().warn(f'Unknown gesture: {gesture_name}')
            self.get_logger().info(f'Available: {list(self.gestures.keys())}')
            return

        if self.state != GestureState.IDLE:
            self.get_logger().info(f'Gesture in progress, queuing: {gesture_name}')
            return

        self.get_logger().info(f'Executing gesture: {gesture_name}')
        self.current_gesture = self.gestures[gesture_name]
        self.gesture_index = 0
        self.state = GestureState.EXECUTING
        self.send_gesture_point()

    def send_gesture_point(self):
        """Send the current gesture point as a trajectory."""
        if self.current_gesture is None:
            return

        if self.gesture_index >= len(self.current_gesture):
            self.state = GestureState.IDLE
            self.current_gesture = None
            return

        pan, tilt, duration = self.current_gesture[self.gesture_index]
        duration = duration / self.speed  # Apply speed multiplier

        # Create trajectory
        traj = JointTrajectory()
        traj.header.stamp = self.get_clock().now().to_msg()
        traj.joint_names = ['neck_pan_joint', 'neck_tilt_joint']

        point = JointTrajectoryPoint()
        point.positions = [pan, tilt]
        point.velocities = [0.0, 0.0]
        point.time_from_start = Duration(
            sec=int(duration),
            nanosec=int((duration % 1) * 1e9)
        )

        traj.points = [point]
        self.trajectory_pub.publish(traj)

        # Record start time
        self.start_time = self.get_clock().now()

    def execute_gesture(self):
        """Check if current gesture point is complete and advance."""
        if self.state != GestureState.EXECUTING:
            return

        if self.current_gesture is None or self.start_time is None:
            return

        # Get expected duration
        _, _, duration = self.current_gesture[self.gesture_index]
        duration = duration / self.speed

        # Check if enough time has passed
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9

        if elapsed >= duration:
            # Move to next point
            self.gesture_index += 1
            if self.gesture_index < len(self.current_gesture):
                self.send_gesture_point()
            else:
                self.state = GestureState.IDLE
                self.current_gesture = None
                self.get_logger().info('Gesture complete')


def main(args=None):
    rclpy.init(args=args)
    node = GestureGenerator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
