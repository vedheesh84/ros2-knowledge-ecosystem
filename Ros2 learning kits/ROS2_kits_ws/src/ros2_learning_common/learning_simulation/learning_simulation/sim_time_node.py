#!/usr/bin/env python3
"""
Simulation Time Node - Understanding use_sim_time
==================================================

LEARNING OBJECTIVES:
--------------------
1. Difference between wall time and simulation time
2. The /clock topic
3. The use_sim_time parameter

SIMULATION TIME CONCEPT:
------------------------
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    WALL TIME vs SIMULATION TIME                         │
    │                                                                         │
    │   WALL TIME (Real Time):                                                │
    │   - Comes from your computer's clock                                    │
    │   - 1 second = 1 real second                                            │
    │   - Used by default                                                     │
    │                                                                         │
    │   SIMULATION TIME:                                                      │
    │   - Comes from /clock topic (published by Gazebo)                       │
    │   - Can run faster, slower, or paused                                   │
    │   - Enabled with: use_sim_time:=true                                    │
    │                                                                         │
    │   WHY? Simulation might run at 0.5x speed on slow computer              │
    │   Without sim_time, robot code would "miss" time!                       │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘
"""

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from builtin_interfaces.msg import Time as TimeMsg


class SimTimeNode(Node):
    """Demonstrates simulation time vs wall time."""

    def __init__(self):
        super().__init__('sim_time_demo')

        self.declare_parameter('use_sim_time', False)
        use_sim = self.get_parameter('use_sim_time').value

        self.get_logger().info('=' * 50)
        self.get_logger().info('SIMULATION TIME DEMO')
        self.get_logger().info(f'use_sim_time = {use_sim}')
        self.get_logger().info('=' * 50)

        if use_sim:
            self.get_logger().info('Using SIMULATION time (from /clock topic)')
            self.get_logger().info('If no /clock, time will not advance!')
        else:
            self.get_logger().info('Using WALL time (real time)')

        self.timer = self.create_timer(1.0, self.show_time)
        self.start_time = self.get_clock().now()

    def show_time(self):
        """Show current time."""
        now = self.get_clock().now()
        elapsed = (now - self.start_time).nanoseconds / 1e9

        self.get_logger().info(
            f'ROS Time: {now.nanoseconds / 1e9:.2f}s, '
            f'Elapsed: {elapsed:.2f}s'
        )


def main(args=None):
    rclpy.init(args=args)
    node = SimTimeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
