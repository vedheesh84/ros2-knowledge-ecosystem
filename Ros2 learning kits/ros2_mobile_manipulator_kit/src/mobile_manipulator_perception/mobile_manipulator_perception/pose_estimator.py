#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Pose Estimator - 2D to 3D Projection
====================================

LEARNING OBJECTIVES:
- Understand pinhole camera model
- See pixel-to-3D projection math
- Learn camera intrinsic parameters
- Practice TF frame transforms

PINHOLE CAMERA MODEL:
  u = fx * (X/Z) + cx
  v = fy * (Y/Z) + cy

  Where:
  - (u, v): pixel coordinates
  - (X, Y, Z): 3D coordinates in camera frame
  - fx, fy: focal lengths (pixels)
  - cx, cy: principal point (image center)

POSE ESTIMATION WITHOUT DEPTH:
  If we know the real object size, we can estimate Z:
  Z = (real_width * fx) / pixel_width

  Then X and Y follow from the pinhole model.

KEY CONCEPT - CAMERA FRAMES:
  - camera_link: ROS convention (X-forward)
  - camera_link_optical: OpenCV convention (Z-forward)
  - Detections are in optical frame!
"""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class CameraInfo:
    """Camera intrinsic parameters."""
    fx: float  # Focal length X (pixels)
    fy: float  # Focal length Y (pixels)
    cx: float  # Principal point X (pixels)
    cy: float  # Principal point Y (pixels)
    width: int  # Image width
    height: int  # Image height


@dataclass
class ObjectPose:
    """3D object pose in camera optical frame."""
    x: float  # X position (meters)
    y: float  # Y position (meters)
    z: float  # Z position / depth (meters)
    confidence: float  # Pose confidence


class PoseEstimator:
    """
    Estimates 3D pose from 2D detection.

    LEARNING OBJECTIVES:
    - Uses known object size for depth estimation
    - Projects pixel coordinates to 3D
    - Outputs pose in camera optical frame

    IMPORTANT FRAME CONVENTION:
    - Output is in camera_link_optical frame
    - Z points forward (into the scene)
    - X points right
    - Y points down
    """

    def __init__(
        self,
        camera_info: CameraInfo,
        known_object_width: float = 0.05,  # 5cm default
    ):
        """
        Initialize pose estimator.

        Args:
            camera_info: Camera intrinsic parameters
            known_object_width: Real-world object width (meters)
        """
        self.camera = camera_info
        self.known_width = known_object_width

    def estimate_pose(
        self,
        pixel_x: int,
        pixel_y: int,
        pixel_width: int,
    ) -> Optional[ObjectPose]:
        """
        Estimate 3D pose from 2D detection.

        LEARNING:
        1. Estimate depth from known object size
        2. Back-project pixel to ray
        3. Scale ray by estimated depth

        Args:
            pixel_x: Detection center X in pixels
            pixel_y: Detection center Y in pixels
            pixel_width: Detection width in pixels

        Returns:
            ObjectPose in camera optical frame, or None if invalid
        """
        if pixel_width <= 0:
            return None

        # Step 1: Estimate depth from known object size
        # LEARNING: This is the key insight - if we know real size,
        # we can estimate distance using similar triangles
        z = (self.known_width * self.camera.fx) / pixel_width

        # Step 2: Back-project pixel to camera ray
        # LEARNING: Invert the pinhole camera equations
        x = (pixel_x - self.camera.cx) * z / self.camera.fx
        y = (pixel_y - self.camera.cy) * z / self.camera.fy

        # Confidence decreases with distance (larger error at distance)
        confidence = min(1.0, 0.5 / z) if z > 0 else 0.0

        return ObjectPose(x=x, y=y, z=z, confidence=confidence)

    def estimate_pose_with_depth(
        self,
        pixel_x: int,
        pixel_y: int,
        depth: float,
    ) -> Optional[ObjectPose]:
        """
        Estimate 3D pose using known depth.

        LEARNING: If you have a depth camera, this is more accurate
        than estimating from object size.

        Args:
            pixel_x: Detection center X in pixels
            pixel_y: Detection center Y in pixels
            depth: Known depth in meters

        Returns:
            ObjectPose in camera optical frame
        """
        if depth <= 0:
            return None

        # Back-project using known depth
        x = (pixel_x - self.camera.cx) * depth / self.camera.fx
        y = (pixel_y - self.camera.cy) * depth / self.camera.fy

        # High confidence with known depth
        confidence = 0.9

        return ObjectPose(x=x, y=y, z=depth, confidence=confidence)

    def optical_to_ros(
        self,
        optical_pose: ObjectPose
    ) -> Tuple[float, float, float]:
        """
        Convert from optical frame to ROS frame.

        LEARNING - Frame conventions:
        - Optical (OpenCV): X-right, Y-down, Z-forward
        - ROS (camera_link): X-forward, Y-left, Z-up

        Transformation:
        - ROS X = Optical Z
        - ROS Y = -Optical X
        - ROS Z = -Optical Y
        """
        ros_x = optical_pose.z   # Depth becomes forward
        ros_y = -optical_pose.x  # Right becomes left (negated)
        ros_z = -optical_pose.y  # Down becomes up (negated)

        return (ros_x, ros_y, ros_z)


def create_default_camera_info(width: int = 640, height: int = 480) -> CameraInfo:
    """
    Create default camera intrinsics.

    LEARNING: These are typical values for a USB webcam.
    For accurate results, calibrate your actual camera!

    Typical FOV: 60-70 degrees
    fx = width / (2 * tan(FOV/2))
    """
    # Assume 60 degree horizontal FOV
    fov_rad = math.radians(60)
    fx = width / (2 * math.tan(fov_rad / 2))
    fy = fx  # Square pixels

    return CameraInfo(
        fx=fx,
        fy=fy,
        cx=width / 2.0,
        cy=height / 2.0,
        width=width,
        height=height,
    )
