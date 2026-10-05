#!/usr/bin/env python3
"""
Hello Node - The Simplest Possible ROS2 Node
=============================================

LEARNING OBJECTIVES:
--------------------
After studying this node, you will understand:
1. What a ROS2 node actually IS (a process with a name in the graph)
2. How rclpy.init() and rclpy.spin() work together
3. Why we need timers for periodic work
4. The basic structure of every ROS2 Python node

WHAT THIS NODE DOES:
--------------------
This node does almost nothing - and that's the point! It:
- Registers itself as "hello_node" in the ROS2 graph
- Prints "Hello, ROS2!" every second using a timer
- That's it!

The simplicity is intentional. Before adding complexity, you must understand
what the bare minimum looks like.

THE MENTAL MODEL:
-----------------
A ROS2 node is:
1. A PROCESS - It runs as a separate program
2. A PARTICIPANT - It registers with the ROS2 middleware (DDS)
3. A NAME - Other nodes can discover it by name
4. A CONTAINER - It can hold publishers, subscribers, timers, services, etc.

Think of nodes like employees in an office:
- Each has a name (node name)
- Each can send memos (publish)
- Each can receive memos (subscribe)
- Each can answer questions (services)
- The office directory (ROS2 graph) knows who everyone is

WHAT IS rclpy.spin()?
---------------------
spin() is the "event loop" - it sits and waits for things to happen:
- Timer fires? Call the timer callback
- Message received? Call the subscription callback
- Service request? Call the service callback

Without spin(), your node would exit immediately!

USAGE:
------
    # Terminal 1: Run the node
    ros2 run learning_core hello_node

    # Terminal 2: See it in the graph
    ros2 node list

    # Terminal 3: Get info about it
    ros2 node info /hello_node

TRY THIS:
---------
1. Run the node and watch it print
2. Open another terminal and run: ros2 node list
3. See /hello_node in the list? That's your node!
4. Run: ros2 node info /hello_node
5. Notice it has no publishers, subscribers, or services yet

CHALLENGE:
----------
Modify this node to:
1. Change the greeting message
2. Change the timer frequency
3. Add a parameter for the greeting (see parameter_echo_node.py)
"""

# =============================================================================
# IMPORTS
# =============================================================================
# rclpy is the ROS2 Python Client Library
# It provides the Python API for ROS2

import rclpy                    # The main ROS2 Python library
from rclpy.node import Node     # The Node class we inherit from


# =============================================================================
# NODE CLASS DEFINITION
# =============================================================================

class HelloNode(Node):
    """
    The simplest possible ROS2 node.

    This class inherits from rclpy.node.Node, which provides:
    - Node naming and registration
    - Timer creation
    - Publisher/subscriber creation
    - Service creation
    - Parameter handling
    - Logging

    Every ROS2 node follows this pattern:
    1. Inherit from Node
    2. Call super().__init__('node_name') with a unique name
    3. Create timers, publishers, subscribers, etc.
    """

    def __init__(self):
        """
        Initialize the node.

        The __init__ method runs ONCE when the node is created.
        Use it to:
        - Set up the node name
        - Create timers, publishers, subscribers
        - Initialize any state variables

        IMPORTANT: super().__init__('node_name') MUST be called first!
        This registers the node with ROS2.
        """

        # =====================================================================
        # STEP 1: Initialize the parent Node class
        # =====================================================================
        # 'hello_node' is the name other nodes will see in the graph
        # This name should be:
        #   - Unique (no other node should have the same name)
        #   - Descriptive (tells you what the node does)
        #   - snake_case (ROS2 convention)

        super().__init__('hello_node')

        # =====================================================================
        # STEP 2: Log that we've started
        # =====================================================================
        # get_logger() returns this node's logger
        # .info() logs at INFO level (visible by default)
        #
        # Logging is CRITICAL for debugging. Always log:
        #   - When your node starts
        #   - Important state changes
        #   - Errors and warnings

        self.get_logger().info('Hello Node has started!')
        self.get_logger().info('I will greet you every second.')

        # =====================================================================
        # STEP 3: Create a timer
        # =====================================================================
        # Timers call a function at regular intervals
        #
        # create_timer(period_seconds, callback_function)
        #   - period_seconds: How often to call the callback (1.0 = every second)
        #   - callback_function: The function to call
        #
        # WHY TIMERS?
        # -----------
        # Without a timer, the node would have nothing to do!
        # Timers are how we create periodic behavior.
        #
        # The timer runs on a separate thread managed by ROS2.
        # When spin() is called, ROS2 watches the timer and calls
        # our callback when it fires.

        timer_period = 1.0  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # =====================================================================
        # STEP 4: Initialize any state variables
        # =====================================================================
        # Keep track of how many times we've greeted
        # This demonstrates that nodes can have state

        self.greeting_count = 0

    def timer_callback(self):
        """
        Called every time the timer fires.

        This is a CALLBACK FUNCTION. You don't call it directly!
        ROS2 calls it when the timer period elapses.

        CALLBACK PATTERN:
        -----------------
        Almost all work in ROS2 happens in callbacks:
        - Timer callback: periodic work
        - Subscription callback: when message arrives
        - Service callback: when request comes in

        Keep callbacks FAST! If your callback takes too long,
        you'll miss other events.
        """

        # Increment our counter
        self.greeting_count += 1

        # Log our greeting
        # Using f-strings for readable formatting
        self.get_logger().info(
            f'Hello, ROS2! (greeting #{self.greeting_count})'
        )


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main(args=None):
    """
    Entry point for the node.

    This function is called when you run:
        ros2 run learning_core hello_node

    The connection between 'hello_node' and this function is defined
    in setup.py's entry_points.

    STANDARD PATTERN:
    -----------------
    Every ROS2 Python node follows this pattern:
    1. rclpy.init() - Initialize ROS2
    2. Create node instance
    3. rclpy.spin() - Run the event loop
    4. Clean up on exit
    """

    # =========================================================================
    # STEP 1: Initialize ROS2
    # =========================================================================
    # rclpy.init() sets up the ROS2 Python client library
    # This MUST be called before creating any nodes
    #
    # args=None means use default ROS2 arguments
    # These can include remapping, parameters, etc.

    rclpy.init(args=args)

    # =========================================================================
    # STEP 2: Create the node
    # =========================================================================
    # This calls HelloNode.__init__(), which:
    #   - Registers the node with ROS2
    #   - Creates the timer
    #   - Logs startup messages

    node = HelloNode()

    # =========================================================================
    # STEP 3: Spin (run the event loop)
    # =========================================================================
    # spin() is a BLOCKING call - it runs forever until:
    #   - The node is destroyed
    #   - rclpy is shutdown
    #   - Ctrl+C is pressed
    #
    # While spinning, ROS2:
    #   - Watches all timers and calls their callbacks
    #   - Watches all subscriptions and calls their callbacks
    #   - Handles service requests
    #   - Manages the node's lifecycle
    #
    # IMPORTANT: Without spin(), the node would exit immediately!

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # User pressed Ctrl+C - this is expected, not an error
        pass

    # =========================================================================
    # STEP 4: Clean up
    # =========================================================================
    # Always clean up when exiting:
    #   - destroy_node() removes the node from the graph
    #   - shutdown() cleans up ROS2 resources

    node.destroy_node()
    rclpy.shutdown()


# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================
# This allows the file to be run directly: python3 hello_node.py
# However, you should use: ros2 run learning_core hello_node

if __name__ == '__main__':
    main()
