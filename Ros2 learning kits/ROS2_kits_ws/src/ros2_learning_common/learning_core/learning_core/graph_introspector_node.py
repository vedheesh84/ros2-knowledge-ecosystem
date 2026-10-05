#!/usr/bin/env python3
"""
Graph Introspector Node - Explore the ROS2 Computation Graph
=============================================================

LEARNING OBJECTIVES:
--------------------
After studying this node, you will understand:
1. What the ROS2 computation graph IS
2. How to discover nodes, topics, and services programmatically
3. How to use the ROS2 Python API for introspection
4. Why the graph is DYNAMIC (nodes come and go)

WHAT IS THE COMPUTATION GRAPH?
------------------------------
The computation graph is the NETWORK of all ROS2 entities:

    ┌─────────────────────────────────────────────────────────────────┐
    │                    COMPUTATION GRAPH                            │
    │                                                                 │
    │   ┌─────────┐          ┌─────────┐          ┌─────────┐        │
    │   │ Node A  │──topic──▶│ Topic X │◀──topic──│ Node B  │        │
    │   └─────────┘          └─────────┘          └─────────┘        │
    │        │                                          │             │
    │        │                                          │             │
    │   ┌────▼────┐                              ┌─────▼─────┐       │
    │   │Service Y│◀─────────────────────────────│ Client    │       │
    │   └─────────┘                              └───────────┘       │
    │                                                                 │
    │   Discovery happens automatically via DDS!                      │
    │                                                                 │
    └─────────────────────────────────────────────────────────────────┘

The graph is:
- DYNAMIC: Nodes can join and leave at any time
- DISTRIBUTED: No central master (unlike ROS1!)
- DISCOVERABLE: Nodes find each other automatically

WHAT THIS NODE DOES:
--------------------
This node periodically scans the ROS2 graph and reports:
- All active nodes
- All topics being published
- All services available

It publishes this information to /graph_info so you can see the graph
change over time.

USAGE:
------
    # Terminal 1: Run the introspector
    ros2 run learning_core graph_introspector_node

    # Terminal 2: Watch the output
    ros2 topic echo /graph_info

    # Terminal 3: Start other nodes and watch them appear!
    ros2 run learning_core hello_node

TRY THIS:
---------
1. Start the introspector alone - see what's in the graph
2. Start hello_node in another terminal
3. Watch the introspector detect it!
4. Kill hello_node and watch it disappear from the graph

CHALLENGE:
----------
1. Add action discovery (currently only nodes, topics, services)
2. Add topic type information
3. Filter out ROS2 internal topics (those starting with /ros)
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class GraphIntrospectorNode(Node):
    """
    A node that explores and reports on the ROS2 computation graph.

    This node demonstrates:
    - Publishing to topics (not just subscribing!)
    - Using ROS2's introspection API
    - String formatting for readable output

    The introspection methods used here are the same ones that power
    commands like `ros2 node list` and `ros2 topic list`.
    """

    def __init__(self):
        """Initialize the graph introspector."""

        super().__init__('graph_introspector')

        # =====================================================================
        # Log startup
        # =====================================================================
        self.get_logger().info('Graph Introspector Node starting...')
        self.get_logger().info('I will scan the ROS2 graph every 3 seconds')
        self.get_logger().info('Publishing graph info to /graph_info')

        # =====================================================================
        # Create a PUBLISHER
        # =====================================================================
        # create_publisher(msg_type, topic_name, qos_depth)
        #
        # msg_type: The message type to publish (String in this case)
        # topic_name: The topic to publish on ('/graph_info')
        # qos_depth: Queue size - how many messages to buffer (10 is typical)
        #
        # PUBLISHER vs SUBSCRIBER:
        # - Publisher: SENDS messages TO a topic
        # - Subscriber: RECEIVES messages FROM a topic
        #
        # Think of a topic like a bulletin board:
        # - Publishers post messages
        # - Subscribers read messages
        # - Many publishers can post to the same board
        # - Many subscribers can read from the same board

        self.publisher = self.create_publisher(
            String,         # Message type
            '/graph_info',  # Topic name
            10              # QoS queue depth
        )

        # =====================================================================
        # Create a timer for periodic introspection
        # =====================================================================
        # We'll scan the graph every 3 seconds
        # This gives time for nodes to start/stop between scans

        self.timer = self.create_timer(3.0, self.introspect_graph)

        # Do one scan immediately at startup
        self.introspect_graph()

    def introspect_graph(self):
        """
        Scan the ROS2 graph and publish information about it.

        This method uses three key introspection functions:
        - get_node_names_and_namespaces(): List all nodes
        - get_topic_names_and_types(): List all topics
        - get_service_names_and_types(): List all services

        These are the same functions used by ros2 CLI tools!
        """

        # =====================================================================
        # Get all nodes in the graph
        # =====================================================================
        # Returns list of tuples: (node_name, namespace)
        # Example: [('hello_node', '/'), ('graph_introspector', '/')]

        nodes = self.get_node_names_and_namespaces()

        # =====================================================================
        # Get all topics in the graph
        # =====================================================================
        # Returns list of tuples: (topic_name, [types])
        # Example: [('/graph_info', ['std_msgs/msg/String'])]

        topics = self.get_topic_names_and_types()

        # =====================================================================
        # Get all services in the graph
        # =====================================================================
        # Returns list of tuples: (service_name, [types])
        # Every node automatically has some services for parameters, etc.

        services = self.get_service_names_and_types()

        # =====================================================================
        # Build a nice report
        # =====================================================================
        # We'll format this as a readable string

        lines = []
        lines.append('=' * 60)
        lines.append('ROS2 GRAPH STATUS')
        lines.append('=' * 60)

        # ----- NODES -----
        lines.append(f'\nNODES ({len(nodes)}):')
        lines.append('-' * 40)
        for name, namespace in sorted(nodes):
            # Full node name includes namespace
            full_name = f'{namespace}/{name}' if namespace != '/' else f'/{name}'
            lines.append(f'  {full_name}')

        # ----- TOPICS -----
        # Filter out some internal ROS2 topics for readability
        user_topics = [
            (name, types) for name, types in topics
            if not name.startswith('/rosout') and
               not name.startswith('/parameter_events')
        ]

        lines.append(f'\nTOPICS ({len(user_topics)} user, {len(topics)} total):')
        lines.append('-' * 40)
        for name, types in sorted(user_topics):
            type_str = types[0] if types else 'unknown'
            lines.append(f'  {name}')
            lines.append(f'    Type: {type_str}')

        # ----- SERVICES -----
        # Only show non-parameter services for readability
        user_services = [
            (name, types) for name, types in services
            if '/get_parameters' not in name and
               '/set_parameters' not in name and
               '/describe_parameters' not in name and
               '/list_parameters' not in name and
               '/get_parameter_types' not in name
        ]

        lines.append(f'\nSERVICES ({len(user_services)} user, {len(services)} total):')
        lines.append('-' * 40)
        for name, types in sorted(user_services):
            lines.append(f'  {name}')

        lines.append('\n' + '=' * 60)

        # =====================================================================
        # Publish the report
        # =====================================================================

        report = '\n'.join(lines)

        msg = String()
        msg.data = report

        self.publisher.publish(msg)

        # Also log a summary
        self.get_logger().info(
            f'Graph scan: {len(nodes)} nodes, '
            f'{len(topics)} topics, '
            f'{len(services)} services'
        )


def main(args=None):
    """Entry point for the graph introspector node."""

    rclpy.init(args=args)

    node = GraphIntrospectorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
