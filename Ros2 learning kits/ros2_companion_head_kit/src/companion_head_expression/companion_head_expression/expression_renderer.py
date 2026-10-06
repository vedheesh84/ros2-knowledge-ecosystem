#!/usr/bin/env python3
"""
expression_renderer.py - Animated face display for Companion Head

LEARNING OBJECTIVES:
====================
1. Expression state representation
2. Animation interpolation (lerp, easing)
3. Layered animation (eyes + mouth)
4. Idle behaviors (blinking, breathing)

EXPRESSION SYSTEM:
==================
The face is rendered as an image with:
- Eyes (shape, size, position, pupil)
- Eyebrows (angle, height)
- Mouth (shape, openness)
- Color tint (mood indicator)

TOPICS:
=======
    Subscribes:
    - /expression/target (companion_head_msgs/Expression): Target expression

    Publishes:
    - /face/display (sensor_msgs/Image): Rendered face image
"""

import math
import random
import time
import numpy as np
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge


class ExpressionState:
    """Current state of face expression."""

    def __init__(self):
        # Eyes
        self.eye_openness = 1.0  # 0 = closed, 1 = fully open
        self.eye_size = 1.0
        self.pupil_x = 0.0  # -1 to 1, gaze direction
        self.pupil_y = 0.0

        # Eyebrows
        self.eyebrow_angle = 0.0  # Negative = sad, positive = angry
        self.eyebrow_height = 0.5  # 0 = low, 1 = high

        # Mouth
        self.mouth_smile = 0.0  # -1 = frown, 1 = smile
        self.mouth_open = 0.0  # 0 = closed, 1 = open

        # Overall
        self.color_tint = (255, 255, 255)  # RGB tint

    def lerp_to(self, other, alpha):
        """Linear interpolation towards another state."""
        self.eye_openness += (other.eye_openness - self.eye_openness) * alpha
        self.eye_size += (other.eye_size - self.eye_size) * alpha
        self.pupil_x += (other.pupil_x - self.pupil_x) * alpha
        self.pupil_y += (other.pupil_y - self.pupil_y) * alpha
        self.eyebrow_angle += (other.eyebrow_angle - self.eyebrow_angle) * alpha
        self.eyebrow_height += (other.eyebrow_height - self.eyebrow_height) * alpha
        self.mouth_smile += (other.mouth_smile - self.mouth_smile) * alpha
        self.mouth_open += (other.mouth_open - self.mouth_open) * alpha

        # Color interpolation
        self.color_tint = tuple(
            int(self.color_tint[i] + (other.color_tint[i] - self.color_tint[i]) * alpha)
            for i in range(3)
        )


