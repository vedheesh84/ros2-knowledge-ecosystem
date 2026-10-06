# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Mobile Manipulator Perception Module
=====================================

LEARNING OBJECTIVES:
- Provides object detection for manipulation
- Handles camera-to-world transforms
- Implements classical CV detection methods
"""

from mobile_manipulator_perception.object_detector import ObjectDetector
from mobile_manipulator_perception.pose_estimator import PoseEstimator

__all__ = ['ObjectDetector', 'PoseEstimator']
