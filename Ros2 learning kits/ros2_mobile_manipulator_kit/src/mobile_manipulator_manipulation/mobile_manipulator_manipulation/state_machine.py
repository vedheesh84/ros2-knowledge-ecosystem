#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Pick-Place State Machine
========================

LEARNING OBJECTIVES:
- Understand finite state machine (FSM) patterns
- See how states model manipulation phases
- Learn transitions based on success/failure
- Practice safe state machine design

STATE DIAGRAM:
```
      ┌──────────────────────────────────────────────┐
      │                                              │
      v                                              │
    IDLE ──> DETECTING ──> PRE_GRASP ──> GRASPING   │
                │              │            │        │
             timeout        failure      failure     │
                │              │            │        │
                v              v            v        │
              IDLE ←───────── ERROR ←──────┘        │
                                                     │
    GRASPING ──> POST_GRASP ──> TRANSPORTING        │
                     │              │                │
                  failure        failure             │
                     │              │                │
                     v              v                │
                   ERROR ←─────────┘                 │
                                                     │
    TRANSPORTING ──> PRE_PLACE ──> PLACING ──> RETRACTING
                         │            │            │
                      failure      failure         │
                         │            │            │
                         v            v            │
                       ERROR ←───────┘             │
                                                   │
    RETRACTING ─────────────────────────────────────┘
```

KEY DESIGN PATTERNS:
1. Each state has clear entry/exit conditions
2. Failure in any state goes to ERROR
3. ERROR state allows reset to IDLE
4. State machine runs in timer callback
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Callable
import time


class ManipulationState(Enum):
    """
    States in the pick-place state machine.

    LEARNING: Each state represents a distinct phase
    of the manipulation task.
    """
    IDLE = auto()          # Waiting for command
    DETECTING = auto()     # Looking for object
    PRE_GRASP = auto()     # Moving to approach pose
    GRASPING = auto()      # Closing gripper on object
    POST_GRASP = auto()    # Lifting object
    TRANSPORTING = auto()  # Moving to place location
    PRE_PLACE = auto()     # Approaching place pose
    PLACING = auto()       # Opening gripper
    RETRACTING = auto()    # Retracting arm
    ERROR = auto()         # Error recovery


@dataclass
class ManipulationConfig:
    """Configuration for state machine."""
    detection_timeout: float = 10.0   # Max time to detect object
    motion_timeout: float = 5.0       # Max time for arm motion
    gripper_timeout: float = 2.0      # Max time for gripper action
    state_delay: float = 0.3          # Delay between states
    max_retries: int = 2              # Retries per state


@dataclass
class GraspPose:
    """Target grasp pose."""
    x: float
    y: float
    z: float
    pre_grasp_offset: float = 0.05  # Approach from above


