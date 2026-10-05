#!/usr/bin/env python3
"""
face_detector.py - Face detection for Companion Head

LEARNING OBJECTIVES:
====================
1. OpenCV face detection (Haar cascades)
2. Image subscription and processing
3. Detection to 3D position estimation

TOPICS:
=======
    Subscribes:
    - /camera/image_raw (sensor_msgs/Image)

    Publishes:
    - /faces/detections (std_msgs/String): JSON of detected faces
    - /faces/image (sensor_msgs/Image): Annotated image
    - /gaze/target (geometry_msgs/PointStamped): Primary face position
"""

import json
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from geometry_msgs.msg import PointStamped
from cv_bridge import CvBridge


class FaceDetector(Node):
    """
    Detects faces in camera images using OpenCV.

    Uses Haar cascade classifier for real-time face detection.
    """

    def __init__(self):
        super().__init__('face_detector')

        # Parameters
        self.declare_parameter('scale_factor', 1.3)
        self.declare_parameter('min_neighbors', 5)
        self.declare_parameter('min_size', 30)
        self.declare_parameter('focal_length', 500.0)  # Approximate for depth
        self.declare_parameter('known_face_width', 0.15)  # meters

        self.scale_factor = self.get_parameter('scale_factor').value
        self.min_neighbors = self.get_parameter('min_neighbors').value
        self.min_size = self.get_parameter('min_size').value
        self.focal_length = self.get_parameter('focal_length').value
        self.known_face_width = self.get_parameter('known_face_width').value

        # OpenCV setup
        self.bridge = CvBridge()

        # Load Haar cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            self.get_logger().error('Failed to load Haar cascade!')

        # Tracking state
        self.face_id_counter = 0
        self.tracked_faces = {}

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Publishers
        self.detection_pub = self.create_publisher(String, '/faces/detections', 10)
        self.image_pub = self.create_publisher(Image, '/faces/image', 10)
        self.gaze_pub = self.create_publisher(PointStamped, '/gaze/target', 10)

        self.get_logger().info('Face Detector initialized')

    def image_callback(self, msg: Image):
        """Process incoming camera image."""
        try:
            # Convert to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except Exception as e:
            self.get_logger().error(f'CV Bridge error: {e}')
            return

        # Convert to grayscale for detection
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=(self.min_size, self.min_size)
        )

        # Process detections
        detections = []
        primary_face = None
        max_area = 0

        for (x, y, w, h) in faces:
            # Create detection dict
            detection = {
                'id': self._get_face_id(x, y, w, h),
                'bbox': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                'center': {
                    'x': float((x + w/2) / cv_image.shape[1]),
                    'y': float((y + h/2) / cv_image.shape[0])
                },
                'confidence': 0.8,  # Haar doesn't provide confidence
            }

            # Estimate depth based on face size
            depth = (self.known_face_width * self.focal_length) / w
            detection['depth'] = float(depth)

            detections.append(detection)

            # Track largest face as primary
            area = w * h
            if area > max_area:
                max_area = area
                primary_face = detection

            # Draw on image
            cv2.rectangle(cv_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(cv_image, f"ID:{detection['id']}",
                        (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 1)

        # Publish detections
        detection_msg = String()
        detection_msg.data = json.dumps({
            'count': len(detections),
            'faces': detections,
            'primary_id': primary_face['id'] if primary_face else -1
        })
        self.detection_pub.publish(detection_msg)

        # Publish annotated image
        img_msg = self.bridge.cv2_to_imgmsg(cv_image, 'bgr8')
        img_msg.header = msg.header
        self.image_pub.publish(img_msg)

        # Publish gaze target for primary face
        if primary_face:
            self._publish_gaze_target(primary_face, cv_image.shape)

    def _get_face_id(self, x, y, w, h):
        """
        Simple face tracking by position proximity.

        In production, you'd use more sophisticated tracking.
        """
        cx, cy = x + w/2, y + h/2

        # Find closest existing track
        min_dist = float('inf')
        best_id = None

        for face_id, (px, py) in self.tracked_faces.items():
            dist = ((cx - px)**2 + (cy - py)**2)**0.5
            if dist < min_dist and dist < w:  # Within face width
                min_dist = dist
                best_id = face_id

        if best_id is not None:
            self.tracked_faces[best_id] = (cx, cy)
            return best_id
        else:
            self.face_id_counter += 1
            self.tracked_faces[self.face_id_counter] = (cx, cy)
            return self.face_id_counter

    def _publish_gaze_target(self, face, img_shape):
        """Publish a gaze target point for the detected face."""
        # Convert normalized coords to 3D point
        # Assuming camera at origin looking in -Y direction

        # Normalized image coordinates (-0.5 to 0.5)
        nx = face['center']['x'] - 0.5
        ny = face['center']['y'] - 0.5

        # Estimate 3D position
        depth = face['depth']

        # Convert to robot frame coordinates
        # Camera looks in -Y, so:
        # Image X -> Robot -X (left/right)
        # Image Y -> Robot -Z (up/down)
        # Depth -> Robot -Y (forward)

        point = PointStamped()
        point.header.stamp = self.get_clock().now().to_msg()
        point.header.frame_id = 'base_link'
        point.point.x = -nx * depth * 0.8  # Scale by FOV
        point.point.y = -depth
        point.point.z = 0.2 - ny * depth * 0.6  # Head height + vertical offset

        self.gaze_pub.publish(point)


def main(args=None):
    rclpy.init(args=args)
    node = FaceDetector()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
