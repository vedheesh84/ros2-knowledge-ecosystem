#!/usr/bin/env python3
# Copyright (c) 2024 ROS2 Learning Kit
# MIT License

"""
Manipulation Node - ROS2 Pick-Place Controller
===============================================

LEARNING OBJECTIVES:
- See state machine integration with ROS2
- Understand command/status interface
- Learn perception → manipulation coordination
- Practice safe operation patterns

TOPICS:
  Subscribe:
    /manipulation/command (String): 'start', 'stop', 'reset'
    /perception/object_pose (PoseStamped): Detected object pose

  Publish:
    /manipulation/state (String): Current state name
    /manipulation/status (String): Status messages

USAGE:
  ros2 run mobile_manipulator_manipulation manipulation_node.py

  # Start pick-place
  ros2 topic pub /manipulation/command std_msgs/String "data: start" --once

  # Monitor state
  ros2 topic echo /manipulation/state
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped

from mobile_manipulator_manipulation.state_machine import (
    PickPlaceStateMachine,
    ManipulationState,
    ManipulationConfig,
    GraspPose,
)
from mobile_manipulator_manipulation.grasp_planner import GraspPlanner

from typing import Optional


class ManipulationNode(Node):
    """
    Main manipulation controller node.

    LEARNING OBJECTIVES:
    - Bridges state machine to ROS2
    - Subscribes to perception for object poses
    - Publishes state for monitoring
    """

    def __init__(self):
        super().__init__('manipulation_node')

        # Parameters
        self.declare_parameter('tick_rate', 10.0)
        self.declare_parameter('place_x', 0.25)
        self.declare_parameter('place_y', 0.15)
        self.declare_parameter('place_z', 0.05)

        tick_rate = self.get_parameter('tick_rate').value
        place_x = self.get_parameter('place_x').value
        place_y = self.get_parameter('place_y').value
        place_z = self.get_parameter('place_z').value

        # State machine
        config = ManipulationConfig(
            detection_timeout=15.0,
            motion_timeout=10.0,
            state_delay=0.5,
        )
        self.state_machine = PickPlaceStateMachine(config)
        self.state_machine.set_place_pose(place_x, place_y, place_z)

        # Set callbacks
        self.state_machine.set_callbacks(
            detect_fn=self._detect_object,
            move_fn=self._move_arm,
            gripper_fn=self._control_gripper,
            on_state_change=self._on_state_change,
        )

        # Grasp planner
        self.grasp_planner = GraspPlanner()

        # Latest detected object
        self._latest_object_pose: Optional[PoseStamped] = None

        # Publishers
        self.state_pub = self.create_publisher(
            String, '/manipulation/state', 10
        )
        self.status_pub = self.create_publisher(
            String, '/manipulation/status', 10
        )

        # Subscribers
        self.command_sub = self.create_subscription(
            String, '/manipulation/command', self._command_callback, 10
        )
        self.object_pose_sub = self.create_subscription(
            PoseStamped, '/perception/object_pose', self._object_pose_callback, 10
        )

        # State machine timer
        self.create_timer(1.0 / tick_rate, self._tick)

        # Status timer
        self.create_timer(1.0, self._publish_state)

        self.get_logger().info(
            'Manipulation node started. '
            'Send "start" to /manipulation/command to begin.'
        )

    def _command_callback(self, msg: String):
        """Handle manipulation commands."""
        command = msg.data.lower().strip()
        self.get_logger().info(f'Command received: {command}')

        if command == 'start':
            self._publish_status('Starting pick-place sequence')
            self.state_machine.start()
        elif command == 'stop':
            self._publish_status('Stopping manipulation')
            self.state_machine.stop()
        elif command == 'reset':
            self._publish_status('Resetting to IDLE')
            self.state_machine.reset()
        else:
            self.get_logger().warn(f'Unknown command: {command}')

    def _object_pose_callback(self, msg: PoseStamped):
        """Store latest detected object pose."""
        self._latest_object_pose = msg

    def _tick(self):
        """Execute state machine tick."""
        self.state_machine.tick()

    def _on_state_change(
        self,
        old_state: ManipulationState,
        new_state: ManipulationState
    ):
        """Handle state transitions."""
        self.get_logger().info(f'State: {old_state.name} → {new_state.name}')
        self._publish_state()

        if new_state == ManipulationState.ERROR:
            self._publish_status('ERROR - send "reset" to recover')
        elif new_state == ManipulationState.IDLE:
            if old_state == ManipulationState.RETRACTING:
                self._publish_status('Pick-place cycle complete!')

    def _publish_state(self):
        """Publish current state."""
        msg = String()
        msg.data = self.state_machine.state.name
        self.state_pub.publish(msg)

    def _publish_status(self, status: str):
        """Publish status message."""
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)
        self.get_logger().info(f'Status: {status}')

    # ===========================================
    # State machine callbacks
    # ===========================================

    def _detect_object(self) -> Optional[GraspPose]:
        """
        Detect callback for state machine.

        LEARNING: This bridges perception to manipulation.
        Returns grasp pose when object is detected.
        """
        if self._latest_object_pose is None:
            return None

        pose = self._latest_object_pose.pose
        self._latest_object_pose = None  # Consume

        # Plan grasp from detected pose
        grasp = self.grasp_planner.plan_top_down_grasp(
            object_x=pose.position.x,
            object_y=pose.position.y,
            object_z=pose.position.z,
        )

        if grasp:
            self.get_logger().info(
                f'Object detected at ({pose.position.x:.3f}, '
                f'{pose.position.y:.3f}, {pose.position.z:.3f})'
            )
            # Convert to state machine GraspPose format
            return GraspPose(x=grasp.x, y=grasp.y, z=grasp.z)

        self.get_logger().warn('Object outside workspace')
        return None

    def _move_arm(self, x: float, y: float, z: float) -> bool:
        """
        Move callback for state machine.

        LEARNING: This would call MoveIt in a real system.
        For now, just log the intended motion.
        """
        self.get_logger().info(f'Moving arm to ({x:.3f}, {y:.3f}, {z:.3f})')
        # TODO: Integrate with ArmInterface
        return True

    def _control_gripper(self, open_gripper: bool) -> bool:
        """
        Gripper callback for state machine.

        LEARNING: This would call gripper action in a real system.
        """
        action = 'Opening' if open_gripper else 'Closing'
        self.get_logger().info(f'{action} gripper')
        # TODO: Integrate with ArmInterface
        return True


def main(args=None):
    rclpy.init(args=args)
    node = ManipulationNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
