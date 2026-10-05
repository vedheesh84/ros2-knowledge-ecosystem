#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from turtlesim.srv import TeleportRelative
from geometry_msgs.msg import Twist
from cex_pkg.action import MoveTurtle


class TeleportActionServer(Node):
    """Action server to teleport the turtle using MoveTurtle action."""

    def __init__(self) -> None:
        super().__init__('teleport_action_server')

        # Create action server
        self._action_server = ActionServer(
            self,
            MoveTurtle,
            'move_turtle',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )

        # Publisher (optional, if you want to send velocity commands too)
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # Service client for teleport
        self._teleport_cli = self.create_client(TeleportRelative, '/turtle1/teleport_relative')
        while not self._teleport_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for TeleportRelative service...")

        self.get_logger().info("TeleportActionServer started.")

    def goal_callback(self, goal_request) -> GoalResponse:
        self.get_logger().info(f"Received goal: x={goal_request.x}, y={goal_request.y}")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle) -> CancelResponse:
        self.get_logger().info("Cancel request received")
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.get_logger().info("Executing goal...")

        x = goal_handle.request.x
        y = goal_handle.request.y

        # Prepare service request
        req = TeleportRelative.Request()
        req.linear = x
        req.angular = y

        # Call service asynchronously
        future = self._teleport_cli.call_async(req)
        await future

        # Mark action as succeeded
        goal_handle.succeed()
        result = MoveTurtle.Result()
        result.success = True
        self.get_logger().info("Teleport executed successfully")
        return result


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TeleportActionServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
