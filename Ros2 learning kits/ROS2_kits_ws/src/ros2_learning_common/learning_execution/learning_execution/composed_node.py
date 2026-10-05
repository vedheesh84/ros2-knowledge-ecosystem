#!/usr/bin/env python3
"""
Composed Node - Multiple Components in One Process
===================================================

LEARNING OBJECTIVES:
--------------------
This node demonstrates COMPOSITION - running multiple "nodes" in a single process.

WHY COMPOSITION?
----------------
Normal nodes run in separate processes:

    ┌───────────┐     ┌───────────┐
    │ Process 1 │ ─── │ Process 2 │
    │  Node A   │     │  Node B   │
    └───────────┘     └───────────┘
         ↑                  ↑
    Separate memory    Separate memory
    Network communication between them

Composed nodes run in ONE process:

    ┌─────────────────────────────┐
    │         Process 1           │
    │  ┌───────┐    ┌───────┐    │
    │  │Node A │    │Node B │    │
    │  └───────┘    └───────┘    │
    │      Shared memory          │
    └─────────────────────────────┘
         ↑
    Intra-process communication (zero-copy!)

BENEFITS OF COMPOSITION:
------------------------
1. Lower latency (no network overhead)
2. Zero-copy message passing (for same-process nodes)
3. Fewer processes to manage
4. Reduced memory usage

WHEN TO USE:
------------
- Nodes that communicate frequently
- Latency-critical pipelines
- Resource-constrained systems

WHEN NOT TO USE:
----------------
- Nodes that might crash (one crash kills all)
- Nodes from different packages (harder to compose)
- Debugging (harder to isolate issues)

USAGE:
------
    ros2 run learning_execution composed_node
"""

import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from std_msgs.msg import String


class ProducerComponent(Node):
    """A producer component that publishes data."""

    def __init__(self):
        super().__init__('producer_component')
        self.get_logger().info('Producer Component initialized')

        self.publisher = self.create_publisher(String, '/internal_data', 10)
        self.timer = self.create_timer(0.5, self.produce)
        self.count = 0

    def produce(self):
        self.count += 1
        msg = String()
        msg.data = f'Internal message #{self.count}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Produced: {msg.data}')


class ConsumerComponent(Node):
    """A consumer component that subscribes to data."""

    def __init__(self):
        super().__init__('consumer_component')
        self.get_logger().info('Consumer Component initialized')

        self.subscription = self.create_subscription(
            String,
            '/internal_data',
            self.consume,
            10
        )

    def consume(self, msg):
        self.get_logger().info(f'Consumed: {msg.data}')


class ProcessorComponent(Node):
    """A processor that both subscribes and publishes."""

    def __init__(self):
        super().__init__('processor_component')
        self.get_logger().info('Processor Component initialized')

        self.subscription = self.create_subscription(
            String,
            '/internal_data',
            self.process,
            10
        )
        self.publisher = self.create_publisher(String, '/processed_data', 10)

    def process(self, msg):
        processed = String()
        processed.data = f'[PROCESSED] {msg.data}'
        self.publisher.publish(processed)
        self.get_logger().info(f'Processed and republished: {processed.data}')


def main(args=None):
    """
    Main function demonstrating composition.

    This runs multiple nodes in a single process using one executor.
    """
    rclpy.init(args=args)

    # Create all components
    producer = ProducerComponent()
    consumer = ConsumerComponent()
    processor = ProcessorComponent()

    # Create a single executor for all components
    executor = SingleThreadedExecutor()

    # Add all nodes to the executor
    executor.add_node(producer)
    executor.add_node(consumer)
    executor.add_node(processor)

    producer.get_logger().info('=' * 50)
    producer.get_logger().info('COMPOSED NODE DEMO')
    producer.get_logger().info('Three components running in ONE process!')
    producer.get_logger().info('Watch for intra-process communication.')
    producer.get_logger().info('=' * 50)

    try:
        # Spin all nodes together
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        producer.destroy_node()
        consumer.destroy_node()
        processor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
