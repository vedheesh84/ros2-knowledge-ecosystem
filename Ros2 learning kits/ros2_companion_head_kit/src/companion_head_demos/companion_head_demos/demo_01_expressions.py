#!/usr/bin/env python3
"""
Demo 01: Face Display & Expressions

LEARNING OBJECTIVES:
====================
1. Understand expression state representation
2. See animation interpolation in action
3. Learn about idle animations (blinking, breathing)

WHAT THIS DEMO DOES:
====================
1. Launches the expression_renderer node
2. Cycles through all available expressions
3. Shows smooth transitions between expressions
4. Demonstrates automatic blinking

TRY THIS:
=========
- Watch the eye blink timing (automatic)
- Notice the smooth transition between expressions
- Observe the color mood changes in the background

COMMANDS:
=========
    # Run this demo
    ros2 run companion_head_demos demo_01_expressions

    # Manually set expressions
    ros2 topic pub --once /expression/target std_msgs/String "data: happy"
    ros2 topic pub --once /expression/target std_msgs/String "data: sad"

PREREQUISITE:
=============
    ros2 run companion_head_expression expression_renderer
"""

import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ExpressionDemo(Node):
    """Demo that cycles through expressions."""

    def __init__(self):
        super().__init__('demo_01_expressions')

        # Expression sequence
        self.expressions = [
            ('neutral', 'Starting with neutral...'),
            ('happy', 'Now showing HAPPY - notice the smile and warm colors'),
            ('sad', 'Now showing SAD - droopy eyes and cool blue tint'),
            ('curious', 'Now showing CURIOUS - wide eyes looking up'),
            ('excited', 'Now showing EXCITED - big eyes and bright colors'),
            ('surprised', 'Now showing SURPRISED - wide open eyes and mouth'),
            ('sleepy', 'Now showing SLEEPY - half-closed eyes'),
            ('angry', 'Now showing ANGRY - furrowed brows'),
            ('confused', 'Now showing CONFUSED - asymmetric expression'),
            ('neutral', 'Back to neutral. Demo complete!'),
        ]

        self.current_index = 0
        self.demo_complete = False

        # Publisher
        self.expression_pub = self.create_publisher(String, '/expression/target', 10)

        # Wait for expression renderer
        self.get_logger().info('='*60)
        self.get_logger().info('DEMO 01: FACE DISPLAY & EXPRESSIONS')
        self.get_logger().info('='*60)
        self.get_logger().info('')
        self.get_logger().info('Make sure expression_renderer is running:')
        self.get_logger().info('  ros2 run companion_head_expression expression_renderer')
        self.get_logger().info('')
        self.get_logger().info('View the face display in RViz (Image panel)')
        self.get_logger().info('  Topic: /face/display')
        self.get_logger().info('')
        self.get_logger().info('Starting demo in 3 seconds...')
        self.get_logger().info('')

        # Timer to cycle expressions
        self.create_timer(3.0, self.show_next_expression)

    def show_next_expression(self):
        """Show the next expression in sequence."""
        if self.demo_complete:
            return

        if self.current_index >= len(self.expressions):
            self.demo_complete = True
            self.get_logger().info('')
            self.get_logger().info('='*60)
            self.get_logger().info('Demo complete! Press Ctrl+C to exit.')
            self.get_logger().info('='*60)
            return

        expression, description = self.expressions[self.current_index]

        # Publish expression
        msg = String()
        msg.data = expression
        self.expression_pub.publish(msg)

        # Log
        self.get_logger().info(f'[{self.current_index + 1}/{len(self.expressions)}] {description}')

        self.current_index += 1


def main(args=None):
    rclpy.init(args=args)
    node = ExpressionDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
