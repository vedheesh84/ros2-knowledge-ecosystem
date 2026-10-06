#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Object Detector - Classical CV Detection
=========================================

LEARNING OBJECTIVES:
- Understand HSV color space for detection
- See contour analysis for shape detection
- Learn image preprocessing techniques
- Practice handling noisy detections

DETECTION PIPELINE:
1. Convert BGR to HSV
2. Apply color mask
3. Morphological operations (denoise)
4. Find contours
5. Filter by area/shape
6. Calculate centroid

KEY CONCEPTS:
- HSV: Better for color detection than RGB
- Morphology: Opening removes noise, closing fills holes
- Contours: Boundary of detected regions
- Moments: Calculate centroid from contour
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Detection:
    """Object detection result."""
    label: str           # Object class (e.g., 'red_cube', 'blue_sphere')
    confidence: float    # Detection confidence (0-1)
    center_x: int        # Pixel X coordinate
    center_y: int        # Pixel Y coordinate
    width: int           # Bounding box width
    height: int          # Bounding box height
    contour: np.ndarray  # OpenCV contour


class ObjectDetector:
    """
    Classical computer vision object detector.

    LEARNING OBJECTIVES:
    - No ML required - works with basic OpenCV
    - Tunable parameters for different objects
    - Good for controlled environments
    """

    # Default color ranges (HSV)
    # LEARNING: HSV ranges are tricky - red wraps around 0/180
    COLOR_RANGES = {
        'red': {
            # Red has two ranges in HSV (wraps around)
            'lower1': np.array([0, 100, 100]),
            'upper1': np.array([10, 255, 255]),
            'lower2': np.array([160, 100, 100]),
            'upper2': np.array([180, 255, 255]),
        },
        'green': {
            'lower': np.array([35, 100, 100]),
            'upper': np.array([85, 255, 255]),
        },
        'blue': {
            'lower': np.array([100, 100, 100]),
            'upper': np.array([130, 255, 255]),
        },
        'yellow': {
            'lower': np.array([20, 100, 100]),
            'upper': np.array([35, 255, 255]),
        },
    }

    def __init__(
        self,
        min_area: int = 500,
        max_area: int = 50000,
        blur_kernel: int = 5,
    ):
        """
        Initialize detector.

        Args:
            min_area: Minimum contour area (pixels^2)
            max_area: Maximum contour area (pixels^2)
            blur_kernel: Gaussian blur kernel size
        """
        self.min_area = min_area
        self.max_area = max_area
        self.blur_kernel = blur_kernel

    def detect_by_color(
        self,
        image: np.ndarray,
        color: str
    ) -> List[Detection]:
        """
        Detect objects by color.

        LEARNING:
        - Convert to HSV first (more robust to lighting)
        - Use inRange() for color thresholding
        - Apply morphology to clean up mask

        Args:
            image: BGR image from camera
            color: Color name ('red', 'green', 'blue', 'yellow')

        Returns:
            List of Detection objects
        """
        if color not in self.COLOR_RANGES:
            return []

        # Preprocess
        blurred = cv2.GaussianBlur(image, (self.blur_kernel, self.blur_kernel), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Create color mask
        ranges = self.COLOR_RANGES[color]
        if 'lower1' in ranges:
            # Handle red (wraps around HSV)
            mask1 = cv2.inRange(hsv, ranges['lower1'], ranges['upper1'])
            mask2 = cv2.inRange(hsv, ranges['lower2'], ranges['upper2'])
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            mask = cv2.inRange(hsv, ranges['lower'], ranges['upper'])

        # Morphological operations
        # LEARNING: Opening removes noise, closing fills holes
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Process detections
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_area <= area <= self.max_area:
                detection = self._contour_to_detection(contour, color)
                if detection:
                    detections.append(detection)

        return detections

    def detect_shapes(
        self,
        image: np.ndarray,
        target_shape: str = 'rectangle'
    ) -> List[Detection]:
        """
        Detect objects by shape.

        LEARNING:
        - approxPolyDP simplifies contours
        - Vertex count indicates shape:
          - 3 vertices = triangle
          - 4 vertices = rectangle/square
          - 5+ vertices = polygon
          - many vertices = circle

        Args:
            image: BGR image
            target_shape: 'triangle', 'rectangle', 'circle'

        Returns:
            List of Detection objects
        """
        # Convert to grayscale and detect edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (self.blur_kernel, self.blur_kernel), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # Find contours
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area or area > self.max_area:
                continue

            # Approximate polygon
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            vertices = len(approx)

            # Classify shape
            shape = None
            if vertices == 3:
                shape = 'triangle'
            elif vertices == 4:
                # Check if square or rectangle
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                shape = 'square' if 0.9 <= aspect_ratio <= 1.1 else 'rectangle'
            elif vertices > 6:
                # Check circularity
                circularity = 4 * np.pi * area / (perimeter ** 2)
                if circularity > 0.7:
                    shape = 'circle'

            if shape == target_shape or target_shape == 'any':
                detection = self._contour_to_detection(contour, shape)
                if detection:
                    detections.append(detection)

        return detections

    def _contour_to_detection(
        self,
        contour: np.ndarray,
        label: str
    ) -> Optional[Detection]:
        """Convert contour to Detection object."""
        # Calculate centroid using moments
        moments = cv2.moments(contour)
        if moments['m00'] == 0:
            return None

        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])

        # Bounding box
        x, y, w, h = cv2.boundingRect(contour)

        # Confidence based on contour area (larger = more confident)
        area = cv2.contourArea(contour)
        confidence = min(1.0, area / self.max_area)

        return Detection(
            label=label,
            confidence=confidence,
            center_x=cx,
            center_y=cy,
            width=w,
            height=h,
            contour=contour,
        )

    def draw_detections(
        self,
        image: np.ndarray,
        detections: List[Detection],
        color: Tuple[int, int, int] = (0, 255, 0)
    ) -> np.ndarray:
        """
        Draw detections on image for visualization.

        LEARNING: Always visualize detections for debugging!
        """
        output = image.copy()

        for det in detections:
            # Draw contour
            cv2.drawContours(output, [det.contour], -1, color, 2)

            # Draw centroid
            cv2.circle(output, (det.center_x, det.center_y), 5, (0, 0, 255), -1)

            # Draw label
            label = f'{det.label} ({det.confidence:.2f})'
            cv2.putText(
                output, label,
                (det.center_x - 50, det.center_y - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )

        return output