class ExpressionRenderer(Node):
    """
    Renders an animated cartoon face.

    Uses OpenCV to draw simple geometric shapes representing
    eyes, eyebrows, and mouth on a canvas.
    """

    def __init__(self):
        super().__init__('expression_renderer')

        # Parameters
        self.declare_parameter('width', 320)
        self.declare_parameter('height', 240)
        self.declare_parameter('fps', 30)
        self.declare_parameter('blink_interval', 3.0)
        self.declare_parameter('transition_speed', 5.0)

        self.width = self.get_parameter('width').value
        self.height = self.get_parameter('height').value
        self.fps = self.get_parameter('fps').value
        self.blink_interval = self.get_parameter('blink_interval').value
        self.transition_speed = self.get_parameter('transition_speed').value

        # Expression definitions
        self.expressions = {
            'neutral': self._create_neutral(),
            'happy': self._create_happy(),
            'sad': self._create_sad(),
            'curious': self._create_curious(),
            'excited': self._create_excited(),
            'sleepy': self._create_sleepy(),
            'surprised': self._create_surprised(),
            'angry': self._create_angry(),
            'confused': self._create_confused(),
        }

        # State
        self.current_state = ExpressionState()
        self.target_state = self._create_neutral()
        self.bridge = CvBridge()

        # Blink state
        self.last_blink = time.time()
        self.is_blinking = False
        self.blink_progress = 0.0

        # Subscriber
        self.expression_sub = self.create_subscription(
            String,  # Using String for simplicity
            '/expression/target',
            self.expression_callback,
            10
        )

        # Publisher
        self.display_pub = self.create_publisher(
            Image,
            '/face/display',
            10
        )

        # Render timer
        self.create_timer(1.0 / self.fps, self.render_frame)

        self.get_logger().info('Expression Renderer initialized')
        self.get_logger().info(f'  Resolution: {self.width}x{self.height}')
        self.get_logger().info(f'  FPS: {self.fps}')
        self.get_logger().info(f'  Expressions: {list(self.expressions.keys())}')

    def _create_neutral(self):
        state = ExpressionState()
        state.eye_openness = 0.9
        state.mouth_smile = 0.0
        state.color_tint = (255, 255, 255)
        return state

    def _create_happy(self):
        state = ExpressionState()
        state.eye_openness = 0.7
        state.eye_size = 1.1
        state.eyebrow_height = 0.7
        state.mouth_smile = 0.8
        state.mouth_open = 0.2
        state.color_tint = (255, 255, 220)  # Warm
        return state

    def _create_sad(self):
        state = ExpressionState()
        state.eye_openness = 0.6
        state.eye_size = 0.9
        state.eyebrow_angle = -20
        state.eyebrow_height = 0.3
        state.mouth_smile = -0.6
        state.color_tint = (200, 200, 255)  # Cool/blue
        return state

    def _create_curious(self):
        state = ExpressionState()
        state.eye_openness = 1.0
        state.eye_size = 1.2
        state.eyebrow_height = 0.8
        state.eyebrow_angle = 10
        state.pupil_y = -0.2  # Look up
        state.mouth_open = 0.1
        state.color_tint = (255, 255, 240)
        return state

    def _create_excited(self):
        state = ExpressionState()
        state.eye_openness = 1.0
        state.eye_size = 1.3
        state.eyebrow_height = 0.9
        state.mouth_smile = 1.0
        state.mouth_open = 0.4
        state.color_tint = (255, 240, 200)  # Bright warm
        return state

    def _create_sleepy(self):
        state = ExpressionState()
        state.eye_openness = 0.3
        state.eye_size = 0.8
        state.eyebrow_height = 0.3
        state.mouth_smile = 0.0
        state.mouth_open = 0.1
        state.color_tint = (220, 220, 240)  # Dim
        return state

    def _create_surprised(self):
        state = ExpressionState()
        state.eye_openness = 1.0
        state.eye_size = 1.4
        state.eyebrow_height = 1.0
        state.mouth_smile = 0.0
        state.mouth_open = 0.6
        state.color_tint = (255, 255, 255)
        return state

    def _create_angry(self):
        state = ExpressionState()
        state.eye_openness = 0.7
        state.eye_size = 0.9
        state.eyebrow_angle = 25
        state.eyebrow_height = 0.4
        state.mouth_smile = -0.3
        state.color_tint = (255, 220, 220)  # Slight red
        return state

    def _create_confused(self):
        state = ExpressionState()
        state.eye_openness = 0.8
        state.eye_size = 1.0
        state.eyebrow_angle = -15
        state.eyebrow_height = 0.6
        state.pupil_x = 0.3  # Look to side
        state.mouth_smile = -0.1
        state.color_tint = (240, 240, 255)
        return state

    def expression_callback(self, msg: String):
        """Handle expression command."""
        name = msg.data.lower().strip()

        if name in self.expressions:
            self.target_state = self.expressions[name]
            self.get_logger().info(f'Expression: {name}')
        else:
            self.get_logger().warn(f'Unknown expression: {name}')

    def render_frame(self):
        """Render and publish a frame."""
        # Update state towards target
        dt = 1.0 / self.fps
        alpha = min(1.0, self.transition_speed * dt)
        self.current_state.lerp_to(self.target_state, alpha)

        # Handle blinking
        self._update_blink()

        # Create canvas
        canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Apply background color tint
        bg_color = tuple(int(c * 0.15) for c in self.current_state.color_tint)
        canvas[:] = bg_color

        # Draw face elements
        self._draw_eyes(canvas)
        self._draw_eyebrows(canvas)
        self._draw_mouth(canvas)

        # Convert to ROS message
        msg = self.bridge.cv2_to_imgmsg(canvas, encoding='bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        self.display_pub.publish(msg)

    def _update_blink(self):
        """Handle automatic blinking."""
        now = time.time()

        if not self.is_blinking:
            # Check if it's time to blink
            if now - self.last_blink > self.blink_interval + random.uniform(-1, 1):
                self.is_blinking = True
                self.blink_progress = 0.0
        else:
            # Progress blink animation
            self.blink_progress += 0.15
            if self.blink_progress >= 1.0:
                self.is_blinking = False
                self.last_blink = now

    def _draw_eyes(self, canvas):
        """Draw both eyes."""
        # Eye centers
        cx = self.width // 2
        cy = self.height // 2 - 20
        eye_spacing = 50

        # Calculate eye openness (including blink)
        openness = self.current_state.eye_openness
        if self.is_blinking:
            # Blink curve: quick close, slow open
            blink_curve = 1.0 - abs(math.sin(self.blink_progress * math.pi))
            openness *= blink_curve

        # Draw left and right eyes
        for side in [-1, 1]:
            ex = cx + side * eye_spacing
            ey = cy

            # Eye size
            size = int(25 * self.current_state.eye_size)

            # Draw eye white (ellipse)
            eye_height = int(size * openness)
            if eye_height > 2:
                cv2.ellipse(canvas, (ex, ey), (size, eye_height),
                            0, 0, 360, (255, 255, 255), -1)

                # Draw pupil
                pupil_size = int(size * 0.4)
                px = ex + int(self.current_state.pupil_x * size * 0.3)
                py = ey + int(self.current_state.pupil_y * eye_height * 0.3)
                cv2.circle(canvas, (px, py), pupil_size, (40, 40, 40), -1)

                # Highlight
                hx = px - pupil_size // 3
                hy = py - pupil_size // 3
                cv2.circle(canvas, (hx, hy), pupil_size // 4, (255, 255, 255), -1)

    def _draw_eyebrows(self, canvas):
        """Draw eyebrows."""
        cx = self.width // 2
        cy = self.height // 2 - 20
        eye_spacing = 50

        brow_y = cy - 35 - int(self.current_state.eyebrow_height * 15)
        brow_len = 30
        angle = self.current_state.eyebrow_angle

        for side in [-1, 1]:
            bx = cx + side * eye_spacing
            by = brow_y

            # Calculate endpoints
            dx = brow_len // 2
            dy = int(math.tan(math.radians(angle * side)) * dx)

            pt1 = (bx - dx, by + dy)
            pt2 = (bx + dx, by - dy)

            cv2.line(canvas, pt1, pt2, (80, 60, 40), 4)

    def _draw_mouth(self, canvas):
        """Draw mouth."""
        cx = self.width // 2
        cy = self.height // 2 + 40

        smile = self.current_state.mouth_smile
        openness = self.current_state.mouth_open

        mouth_width = 40
        mouth_height = int(15 * (1 + openness))

        # Calculate curve
        curve = int(smile * 15)

        # Draw mouth as bezier-ish curve using polylines
        pts = []
        for i in range(21):
            t = i / 20.0 - 0.5
            x = int(cx + t * mouth_width * 2)
            y = int(cy + curve * (1 - 4 * t * t))
            if openness > 0.1:
                y += int(openness * 10 * (1 - 4 * t * t))
            pts.append([x, y])

        pts = np.array(pts, np.int32)
        cv2.polylines(canvas, [pts], False, (80, 60, 60), 3)

        # Fill if mouth is open
        if openness > 0.1:
            lower_pts = []
            for i in range(21):
                t = i / 20.0 - 0.5
                x = int(cx + t * mouth_width * 2)
                y = int(cy + curve * (1 - 4 * t * t) + openness * 20)
                lower_pts.append([x, y])

            all_pts = np.array(pts.tolist() + lower_pts[::-1], np.int32)
            cv2.fillPoly(canvas, [all_pts], (60, 40, 40))


def main(args=None):
    rclpy.init(args=args)
    node = ExpressionRenderer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
