#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from cex_pkg.action import MoveTurtle
from turtlesim.msg import Pose


class MoveTurtleClient(Node):
    """Action client to move the turtle using MoveTurtle action."""

    def __init__(self) -> None:
        super().__init__('move_turtle_client')

        # Action client
        self._action_client = ActionClient(self, MoveTurtle, 'move_turtle')

        # Pose subscription
        self._pose_sub_ = self.create_subscription(
            Pose, '/turtle1/pose', self._pose_callback, 10
        )
        self._current_pose = None

    def _pose_callback(self, msg: Pose) -> None:
        self._current_pose = msg

    def send_goal(self, x: float, y: float) -> None:
        self.get_logger().info("Waiting for action server 'move_turtle'...")
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Action server not available after waiting. Exiting.")
            return

        goal_msg = MoveTurtle.Goal()
        goal_msg.x = x
        goal_msg.y = y

        self.get_logger().info(f'Sending goal: x={x}, y={y}')
        self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self._feedback_callback
        ).add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')
        goal_handle.get_result_async().add_done_callback(self._get_result_callback)

    def _feedback_callback(self, feedback_msg) -> None:
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Feedback: Distance moved = {feedback.distance_moved:.2f}')

    def _get_result_callback(self, future) -> None:
        result = future.result().result
        self.get_logger().info(f'Result: Success={result.success}, Total Distance={result.distance_moved:.2f}')
        rclpy.shutdown()


def main(args=None) -> None:
    rclpy.init(args=args)
    client = MoveTurtleClient()
    client.send_goal(2.0, 2.0)

    try:
        rclpy.spin(client)
    except KeyboardInterrupt:
        pass
    finally:
        client.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
