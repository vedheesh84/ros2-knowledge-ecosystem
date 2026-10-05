#!/usr/bin/env python3
"""
Robot Brain Node - State Machine Coordinator
=============================================

LEARNING OBJECTIVES:
--------------------
This capstone node demonstrates:
1. State machine design for robots
2. Coordinating multiple subsystems
3. Using topics, services together
4. Building a complete robot behavior

SYSTEM ARCHITECTURE:
--------------------
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    INTEGRATED ROBOT SYSTEM                              │
    │                                                                         │
    │   ┌──────────────┐                           ┌──────────────┐          │
    │   │    Sensor    │ ──/sensor_data──────────▶ │    Robot     │          │
    │   │    Fusion    │                           │    Brain     │          │
    │   └──────────────┘                           │  (State      │          │
    │                                              │   Machine)   │          │
    │   ┌──────────────┐                           │              │          │
    │   │   Command    │ ◀─/execute_cmd (srv)───── │              │          │
    │   │   Executor   │                           └──────────────┘          │
    │   └──────────────┘                                  │                   │
    │                                                     │                   │
    │                                           /robot_status (topic)         │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

STATES:
-------
    IDLE -> SENSING -> PROCESSING -> ACTING -> IDLE
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger
from enum import Enum


class RobotState(Enum):
    IDLE = 'IDLE'
    SENSING = 'SENSING'
    PROCESSING = 'PROCESSING'
    ACTING = 'ACTING'


class RobotBrainNode(Node):
    """Coordinates robot behavior using a state machine."""

    def __init__(self):
        super().__init__('robot_brain')
        self.get_logger().info('Robot Brain Node starting...')
        self.get_logger().info('This is the INTEGRATION capstone!')

        self.state = RobotState.IDLE
        self.last_sensor_data = None

        # Subscribe to sensor data
        self.sensor_sub = self.create_subscription(
            String, '/sensor_data', self.sensor_callback, 10
        )

        # Service client to command executor
        self.executor_client = self.create_client(Trigger, '/execute_command')

        # Publish robot status
        self.status_pub = self.create_publisher(String, '/robot_status', 10)

        # State machine timer
        self.timer = self.create_timer(1.0, self.state_machine_tick)

        self.get_logger().info(f'Initial state: {self.state.value}')

    def sensor_callback(self, msg):
        """Receive sensor data."""
        self.last_sensor_data = msg.data
        self.get_logger().info(f'Sensor data received: {msg.data[:30]}...')

    def state_machine_tick(self):
        """Main state machine logic."""

        if self.state == RobotState.IDLE:
            self.get_logger().info('State: IDLE - waiting for data')
            if self.last_sensor_data:
                self.state = RobotState.SENSING

        elif self.state == RobotState.SENSING:
            self.get_logger().info('State: SENSING - collecting data')
            self.state = RobotState.PROCESSING

        elif self.state == RobotState.PROCESSING:
            self.get_logger().info('State: PROCESSING - analyzing data')
            self.state = RobotState.ACTING

        elif self.state == RobotState.ACTING:
            self.get_logger().info('State: ACTING - executing command')
            self.call_executor()
            self.last_sensor_data = None
            self.state = RobotState.IDLE

        # Publish status
        status = String()
        status.data = f'Robot state: {self.state.value}'
        self.status_pub.publish(status)

    def call_executor(self):
        """Call the command executor service."""
        if not self.executor_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Executor service not available')
            return

        request = Trigger.Request()
        future = self.executor_client.call_async(request)
        future.add_done_callback(self.executor_callback)

    def executor_callback(self, future):
        """Handle executor response."""
        result = future.result()
        if result.success:
            self.get_logger().info(f'Execution: {result.message}')
        else:
            self.get_logger().warn(f'Execution failed: {result.message}')


def main(args=None):
    rclpy.init(args=args)
    node = RobotBrainNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
