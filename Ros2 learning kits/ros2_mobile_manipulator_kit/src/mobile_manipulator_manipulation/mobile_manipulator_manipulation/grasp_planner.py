#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Grasp Planner - Compute Grasp Poses
===================================

LEARNING OBJECTIVES:
- Understand grasp pose computation
- See approach vector selection
- Learn grasp frame conventions
- Practice collision-aware planning

GRASP FRAME CONVENTION:
- X: Approach direction (into object)
- Y: Gripper closing direction
- Z: Perpendicular (thumb direction)

GRASP TYPES:
1. Top-down: Approach from above (most common)
2. Side: Approach from side (for tall objects)
3. Angled: Compromised approach angle
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import math


@dataclass
class GraspPose:
    """
    Complete grasp pose specification.

    LEARNING: A grasp needs both position and orientation.
    The approach direction determines how the gripper aligns.
    """
    # Position (in arm_base_link frame)
    x: float
    y: float
    z: float

    # Orientation (roll, pitch, yaw in radians)
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    # Approach offset (how far to start from grasp point)
    pre_grasp_distance: float = 0.05  # 5cm

    # Post-grasp lift height
    post_grasp_lift: float = 0.10  # 10cm


class GraspPlanner:
    """
    Computes grasp poses for pick-and-place.

    LEARNING OBJECTIVES:
    - Compute approach poses from object position
    - Handle workspace limits
    - Select grasp orientation
    """

    def __init__(
        self,
        workspace_min: Tuple[float, float, float] = (0.1, -0.2, 0.0),
        workspace_max: Tuple[float, float, float] = (0.4, 0.2, 0.3),
        table_height: float = 0.0,
    ):
        """
        Initialize grasp planner.

        Args:
            workspace_min: (x, y, z) minimum reachable position
            workspace_max: (x, y, z) maximum reachable position
            table_height: Z height of table surface
        """
        self.workspace_min = workspace_min
        self.workspace_max = workspace_max
        self.table_height = table_height

    def plan_top_down_grasp(
        self,
        object_x: float,
        object_y: float,
        object_z: float,
        object_height: float = 0.05,
    ) -> Optional[GraspPose]:
        """
        Plan a top-down grasp.

        LEARNING: Top-down grasps approach from directly above.
        Best for objects on flat surfaces.

        Orientation: gripper pointing down (pitch = pi/2)

        Args:
            object_x, object_y, object_z: Object center position
            object_height: Object height for grasp point calculation

        Returns:
            GraspPose if reachable, None otherwise
        """
        # Grasp point is at middle height of object
        grasp_z = object_z + object_height / 2.0

        # Check workspace limits
        if not self._in_workspace(object_x, object_y, grasp_z):
            return None

        # Top-down orientation: gripper pointing down
        # pitch = pi/2 makes gripper point down (Z toward table)
        return GraspPose(
            x=object_x,
            y=object_y,
            z=grasp_z,
            roll=0.0,
            pitch=math.pi / 2,  # Point down
            yaw=0.0,
            pre_grasp_distance=0.08,
            post_grasp_lift=0.10,
        )

    def plan_side_grasp(
        self,
        object_x: float,
        object_y: float,
        object_z: float,
        approach_from: str = 'front',
    ) -> Optional[GraspPose]:
        """
        Plan a side grasp.

        LEARNING: Side grasps approach horizontally.
        Better for tall objects that might tip over.

        Args:
            object_x, object_y, object_z: Object center position
            approach_from: 'front', 'left', 'right', 'back'

        Returns:
            GraspPose if reachable, None otherwise
        """
        if not self._in_workspace(object_x, object_y, object_z):
            return None

        # Determine yaw based on approach direction
        yaw_map = {
            'front': 0.0,
            'left': math.pi / 2,
            'right': -math.pi / 2,
            'back': math.pi,
        }
        yaw = yaw_map.get(approach_from, 0.0)

        # Side grasp: gripper horizontal
        return GraspPose(
            x=object_x,
            y=object_y,
            z=object_z,
            roll=0.0,
            pitch=0.0,  # Horizontal
            yaw=yaw,
            pre_grasp_distance=0.08,
            post_grasp_lift=0.08,
        )

    def compute_pre_grasp(self, grasp: GraspPose) -> Tuple[float, float, float]:
        """
        Compute pre-grasp approach position.

        LEARNING: Pre-grasp is offset along the approach direction.
        For top-down, this means moving up. For side, moving back.
        """
        # For top-down (pitch = pi/2), approach is in -Z
        if abs(grasp.pitch - math.pi / 2) < 0.1:
            return (
                grasp.x,
                grasp.y,
                grasp.z + grasp.pre_grasp_distance
            )

        # For side grasp, approach along X (body frame forward)
        return (
            grasp.x - grasp.pre_grasp_distance * math.cos(grasp.yaw),
            grasp.y - grasp.pre_grasp_distance * math.sin(grasp.yaw),
            grasp.z
        )

    def compute_post_grasp(self, grasp: GraspPose) -> Tuple[float, float, float]:
        """
        Compute post-grasp lift position.

        LEARNING: After grasping, lift the object to clear obstacles.
        """
        return (
            grasp.x,
            grasp.y,
            grasp.z + grasp.post_grasp_lift
        )

    def _in_workspace(self, x: float, y: float, z: float) -> bool:
        """Check if position is within arm workspace."""
        return (
            self.workspace_min[0] <= x <= self.workspace_max[0] and
            self.workspace_min[1] <= y <= self.workspace_max[1] and
            self.workspace_min[2] <= z <= self.workspace_max[2]
        )

    def get_workspace_center(self) -> Tuple[float, float, float]:
        """Get center of workspace (good default target)."""
        return (
            (self.workspace_min[0] + self.workspace_max[0]) / 2,
            (self.workspace_min[1] + self.workspace_max[1]) / 2,
            (self.workspace_min[2] + self.workspace_max[2]) / 2,
        )
