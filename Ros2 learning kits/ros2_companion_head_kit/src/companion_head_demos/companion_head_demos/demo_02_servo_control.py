#!/usr/bin/env python3
"""
Demo 02: Servo Control & Gestures

LEARNING OBJECTIVES:
====================
1. Pan/tilt kinematics
2. Trajectory generation and smoothing
3. Predefined gesture sequences

WHAT THIS DEMO DOES:
====================
1. Move head through pan/tilt range
2. Execute predefined gestures (nod, shake, curious)
3. Show velocity and acceleration limits

TRY THIS:
=========
- Send position commands manually
- Create your own gesture sequence
- Observe trajectory smoothing

COMMANDS:
=========
    # Run this demo
    ros2 run companion_head_demos demo_02_servo_control

    # Manual gaze control
    ros2 topic pub --once /gaze/target geometry_msgs/PointStamped \\
        "{header: {frame_id: 'base_link'}, point: {x: 0.5, y: -1.0, z: 0.2}}"

    # Trigger gestures
    ros2 topic pub --once /gesture/command std_msgs/String "data: nod_yes"
    ros2 topic pub --once /gesture/command std_msgs/String "data: shake_no"

PREREQUISITE:
=============
    Gazebo simulation or joint_state_publisher_gui
"""

import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PointStamped


class ServoDemo(Node):
    """Demo that shows servo control and gestures."""

    def __init__(self):
        super().__init__('demo_02_servo_control')

        # Demo sequence
        self.sequence = [
            ('gaze', (0.0, -1.0, 0.2), 'Looking center'),
            ('gaze', (-0.5, -1.0, 0.2), 'Looking LEFT'),
            ('gaze', (0.5, -1.0, 0.2), 'Looking RIGHT'),
            ('gaze', (0.0, -1.0, 0.4), 'Looking UP'),
            ('gaze', (0.0, -1.0, 0.0), 'Looking DOWN'),
            ('gaze', (0.0, -1.0, 0.2), 'Back to center'),
            ('gesture', 'nod_yes', 'Gesture: NOD YES'),
            ('gesture', 'shake_no', 'Gesture: SHAKE NO'),
            ('gesture', 'curious_tilt', 'Gesture: CURIOUS TILT'),
            ('gesture', 'greet', 'Gesture: GREETING'),
            ('gaze', (0.0, -1.0, 0.2), 'Demo complete!'),
        ]

        self.current_index = 0
        self.demo_complete = False

        # Publishers
        self.gaze_pub = self.create_publisher(PointStamped, '/gaze/target', 10)
        self.gesture_pub = self.create_publisher(String, '/gesture/command', 10)

        self.get_logger().info('='*60)
        self.get_logger().info('DEMO 02: SERVO CONTROL & GESTURES')
        self.get_logger().info('='*60)
        self.get_logger().info('')
        self.get_logger().info('Make sure the simulation or hardware is running.')
        self.get_logger().info('')
        self.get_logger().info('Starting demo in 3 seconds...')

        # Timer to run sequence
        self.create_timer(3.0, self.run_next_step)

    def run_next_step(self):
        """Execute next step in demo."""
        if self.demo_complete:
            return

        if self.current_index >= len(self.sequence):
            self.demo_complete = True
            self.get_logger().info('')
            self.get_logger().info('='*60)
            self.get_logger().info('Demo complete! Press Ctrl+C to exit.')
            self.get_logger().info('='*60)
            return

        action_type, data, description = self.sequence[self.current_index]

        self.get_logger().info(f'[{self.current_index + 1}/{len(self.sequence)}] {description}')

        if action_type == 'gaze':
            x, y, z = data
            msg = PointStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = 'base_link'
            msg.point.x = x
            msg.point.y = y
            msg.point.z = z
            self.gaze_pub.publish(msg)

        elif action_type == 'gesture':
            msg = String()
            msg.data = data
            self.gesture_pub.publish(msg)

        self.current_index += 1


def main(args=None):
    rclpy.init(args=args)
    node = ServoDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