class PickPlaceStateMachine:
    """
    Finite state machine for pick-and-place.

    LEARNING OBJECTIVES:
    - See state machine execution loop
    - Understand callbacks for actions
    - Learn error handling patterns

    USAGE:
        sm = PickPlaceStateMachine()
        sm.set_callbacks(
            detect_fn=my_detect,
            move_fn=my_move,
            gripper_fn=my_gripper
        )
        sm.start()

        # In timer loop:
        sm.tick()
    """

    def __init__(self, config: Optional[ManipulationConfig] = None):
        """Initialize state machine."""
        self.config = config or ManipulationConfig()
        self._state = ManipulationState.IDLE
        self._running = False
        self._retry_count = 0

        # Current grasp target
        self._grasp_pose: Optional[GraspPose] = None
        self._place_pose: Optional[GraspPose] = None

        # Callbacks for actions (set by user)
        self._detect_callback: Optional[Callable] = None
        self._move_callback: Optional[Callable] = None
        self._gripper_callback: Optional[Callable] = None

        # State change callback
        self._on_state_change: Optional[Callable] = None

        # Timing
        self._state_start_time = 0.0

    @property
    def state(self) -> ManipulationState:
        """Current state."""
        return self._state

    @property
    def is_running(self) -> bool:
        """Whether state machine is active."""
        return self._running

    def set_callbacks(
        self,
        detect_fn: Optional[Callable] = None,
        move_fn: Optional[Callable] = None,
        gripper_fn: Optional[Callable] = None,
        on_state_change: Optional[Callable] = None,
    ):
        """
        Set action callbacks.

        LEARNING: State machine delegates actual work to callbacks.
        This separates logic (state machine) from execution (ROS nodes).

        Args:
            detect_fn: () -> Optional[GraspPose] - detect object
            move_fn: (x, y, z) -> bool - move arm to pose
            gripper_fn: (open: bool) -> bool - control gripper
            on_state_change: (old, new) -> None - state change notification
        """
        self._detect_callback = detect_fn
        self._move_callback = move_fn
        self._gripper_callback = gripper_fn
        self._on_state_change = on_state_change

    def set_place_pose(self, x: float, y: float, z: float):
        """Set target place location."""
        self._place_pose = GraspPose(x=x, y=y, z=z)

    def start(self):
        """Start the state machine."""
        if self._running:
            return

        self._running = True
        self._retry_count = 0
        self._set_state(ManipulationState.DETECTING)

    def stop(self):
        """Stop the state machine."""
        self._running = False
        self._set_state(ManipulationState.IDLE)

    def reset(self):
        """Reset from error state."""
        self._retry_count = 0
        self._grasp_pose = None
        self._set_state(ManipulationState.IDLE)

    def tick(self):
        """
        Execute one tick of the state machine.

        LEARNING: Call this in a timer callback (e.g., 10Hz).
        State machine checks current state and takes action.
        """
        if not self._running:
            return

        # Check for timeout in current state
        elapsed = time.time() - self._state_start_time

        if self._state == ManipulationState.DETECTING:
            self._tick_detecting(elapsed)
        elif self._state == ManipulationState.PRE_GRASP:
            self._tick_pre_grasp(elapsed)
        elif self._state == ManipulationState.GRASPING:
            self._tick_grasping(elapsed)
        elif self._state == ManipulationState.POST_GRASP:
            self._tick_post_grasp(elapsed)
        elif self._state == ManipulationState.TRANSPORTING:
            self._tick_transporting(elapsed)
        elif self._state == ManipulationState.PRE_PLACE:
            self._tick_pre_place(elapsed)
        elif self._state == ManipulationState.PLACING:
            self._tick_placing(elapsed)
        elif self._state == ManipulationState.RETRACTING:
            self._tick_retracting(elapsed)

    def _set_state(self, new_state: ManipulationState):
        """Change state with notification."""
        old_state = self._state
        if old_state == new_state:
            return

        self._state = new_state
        self._state_start_time = time.time()

        if self._on_state_change:
            self._on_state_change(old_state, new_state)

    def _go_to_error(self, message: str):
        """Transition to error state."""
        self._set_state(ManipulationState.ERROR)
        self._running = False

    # =========================================
    # State tick implementations
    # =========================================

    def _tick_detecting(self, elapsed: float):
        """Look for object to grasp."""
        if elapsed > self.config.detection_timeout:
            self._go_to_error("Detection timeout")
            return

        if self._detect_callback:
            pose = self._detect_callback()
            if pose:
                self._grasp_pose = pose
                time.sleep(self.config.state_delay)
                self._set_state(ManipulationState.PRE_GRASP)

    def _tick_pre_grasp(self, elapsed: float):
        """Move to pre-grasp approach pose."""
        if elapsed > self.config.motion_timeout:
            self._go_to_error("Pre-grasp timeout")
            return

        if self._grasp_pose and self._move_callback:
            # Move to position above grasp point
            pre_z = self._grasp_pose.z + self._grasp_pose.pre_grasp_offset
            success = self._move_callback(
                self._grasp_pose.x,
                self._grasp_pose.y,
                pre_z
            )
            if success:
                # Open gripper
                if self._gripper_callback:
                    self._gripper_callback(True)  # open
                time.sleep(self.config.state_delay)
                self._set_state(ManipulationState.GRASPING)
            elif self._retry_count < self.config.max_retries:
                self._retry_count += 1
            else:
                self._go_to_error("Pre-grasp failed")

    def _tick_grasping(self, elapsed: float):
        """Move down and close gripper."""
        if elapsed > self.config.motion_timeout:
            self._go_to_error("Grasping timeout")
            return

        if self._grasp_pose and self._move_callback:
            # Move to grasp position
            success = self._move_callback(
                self._grasp_pose.x,
                self._grasp_pose.y,
                self._grasp_pose.z
            )
            if success:
                # Close gripper
                if self._gripper_callback:
                    time.sleep(self.config.state_delay)
                    self._gripper_callback(False)  # close
                time.sleep(self.config.state_delay)
                self._set_state(ManipulationState.POST_GRASP)
            elif self._retry_count < self.config.max_retries:
                self._retry_count += 1
            else:
                self._go_to_error("Grasping failed")

    def _tick_post_grasp(self, elapsed: float):
        """Lift object after grasping."""
        if elapsed > self.config.motion_timeout:
            self._go_to_error("Post-grasp timeout")
            return

        if self._grasp_pose and self._move_callback:
            # Lift object
            lift_z = self._grasp_pose.z + 0.1  # 10cm lift
            success = self._move_callback(
                self._grasp_pose.x,
                self._grasp_pose.y,
                lift_z
            )
            if success:
                time.sleep(self.config.state_delay)
                self._set_state(ManipulationState.TRANSPORTING)
            else:
                self._go_to_error("Post-grasp lift failed")

    def _tick_transporting(self, elapsed: float):
        """Move to place location (horizontal motion)."""
        if elapsed > self.config.motion_timeout:
            self._go_to_error("Transport timeout")
            return

        if self._place_pose and self._move_callback:
            # Move above place location
            pre_z = self._place_pose.z + 0.1
            success = self._move_callback(
                self._place_pose.x,
                self._place_pose.y,
                pre_z
            )
            if success:
                time.sleep(self.config.state_delay)
                self._set_state(ManipulationState.PRE_PLACE)
            else:
                self._go_to_error("Transport failed")

    def _tick_pre_place(self, elapsed: float):
        """Approach place position."""
        if elapsed > self.config.motion_timeout:
            self._go_to_error("Pre-place timeout")
            return

        if self._place_pose and self._move_callback:
            success = self._move_callback(
                self._place_pose.x,
                self._place_pose.y,
                self._place_pose.z
            )
            if success:
                time.sleep(self.config.state_delay)
                self._set_state(ManipulationState.PLACING)
            else:
                self._go_to_error("Pre-place failed")

    def _tick_placing(self, elapsed: float):
        """Open gripper to place object."""
        if elapsed > self.config.gripper_timeout:
            self._go_to_error("Place timeout")
            return

        if self._gripper_callback:
            self._gripper_callback(True)  # open
            time.sleep(self.config.state_delay)
            self._set_state(ManipulationState.RETRACTING)

    def _tick_retracting(self, elapsed: float):
        """Retract arm and return to IDLE."""
        if elapsed > self.config.motion_timeout:
            self._go_to_error("Retract timeout")
            return

        if self._place_pose and self._move_callback:
            # Lift away from placed object
            retract_z = self._place_pose.z + 0.1
            success = self._move_callback(
                self._place_pose.x,
                self._place_pose.y,
                retract_z
            )
            if success:
                # Cycle complete!
                self._grasp_pose = None
                self._retry_count = 0
                time.sleep(self.config.state_delay)
                self._set_state(ManipulationState.IDLE)
                self._running = False
            else:
                self._go_to_error("Retract failed")
