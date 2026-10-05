#!/usr/bin/env python3
"""
Service Client Node - Making Service Requests
==============================================

LEARNING OBJECTIVES:
--------------------
After studying this node, you will understand:
1. How to create a service client
2. How to wait for a service to be available
3. How to make synchronous and asynchronous service calls
4. Error handling for service calls

CLIENT MENTAL MODEL:
--------------------
A client is like making a phone call:
1. Check if the service exists (wait_for_service)
2. Send the request (call_async or call)
3. Wait for response (spin_until_future_complete)
4. Process the response

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                       SERVICE CLIENT WORKFLOW                           │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │   1. WAIT FOR SERVICE                                                   │
    │   ┌────────────────────────────────────────────────────────────────┐   │
    │   │ client.wait_for_service(timeout_sec=1.0)                        │   │
    │   │ Returns True if service is available, False if timeout         │   │
    │   └────────────────────────────────────────────────────────────────┘   │
    │                              │                                          │
    │                              ▼                                          │
    │   2. CREATE REQUEST                                                     │
    │   ┌────────────────────────────────────────────────────────────────┐   │
    │   │ request = ServiceType.Request()                                 │   │
    │   │ request.field = value                                           │   │
    │   └────────────────────────────────────────────────────────────────┘   │
    │                              │                                          │
    │                              ▼                                          │
    │   3. SEND REQUEST (ASYNC)                                               │
    │   ┌────────────────────────────────────────────────────────────────┐   │
    │   │ future = client.call_async(request)                             │   │
    │   │ Returns immediately with a Future object                        │   │
    │   └────────────────────────────────────────────────────────────────┘   │
    │                              │                                          │
    │                              ▼                                          │
    │   4. WAIT FOR RESPONSE                                                  │
    │   ┌────────────────────────────────────────────────────────────────┐   │
    │   │ rclpy.spin_until_future_complete(node, future)                  │   │
    │   │ Blocks until response arrives                                   │   │
    │   └────────────────────────────────────────────────────────────────┘   │
    │                              │                                          │
    │                              ▼                                          │
    │   5. GET RESPONSE                                                       │
    │   ┌────────────────────────────────────────────────────────────────┐   │
    │   │ response = future.result()                                      │   │
    │   └────────────────────────────────────────────────────────────────┘   │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

USAGE:
------
    # Terminal 1: Start the server FIRST
    ros2 run learning_comms service_server_node.py

    # Terminal 2: Run the client
    ros2 run learning_comms service_client_node.py
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool


class ServiceClientNode(Node):
    """
    A node that calls a service.

    This demonstrates the CLIENT side of service communication.
    It sends requests and waits for responses.
    """

    def __init__(self):
        """Initialize the service client node."""

        super().__init__('service_client')

        self.get_logger().info('Service Client Node starting...')

        # =====================================================================
        # CREATE A SERVICE CLIENT
        # =====================================================================
        # create_client(srv_type, service_name)
        #
        # Parameters:
        #   srv_type: Must match the server's service type
        #   service_name: Must match the server's service name

        self.client = self.create_client(SetBool, '/toggle_counter')

        # =====================================================================
        # WAIT FOR THE SERVICE TO BE AVAILABLE
        # =====================================================================
        # The server might not be running yet!
        # wait_for_service() blocks until the service is ready
        #
        # IMPORTANT: Always check if the service is available before calling

        self.get_logger().info('Waiting for /toggle_counter service...')

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn(
                'Service not available, waiting...\n'
                'Make sure service_server_node.py is running!'
            )

        self.get_logger().info('Service is available!')

        # =====================================================================
        # DEMO: TOGGLE THE COUNTER
        # =====================================================================
        # We'll make a few calls to demonstrate the pattern

        # Enable the counter
        self.get_logger().info('Enabling counter...')
        response = self.call_service(enable=True)
        self.get_logger().info(f'Response: success={response.success}, message="{response.message}"')

        # Wait a bit for counter to increment
        import time
        time.sleep(3)

        # Disable the counter
        self.get_logger().info('Disabling counter...')
        response = self.call_service(enable=False)
        self.get_logger().info(f'Response: success={response.success}, message="{response.message}"')

        self.get_logger().info('Demo complete!')

    def call_service(self, enable: bool):
        """
        Make a synchronous service call.

        This demonstrates the pattern for calling services:
        1. Create request
        2. Call async
        3. Wait for result
        4. Return response

        Args:
            enable: Whether to enable or disable the counter

        Returns:
            The service response
        """

        # =====================================================================
        # CREATE THE REQUEST
        # =====================================================================
        # Request types are named ServiceType.Request

        request = SetBool.Request()
        request.data = enable

        # =====================================================================
        # SEND THE REQUEST (ASYNC)
        # =====================================================================
        # call_async() returns immediately with a Future object
        # The Future will eventually contain the response

        future = self.client.call_async(request)

        # =====================================================================
        # WAIT FOR THE RESPONSE
        # =====================================================================
        # spin_until_future_complete() processes callbacks until
        # the future is done
        #
        # WARNING: This blocks! Use with caution in callbacks.
        # For non-blocking patterns, use add_done_callback()

        rclpy.spin_until_future_complete(self, future)

        # =====================================================================
        # GET THE RESPONSE
        # =====================================================================
        # future.result() returns the response (or raises exception)

        return future.result()


def main(args=None):
    """Entry point for the service client node."""

    rclpy.init(args=args)

    try:
        node = ServiceClientNode()
        # Node does its demo in __init__, so we just clean up
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
