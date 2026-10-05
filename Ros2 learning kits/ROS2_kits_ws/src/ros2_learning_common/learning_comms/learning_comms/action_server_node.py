#!/usr/bin/env python3
"""
Action Server Node - Long-Running Tasks with Feedback
======================================================

LEARNING OBJECTIVES:
--------------------
After studying this node, you will understand:
1. What an action IS and how it differs from services
2. How to create an action server
3. How to provide feedback during execution
4. How to handle cancellation requests
5. The goal-feedback-result lifecycle

WHAT IS AN ACTION?
------------------
An action is for LONG-RUNNING TASKS with FEEDBACK:
- Client sends a GOAL (what to do)
- Server sends FEEDBACK (progress updates)
- Server sends RESULT (final outcome)
- Client can CANCEL at any time

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                         ACTION COMMUNICATION                            │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │   ┌────────────┐         Goal          ┌────────────┐                  │
    │   │            │ ─────────────────────▶│            │                  │
    │   │   Action   │                       │   Action   │                  │
    │   │   Client   │◀───── Feedback ───────│   Server   │                  │
    │   │            │◀────── Result ────────│            │                  │
    │   │            │────── Cancel ────────▶│            │                  │
    │   └────────────┘                       └────────────┘                  │
    │                                                                         │
    │   Timeline:                                                             │
    │   ──────────────────────────────────────────────────────────────▶      │
    │       │                                                    │            │
    │      Goal                Feedback     Feedback           Result         │
    │      sent                  #1           #2              received        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

WHEN TO USE ACTIONS:
--------------------
- Task takes significant time (seconds to minutes)
- You want to track progress
- You might want to cancel mid-execution
- Examples: navigation, arm movement, data download

SERVICES vs ACTIONS:
--------------------
| Aspect | Service | Action |
|--------|---------|--------|
| Duration | Quick | Long |
| Feedback | None | Yes |
| Cancellation | No | Yes |
| Blocking | Yes | Optional |

THIS ACTION:
------------
Counts from 0 to a target number, sending feedback at each count.
Simulates a long-running task with progress updates.

USAGE:
------
    # Terminal 1: Start the server
    ros2 run learning_comms action_server_node.py

    # Terminal 2: Call from CLI (limited feedback)
    ros2 action send_goal /count_to_number learning_comms/action/CountToNumber \
        "{target_number: 10, delay_between_counts: 0.5}"

    # Or use the action client node
    ros2 run learning_comms action_client_node.py
"""

import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup

# Import our custom action type
# This import works AFTER the package is built (colcon build)
from learning_comms.action import CountToNumber


class ActionServerNode(Node):
    """
    A node that provides an action server.

    This demonstrates the SERVER side of action communication.
    It accepts goals, provides feedback, and returns results.
    """

    def __init__(self):
        """Initialize the action server node."""

        super().__init__('action_server')

        self.get_logger().info('Action Server Node starting...')

        # =====================================================================
        # CREATE CALLBACK GROUP
        # =====================================================================
        # ReentrantCallbackGroup allows multiple callbacks to run simultaneously
        # This is important for actions because:
        # - We might receive a cancel request while executing
        # - We need to handle new goals while one is running

        self.callback_group = ReentrantCallbackGroup()

        # =====================================================================
        # CREATE ACTION SERVER
        # =====================================================================
        # ActionServer(node, action_type, action_name, execute_callback, ...)
        #
        # Parameters:
        #   node: The node that owns this server
        #   action_type: The action interface type
        #   action_name: The name clients use to find this action
        #   execute_callback: Called when a goal is accepted and should execute
        #   goal_callback: Called when a new goal arrives (accept/reject)
        #   cancel_callback: Called when client requests cancellation

        self.action_server = ActionServer(
            self,
            CountToNumber,
            '/count_to_number',
            self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )

        self.get_logger().info('Action server "/count_to_number" is ready')
        self.get_logger().info(
            'Call with: ros2 action send_goal /count_to_number '
            'learning_comms/action/CountToNumber '
            '"{target_number: 10, delay_between_counts: 0.5}"'
        )

    def goal_callback(self, goal_request):
        """
        Called when a new goal is received.

        Decide whether to accept or reject the goal.

        Args:
            goal_request: The goal request message

        Returns:
            GoalResponse.ACCEPT or GoalResponse.REJECT
        """

        self.get_logger().info(
            f'Received goal request: count to {goal_request.target_number}'
        )

        # Validate the goal
        if goal_request.target_number <= 0:
            self.get_logger().warn('Rejecting goal: target must be positive')
            return GoalResponse.REJECT

        if goal_request.delay_between_counts <= 0:
            self.get_logger().warn('Rejecting goal: delay must be positive')
            return GoalResponse.REJECT

        self.get_logger().info('Goal accepted!')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """
        Called when a cancellation request is received.

        Decide whether to accept the cancellation.

        Args:
            goal_handle: Handle to the goal being cancelled

        Returns:
            CancelResponse.ACCEPT or CancelResponse.REJECT
        """

        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        """
        Execute the action.

        This is the main work of the action server.
        It runs asynchronously and can be cancelled.

        Args:
            goal_handle: Handle to the current goal (for feedback/result)

        Returns:
            The result message
        """

        self.get_logger().info('Executing goal...')

        # Get goal parameters
        target = goal_handle.request.target_number
        delay = goal_handle.request.delay_between_counts

        # Create feedback and result messages
        feedback_msg = CountToNumber.Feedback()
        result = CountToNumber.Result()

        # Track timing
        start_time = time.time()

        # =====================================================================
        # MAIN EXECUTION LOOP
        # =====================================================================
        # This is where the actual work happens
        # We count from 0 to target, sending feedback at each step

        for i in range(target + 1):
            # Check for cancellation
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result.final_count = i
                result.time_taken = time.time() - start_time
                result.success = False
                result.message = f'Goal cancelled at count {i}'
                self.get_logger().info(f'Goal cancelled at count {i}')
                return result

            # Update feedback
            feedback_msg.current_count = i
            feedback_msg.percentage_complete = (i / target) * 100.0
            remaining_counts = target - i
            feedback_msg.estimated_time_remaining = remaining_counts * delay

            # Publish feedback
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(
                f'Count: {i}/{target} ({feedback_msg.percentage_complete:.1f}%)'
            )

            # Wait before next count (simulating work)
            if i < target:  # Don't delay after last count
                time.sleep(delay)

        # =====================================================================
        # GOAL SUCCEEDED
        # =====================================================================

        goal_handle.succeed()

        result.final_count = target
        result.time_taken = time.time() - start_time
        result.success = True
        result.message = f'Successfully counted to {target}'

        self.get_logger().info(
            f'Goal completed! Final count: {target}, '
            f'Time: {result.time_taken:.2f}s'
        )

        return result


def main(args=None):
    """Entry point for the action server node."""

    rclpy.init(args=args)
    node = ActionServerNode()

    # Use MultiThreadedExecutor for concurrent goal handling
    from rclpy.executors import MultiThreadedExecutor
    executor = MultiThreadedExecutor()

    try:
        rclpy.spin(node, executor)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
