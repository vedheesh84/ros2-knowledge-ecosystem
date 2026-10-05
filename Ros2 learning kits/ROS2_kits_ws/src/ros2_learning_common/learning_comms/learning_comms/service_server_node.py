#!/usr/bin/env python3
"""
Service Server Node - Request-Response Communication
=====================================================

LEARNING OBJECTIVES:
--------------------
After studying this node, you will understand:
1. What a service IS and how it differs from topics
2. How to create a service server
3. How to handle service requests
4. When to use services vs topics

WHAT IS A SERVICE?
------------------
A service is a REQUEST-RESPONSE pattern:
- Client sends a request and WAITS for a response
- Server receives request, processes it, sends response
- One request = one response (synchronous)

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                         SERVICE COMMUNICATION                           │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │   ┌────────────┐     Request      ┌────────────┐                       │
    │   │            │ ────────────────▶│            │                       │
    │   │   Client   │                  │   Server   │                       │
    │   │            │ ◀────────────────│            │                       │
    │   └────────────┘     Response     └────────────┘                       │
    │                                                                         │
    │   - One-to-one: Each request goes to one server                        │
    │   - Synchronous: Client blocks until response arrives                  │
    │   - Guaranteed: Response confirms the operation                        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

WHEN TO USE SERVICES:
---------------------
- Quick, discrete operations (not continuous data)
- You need confirmation that something happened
- Examples: trigger a reset, get current state, set a parameter

TOPICS vs SERVICES:
-------------------
| Aspect | Topic | Service |
|--------|-------|---------|
| Pattern | Streaming | Request-Response |
| Timing | Asynchronous | Synchronous |
| Confirmation | None | Response confirms |
| Multiple receivers | Yes | No (one server) |
| Use case | Sensor data | Commands, queries |

THIS SERVICE:
-------------
Provides a service to toggle a stateful counter on or off.
Uses standard ROS 2 interface `std_srvs/srv/SetBool`.

USAGE:
------
    # Terminal 1: Run the server
    ros2 run learning_comms service_server_node.py

    # Terminal 2: Call the service from CLI
    ros2 service call /toggle_counter std_srvs/srv/SetBool "data: true"

    # Or run the client node
    ros2 run learning_comms service_client_node.py
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool


class ServiceServerNode(Node):
    """
    A node that provides a service.

    This demonstrates the SERVER side of service communication.
    It waits for requests and sends responses.
    """

    def __init__(self):
        """Initialize the service server node."""

        super().__init__('service_server')

        self.get_logger().info('Service Server Node starting...')

        # =====================================================================
        # CREATE A SERVICE SERVER
        # =====================================================================
        # create_service(srv_type, service_name, callback)
        #
        # Parameters:
        #   srv_type: The service type (defines request and response)
        #             We use SetBool: request has 'data' (bool), response has
        #             'success' (bool) and 'message' (string)
        #
        #   service_name: The name of the service
        #                 Clients use this to find the service
        #
        #   callback: Function called when a request arrives
        #             Signature: callback(request, response) -> response
        #
        # SERVICE TYPES:
        # --------------
        # Services are defined in .srv files with two parts:
        # ---
        # separates request (above) from response (below)
        #
        # std_srvs/SetBool:
        #   bool data           # Request: true or false
        #   ---
        #   bool success        # Response: did it work?
        #   string message      # Response: human-readable message

        self.service = self.create_service(
            SetBool,                    # Service type
            '/toggle_counter',          # Service name
            self.handle_toggle_request  # Callback
        )

        # Internal state - the service can maintain state!
        self.counter_enabled = False
        self.counter_value = 0

        # Create a timer that counts when enabled
        self.timer = self.create_timer(1.0, self.timer_callback)

        self.get_logger().info('Service "/toggle_counter" is ready')
        self.get_logger().info('Call with: ros2 service call /toggle_counter std_srvs/srv/SetBool "data: true"')

    def handle_toggle_request(self, request, response):
        """
        Handle incoming service requests.

        This callback is called when a client sends a request.
        It must fill in the response and return it.

        Args:
            request: The incoming request (SetBool.Request)
                    Has a 'data' field (bool)
            response: The response to fill in (SetBool.Response)
                     Has 'success' (bool) and 'message' (string)

        Returns:
            The filled-in response object
        """

        self.get_logger().info(f'Received request: data={request.data}')

        # =====================================================================
        # PROCESS THE REQUEST
        # =====================================================================
        # The request object contains the data sent by the client
        # We process it and prepare a response

        if request.data:
            # Client wants to enable the counter
            self.counter_enabled = True
            response.success = True
            response.message = f'Counter ENABLED. Current value: {self.counter_value}'
            self.get_logger().info('Counter enabled!')
        else:
            # Client wants to disable the counter
            self.counter_enabled = False
            response.success = True
            response.message = f'Counter DISABLED. Final value: {self.counter_value}'
            self.get_logger().info('Counter disabled!')

        # =====================================================================
        # RETURN THE RESPONSE
        # =====================================================================
        # The response is sent back to the client
        # The client is WAITING for this response!

        return response

    def timer_callback(self):
        """Timer callback that counts when enabled."""
        if self.counter_enabled:
            self.counter_value += 1
            self.get_logger().info(f'Counter: {self.counter_value}')


def main(args=None):
    """Entry point for the service server node."""

    rclpy.init(args=args)
    node = ServiceServerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
