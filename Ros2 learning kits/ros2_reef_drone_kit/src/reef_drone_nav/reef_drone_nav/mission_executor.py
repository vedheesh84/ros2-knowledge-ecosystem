#!/usr/bin/env python3
"""
mission_executor.py - Mission State Machine for AUV

MISSION STRUCTURE:
==================
A mission is a sequence of tasks, each with:
  - Type: navigation, survey, hold, surface
  - Parameters: waypoints, patterns, durations
  - Completion criteria

MISSION STATES:
===============
  IDLE      → Waiting for mission
  DESCEND   → Diving to operating depth
  NAVIGATE  → Moving to waypoint
  SURVEY    → Executing survey pattern
  HOLD      → Station keeping
  SURFACE   → Returning to surface
  ABORT     → Emergency surfacing

EXAMPLE MISSION:
================
1. DESCEND to 10m
2. NAVIGATE to survey start
3. SURVEY lawnmower pattern
4. NAVIGATE to recovery point
5. SURFACE

Topics:
  Subscribe: /odom (nav_msgs/Odometry)
  Subscribe: /mission/command (std_msgs/String)
  Publish: /waypoints (geometry_msgs/PoseArray)
  Publish: /mission/status (std_msgs/String)
"""

import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseArray, Pose
from nav_msgs.msg import Odometry
import transforms3d


class MissionState:
    IDLE = 'IDLE'
    DESCEND = 'DESCEND'
    NAVIGATE = 'NAVIGATE'
    SURVEY = 'SURVEY'
    HOLD = 'HOLD'
    SURFACE = 'SURFACE'
    ABORT = 'ABORT'


class MissionExecutor(Node):
    """Executes pre-defined AUV missions."""

    def __init__(self):
        super().__init__('mission_executor')

        # Parameters
        self.declare_parameter('operating_depth', -10.0)  # m
        self.declare_parameter('surface_depth', -1.0)     # m

        self.operating_depth = self.get_parameter('operating_depth').value
        self.surface_depth = self.get_parameter('surface_depth').value

        # State
        self.state = MissionState.IDLE
        self.current_position = np.zeros(3)
        self.mission_waypoints = []
        self.current_wp_idx = 0

        # Subscribers
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.cmd_sub = self.create_subscription(
            String, '/mission/command', self.command_callback, 10)

        # Publishers
        self.waypoint_pub = self.create_publisher(PoseArray, '/waypoints', 10)
        self.status_pub = self.create_publisher(String, '/mission/status', 10)

        # State machine timer (1 Hz)
        self.timer = self.create_timer(1.0, self.state_machine)

        self.get_logger().info('Mission Executor started')

    def odom_callback(self, msg: Odometry):
        """Update current position."""
        self.current_position = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z
        ])

    def command_callback(self, msg: String):
        """Process mission commands."""
        cmd = msg.data.lower()

        if cmd == 'start_demo':
            self.start_demo_mission()
        elif cmd == 'abort':
            self.state = MissionState.ABORT
            self.get_logger().warn('ABORT command received!')
        elif cmd == 'surface':
            self.state = MissionState.SURFACE
        else:
            self.get_logger().info(f'Unknown command: {cmd}')

    def start_demo_mission(self):
        """Start a demonstration survey mission."""
        self.get_logger().info('Starting demo mission...')

        # Generate lawnmower survey pattern
        self.mission_waypoints = self._generate_survey_pattern(
            start_x=0.0, start_y=0.0,
            length=10.0, width=6.0,
            spacing=2.0,
            depth=self.operating_depth
        )

        self.current_wp_idx = 0
        self.state = MissionState.DESCEND

    def _generate_survey_pattern(
        self, start_x: float, start_y: float,
        length: float, width: float, spacing: float,
        depth: float
    ) -> list:
        """
        Generate lawnmower survey pattern.

              →→→→→→→→→→
                       ↓
              ←←←←←←←←←←
              ↓
              →→→→→→→→→→
        """
        waypoints = []
        num_lines = int(width / spacing) + 1
        direction = 1  # 1 = positive X, -1 = negative X

        for i in range(num_lines):
            y = start_y + i * spacing
            heading = 0.0 if direction == 1 else np.pi

            x_start = start_x if direction == 1 else start_x + length
            x_end = start_x + length if direction == 1 else start_x

            # Leg start waypoint
            waypoints.append({
                'x': x_start,
                'y': y,
                'z': depth,
                'heading': heading
            })

            # Leg end waypoint
            waypoints.append({
                'x': x_end,
                'y': y,
                'z': depth,
                'heading': heading
            })

            direction *= -1

        return waypoints


    def state_machine(self):
        """Execute state machine logic."""
        status = String()
        status.data = self.state
        self.status_pub.publish(status)

        if self.state == MissionState.IDLE:
            pass  # Waiting for command

        elif self.state == MissionState.DESCEND:
            # Check if at operating depth
            if self.current_position[2] <= self.operating_depth + 0.5:
                self.state = MissionState.NAVIGATE
                self._publish_waypoints()
                self.get_logger().info('Reached operating depth, navigating...')
            else:
                # Publish descent waypoint
                wp = PoseArray()
                wp.header.frame_id = 'odom'
                pose = Pose()
                pose.position.x = self.current_position[0]
                pose.position.y = self.current_position[1]
                pose.position.z = self.operating_depth
                pose.orientation.w = 1.0
                wp.poses.append(pose)
                self.waypoint_pub.publish(wp)

        elif self.state == MissionState.NAVIGATE:
            # Check mission progress
            if self.current_wp_idx >= len(self.mission_waypoints):
                self.state = MissionState.SURFACE
                self.get_logger().info('Survey complete, surfacing...')

        elif self.state == MissionState.SURFACE:
            # Publish surface waypoint
            wp = PoseArray()
            wp.header.frame_id = 'odom'
            pose = Pose()
            pose.position.x = self.current_position[0]
            pose.position.y = self.current_position[1]
            pose.position.z = self.surface_depth
            pose.orientation.w = 1.0
            wp.poses.append(pose)
            self.waypoint_pub.publish(wp)

            if self.current_position[2] >= self.surface_depth - 0.5:
                self.state = MissionState.IDLE
                self.get_logger().info('Mission complete!')

        elif self.state == MissionState.ABORT:
            # Emergency surface
            wp = PoseArray()
            wp.header.frame_id = 'odom'
            pose = Pose()
            pose.position.x = self.current_position[0]
            pose.position.y = self.current_position[1]
            pose.position.z = 0.0  # Surface
            pose.orientation.w = 1.0
            wp.poses.append(pose)
            self.waypoint_pub.publish(wp)

    def _publish_waypoints(self):
        """Publish mission waypoints."""
        wp = PoseArray()
        wp.header.frame_id = 'odom'

        for waypoint in self.mission_waypoints:
            pose = Pose()
            pose.position.x = waypoint['x']
            pose.position.y = waypoint['y']
            pose.position.z = waypoint['z']
            quat = transforms3d.euler.euler2quat(0, 0, waypoint['heading'])
            pose.orientation.w = quat[0]
            pose.orientation.x = quat[1]
            pose.orientation.y = quat[2]
            pose.orientation.z = quat[3]
            wp.poses.append(pose)

        self.waypoint_pub.publish(wp)


def main(args=None):
    rclpy.init(args=args)
    node = MissionExecutor()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException, Exception):
        pass
    finally:
        try:
            node.destroy_node()
            rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
