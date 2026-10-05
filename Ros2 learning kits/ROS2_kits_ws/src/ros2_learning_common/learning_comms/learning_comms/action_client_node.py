#!/usr/bin/env python3
"""
Action Client Node - Sending Goals and Monitoring Progress
===========================================================

LEARNING OBJECTIVES:
--------------------
After studying this node, you will understand:
1. How to create an action client
2. How to send goals and receive feedback
3. How to handle the goal lifecycle (accepted, executing, done)
4. How to cancel a running goal

ACTION CLIENT WORKFLOW:
-----------------------
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                       ACTION CLIENT WORKFLOW                            │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │   1. WAIT FOR SERVER                                                    │
    │   ┌────────────────────────────────────────────────────────────────┐   │
    │   │ client.wait_for_server()                                        │   │
    │   └────────────────────────────────────────────────────────────────┘   │
    │                              │                                          │
    │                              ▼                                          │
    │   2. SEND GOAL                                                          │
    │   ┌────────────────────────────────────────────────────────────────┐   │
    │   │ future = client.send_goal_async(goal, feedback_callback)        │   │
    │   └────────────────────────────────────────────────────────────────┘   │
    │                              │                                          │
    │                              ▼                                          │
    │   3. GOAL ACCEPTED/REJECTED                                             │
    │   ┌────────────────────────────────────────────────────────────────┐   │
    │   │ goal_handle = future.result()                                   │   │
    │   │ if goal_handle.accepted: ...                                    │   │
    │   └────────────────────────────────────────────────────────────────┘   │
    │                              │                                          │
    │                              ▼                                          │
    │   4. RECEIVE FEEDBACK (multiple times)                                  │
    │   ┌────────────────────────────────────────────────────────────────┐   │
    │   │ feedback_callback(feedback_msg) - called for each update        │   │
    │   └────────────────────────────────────────────────────────────────┘   │
    │                              │                                          │
    │                              ▼                                          │
    │   5. GET RESULT                                                         │
    │   ┌────────────────────────────────────────────────────────────────┐   │
    │   │ result_future = goal_handle.get_result_async()                  │   │
    │   │ result = result_future.result()                                 │   │
    │   └────────────────────────────────────────────────────────────────┘   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

USAGE:
------
    # Terminal 1: Start the server FIRST
    ros2 run learning_comms action_server_node.py

    # Terminal 2: Run the client
    ros2 run learning_comms action_client_node.py
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import GoalStatus

# Import our custom action type
from learning_comms.action import CountToNumber


class ActionClientNode(Node):
    """
    A node that calls an action server.

    This demonstrates the CLIENT side of action communication.
    It sends goals, receives feedback, and handles results.
    """

    def __init__(self):
        """Initialize the action client node."""

        super().__init__('action_client')

        self.get_logger().info('Action Client Node starting...')

        # =====================================================================
        # CREATE ACTION CLIENT
        # =====================================================================
        # ActionClient(node, action_type, action_name)
        #
        # Parameters:
        #   node: The node that owns this client
        #   action_type: Must match the server's type
        #   action_name: Must match the server's name

        self.action_client = ActionClient(
            self,
            CountToNumber,
            '/count_to_number'
        )

        # =====================================================================
        # WAIT FOR ACTION SERVER
        # =====================================================================

        self.get_logger().info('Waiting for action server...')

        if not self.action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error(
                'Action server not available!\n'
                'Make sure action_server_node.py is running.'
            )
            return

        self.get_logger().info('Action server is available!')

        # Send a goal
        self.send_goal()

    def send_goal(self):
        """
        Send a goal to the action server.

        This demonstrates the full goal lifecycle:
        1. Create goal message
        2. Send goal with feedback callback
        3. Handle goal response
        4. Wait for result
        """

        # =====================================================================
        # CREATE GOAL MESSAGE
        # =====================================================================

        goal_msg = CountToNumber.Goal()
        goal_msg.target_number = 10
        goal_msg.delay_between_counts = 0.5

        self.get_logger().info(
            f'Sending goal: count to {goal_msg.target_number} '
            f'with {goal_msg.delay_between_counts}s delay'
        )

        # =====================================================================
        # SEND GOAL (ASYNC)
        # =====================================================================
        # send_goal_async() returns immediately with a Future
        # The Future resolves when the server accepts/rejects the goal
        #
        # feedback_callback is called for each feedback message

        send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # Add callback for when goal is accepted/rejected
        send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        """
        Called each time feedback is received.

        This is where you update UI, log progress, etc.

        Args:
            feedback_msg: Contains the feedback data
        """

        feedback = feedback_msg.feedback

        self.get_logger().info(
            f'Feedback: count={feedback.current_count}, '
            f'progress={feedback.percentage_complete:.1f}%, '
            f'ETA={feedback.estimated_time_remaining:.1f}s'
        )

    def goal_response_callback(self, future):
        """
        Called when the server accepts or rejects the goal.

        Args:
            future: Contains the goal handle (or rejection info)
        """

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().warn('Goal was rejected by server')
            return

        self.get_logger().info('Goal accepted by server!')

        # =====================================================================
        # GET RESULT (ASYNC)
        # =====================================================================
        # Once accepted, we wait for the result
        # get_result_async() returns a Future for the final result

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        """
        Called when the action completes (or fails).

        Args:
            future: Contains the result
        """

        result = future.result()
        status = result.status

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Goal succeeded!')
            self.get_logger().info(
                f'Result: final_count={result.result.final_count}, '
                f'time={result.result.time_taken:.2f}s, '
                f'message="{result.result.message}"'
            )
        elif status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info('Goal was cancelled')
        else:
            self.get_logger().error(f'Goal failed with status: {status}')

        # Shutdown after demo
        self.get_logger().info('Demo complete!')


def main(args=None):
    """Entry point for the action client node."""

    rclpy.init(args=args)
    node = ActionClientNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
