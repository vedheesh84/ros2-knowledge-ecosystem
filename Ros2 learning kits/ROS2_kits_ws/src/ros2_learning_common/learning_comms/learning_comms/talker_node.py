#!/usr/bin/env python3
"""
Talker Node - Publishing Messages to Topics
============================================

LEARNING OBJECTIVES:
--------------------
After studying this node, you will understand:
1. What a topic IS and how it works
2. How to create a publisher
3. How to publish messages at regular intervals
4. The concept of QoS (Quality of Service)

WHAT IS A TOPIC?
----------------
A topic is a named channel for streaming data. Think of it like a radio station:
- Publishers broadcast on a frequency (topic name)
- Subscribers tune in to receive broadcasts
- Many publishers can broadcast to the same topic
- Many subscribers can listen to the same topic

    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           TOPIC COMMUNICATION                           │
    ├─────────────────────────────────────────────────────────────────────────┤
    │                                                                         │
    │   Publisher A ─────┐                                                    │
    │                    │                   ┌───────▶ Subscriber X           │
    │   Publisher B ─────┼──▶ /topic_name ──┼                                 │
    │                    │                   └───────▶ Subscriber Y           │
    │   Publisher C ─────┘                                                    │
    │                                                                         │
    │   - Any-to-any: Multiple publishers, multiple subscribers              │
    │   - Asynchronous: Publishers don't wait for subscribers                │
    │   - Fire-and-forget: No confirmation of receipt                        │
    │                                                                         │
    └─────────────────────────────────────────────────────────────────────────┘

WHEN TO USE TOPICS:
-------------------
- Continuous data streams (sensor data, robot state)
- High-frequency updates (10-100+ Hz)
- When you don't need confirmation of receipt
- Examples: camera images, laser scans, odometry, cmd_vel

USAGE:
------
    # Terminal 1: Run the talker
    ros2 run learning_comms talker_node.py

    # Terminal 2: Listen to the topic
    ros2 topic echo /chatter

    # Terminal 3: Check topic info
    ros2 topic info /chatter
    ros2 topic hz /chatter

TRY THIS:
---------
1. Run multiple talker nodes - what happens?
2. Run multiple listeners - do they all receive?
3. Start listener BEFORE talker - does it work?
4. Start listener AFTER talker has been running - what happens to old messages?
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TalkerNode(Node):
    """
    A node that publishes messages to a topic.

    This demonstrates the PUBLISHER side of topic communication.
    Every second, it publishes a message to /chatter.
    """

    def __init__(self):
        """Initialize the talker node."""

        super().__init__('talker')

        self.get_logger().info('Talker Node starting...')

        # =====================================================================
        # CREATE A PUBLISHER
        # =====================================================================
        # create_publisher(msg_type, topic_name, qos_depth)
        #
        # Parameters:
        #   msg_type: The type of message to publish
        #             Must match what subscribers expect!
        #
        #   topic_name: The channel name (starts with /)
        #               Convention: lowercase, underscores, descriptive
        #
        #   qos_depth: Queue size for pending messages
        #              10 is a reasonable default
        #              Higher = more buffering, more memory
        #              Lower = less latency, may drop messages
        #
        # ABOUT QoS (Quality of Service):
        # --------------------------------
        # QoS controls message delivery guarantees:
        # - RELIABLE: Guarantee delivery (slower)
        # - BEST_EFFORT: May drop messages (faster)
        # For this simple example, we use the default (10) which is RELIABLE.

        self.publisher = self.create_publisher(
            String,      # Message type: std_msgs/String
            '/chatter',  # Topic name
            10           # QoS depth
        )

        # =====================================================================
        # CREATE A TIMER FOR PERIODIC PUBLISHING
        # =====================================================================
        # Publishers don't HAVE to use timers, but they often do.
        # You could also publish in response to events.

        self.timer_period = 1.0  # seconds
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        # Track message count
        self.message_count = 0

        self.get_logger().info('Publishing to /chatter every 1 second')
        self.get_logger().info('Run: ros2 topic echo /chatter to see messages')

    def timer_callback(self):
        """
        Called every timer period to publish a message.

        This demonstrates the standard publishing pattern:
        1. Create a message object
        2. Fill in the message fields
        3. Call publisher.publish()
        """

        # =====================================================================
        # CREATE AND FILL MESSAGE
        # =====================================================================
        # Each message type is a Python class
        # std_msgs/String has one field: data (string)

        msg = String()
        self.message_count += 1
        msg.data = f'Hello, ROS2! Message #{self.message_count}'

        # =====================================================================
        # PUBLISH THE MESSAGE
        # =====================================================================
        # This is non-blocking - it puts the message in a queue
        # The actual sending happens in the ROS2 middleware

        self.publisher.publish(msg)

        # Log what we published (helpful for debugging)
        self.get_logger().info(f'Published: "{msg.data}"')


def main(args=None):
    """Entry point for the talker node."""

    rclpy.init(args=args)
    node = TalkerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
