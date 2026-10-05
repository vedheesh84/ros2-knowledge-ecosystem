#!/usr/bin/env python3
"""
Listener Node - Subscribing to Topics
======================================

LEARNING OBJECTIVES:
--------------------
After studying this node, you will understand:
1. How to create a subscriber
2. How callbacks are triggered when messages arrive
3. The subscriber-publisher relationship
4. Message processing patterns

SUBSCRIBER MENTAL MODEL:
------------------------
A subscriber is like a mailbox:
- You set it up once (create_subscription)
- Messages arrive asynchronously (you don't control when)
- A callback is called for each message
- You process the message in the callback

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                         SUBSCRIBER LIFECYCLE                            │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │   1. CREATE            2. WAIT                  3. CALLBACK             │
    │   ┌──────────────┐    ┌──────────────┐         ┌──────────────┐        │
    │   │create_       │    │              │  msg    │ callback(msg)│        │
    │   │subscription()│───▶│  spin()      │────────▶│              │        │
    │   │              │    │  waiting...  │         │ process msg  │        │
    │   └──────────────┘    └──────────────┘         └──────────────┘        │
    │                             ▲                         │                 │
    │                             └─────────────────────────┘                 │
    │                                   (loop forever)                        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

KEY DIFFERENCES FROM POLLING:
-----------------------------
- Polling: "Is there a message? Is there a message? Is there a message?"
- Callbacks: "Hey, a message arrived!" (ROS2 tells you)

The callback model is more efficient and responsive.

USAGE:
------
    # Terminal 1: Run the talker (producer)
    ros2 run learning_comms talker_node.py

    # Terminal 2: Run the listener (consumer)
    ros2 run learning_comms listener_node.py

TRY THIS:
---------
1. Start listener, then talker - messages flow immediately
2. Start talker, then listener - what about old messages?
3. Run 3 listeners with 1 talker - all receive!
4. Run 3 talkers with 1 listener - receives all!
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ListenerNode(Node):
    """
    A node that subscribes to messages from a topic.

    This demonstrates the SUBSCRIBER side of topic communication.
    It receives messages from /chatter and logs them.
    """

    def __init__(self):
        """Initialize the listener node."""

        super().__init__('listener')

        self.get_logger().info('Listener Node starting...')

        # =====================================================================
        # CREATE A SUBSCRIBER
        # =====================================================================
        # create_subscription(msg_type, topic_name, callback, qos_depth)
        #
        # Parameters:
        #   msg_type: The expected message type
        #             MUST match the publisher's type!
        #
        #   topic_name: The topic to subscribe to
        #               MUST match the publisher's topic!
        #
        #   callback: Function to call when a message arrives
        #             Signature: callback(msg)
        #
        #   qos_depth: Queue size for pending callbacks
        #              If callbacks are slow, messages queue up
        #
        # IMPORTANT: The subscriber is passive!
        # - It doesn't request messages
        # - It waits for publishers to send them
        # - If no publisher exists, it just waits silently

        self.subscription = self.create_subscription(
            String,              # Message type
            '/chatter',          # Topic name (matches talker)
            self.listener_callback,  # Callback function
            10                   # QoS depth
        )

        # Track message count for statistics
        self.messages_received = 0

        self.get_logger().info('Subscribed to /chatter')
        self.get_logger().info('Waiting for messages...')

    def listener_callback(self, msg):
        """
        Called when a message arrives on the subscribed topic.

        This is the core of the subscriber pattern:
        - Function is called automatically by ROS2
        - msg parameter contains the received message
        - Process quickly to avoid blocking other callbacks

        Args:
            msg: The received message (std_msgs/String in this case)
        """

        # =====================================================================
        # PROCESS THE MESSAGE
        # =====================================================================
        # The message object has the same structure as when it was published
        # For std_msgs/String, there's one field: data

        self.messages_received += 1

        # Log what we received
        self.get_logger().info(
            f'Received #{self.messages_received}: "{msg.data}"'
        )

        # =====================================================================
        # YOU COULD DO MORE HERE
        # =====================================================================
        # In a real robot, you might:
        # - Parse sensor data
        # - Update internal state
        # - Trigger other actions
        # - Publish processed data to another topic
        #
        # KEEP CALLBACKS FAST!
        # If your callback takes too long, you'll miss messages.
        # For heavy processing, consider:
        # - Storing data and processing in a separate thread
        # - Using a timer for periodic processing
        # - Using an executor with multiple threads


def main(args=None):
    """Entry point for the listener node."""

    rclpy.init(args=args)
    node = ListenerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    # Log statistics on exit
    node.get_logger().info(f'Total messages received: {node.messages_received}')

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
