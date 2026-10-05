# cex_pkg (ROS2 Concepts Examples)

Educational ROS2 package demonstrating fundamental concepts including publishers, subscribers, services, actions, and custom message types.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Custom Interfaces](#custom-interfaces)
- [Scripts](#scripts)
- [Launch Files](#launch-files)
- [Usage](#usage)
- [Learning Path](#learning-path)

---

## Overview

This package provides hands-on examples for learning ROS2 fundamentals:

- **Publishers & Subscribers** - Basic message passing
- **Services** - Request-response communication
- **Actions** - Long-running tasks with feedback
- **Custom Interfaces** - Creating your own message/service/action types

### Learning Objectives

After working through this package, you will understand:
1. How to create ROS2 nodes in Python
2. Publisher-subscriber communication patterns
3. Service client-server interactions
4. Action goal-feedback-result flow
5. Defining and using custom interfaces

---

## Package Structure

```
cex_pkg/
├── action/
│   └── MoveTurtle.action        # Custom action definition
├── msg/
│   └── NumPair.msg              # Custom message (two integers)
├── srv/
│   └── AddTwoInt.srv            # Custom service (add two ints)
├── script/
│   ├── simple_publisher.py      # Basic publisher example
│   ├── simple_subscriber.py     # Basic subscriber example
│   ├── pub_two_num.py           # Publishes NumPair messages
│   ├── pub_sub.py               # Combined pub/sub demo
│   ├── add_two_int.py           # Service server
│   ├── add_two_int_client.py    # Service client
│   ├── sub_client_add.py        # Subscriber + service client
│   ├── action_server.py         # Action server
│   ├── action.py                # Action client
│   └── move_turtle.py           # Turtle movement demo
├── launch/
│   ├── simple_launch.py         # Pub/sub pair
│   ├── sub_client_launch.py     # Sub + service demo
│   └── display.launch.py        # Display launch
├── urdf/
│   ├── my_first_robot.urdf      # Simple URDF example
│   └── 05-visual.urdf           # Visual URDF example
├── CMakeLists.txt
└── package.xml
```

---

## Custom Interfaces

### NumPair.msg

A message containing two integers for arithmetic demonstrations.

```
int64 a
int64 b
```

**Usage:**
```python
from cex_pkg.msg import NumPair
msg = NumPair()
msg.a = 5
msg.b = 10
```

### AddTwoInt.srv

A service that adds two integers and returns the sum.

```
# Request
int64 a
int64 b
---
# Response
int64 sum
```

**Usage:**
```python
from cex_pkg.srv import AddTwoInt
# Client sends a=5, b=3
# Server responds sum=8
```

### MoveTurtle.action

An action for moving a turtle to a target position with progress feedback.

```
# Goal
float32 x
float32 y
---
# Result
bool success
---
# Feedback
float32 distance_moved
```

**Usage:** Send a goal position, receive distance feedback during movement, get success status when complete.

---

## Scripts

### Publishers & Subscribers

| Script | Description | Topics |
|--------|-------------|--------|
| `simple_publisher.py` | Publishes incrementing String messages | Pub: `/chatter` |
| `simple_subscriber.py` | Listens to String messages | Sub: `/chatter` |
| `pub_two_num.py` | Publishes NumPair messages | Pub: `/num_pair` |
| `pub_sub.py` | Combined publisher-subscriber | Both |

### Services

| Script | Description | Service |
|--------|-------------|---------|
| `add_two_int.py` | Server that adds two integers | `/add_two_ints` |
| `add_two_int_client.py` | Client that requests addition | `/add_two_ints` |
| `sub_client_add.py` | Subscribes to NumPair, calls service on even numbers | Sub + Client |

### Actions

| Script | Description | Action |
|--------|-------------|--------|
| `action_server.py` | MoveTurtle action server | `/move_turtle` |
| `action.py` | MoveTurtle action client | `/move_turtle` |
| `move_turtle.py` | Turtle movement demonstration | Uses turtlesim |

---

## Launch Files

### simple_launch.py

Launches a publisher-subscriber pair for basic communication demo.

```bash
ros2 launch cex_pkg simple_launch.py
```

**Nodes launched:**
- `simple_publisher` - Publishes to `/chatter`
- `simple_subscriber` - Subscribes to `/chatter`

### sub_client_launch.py

Demonstrates subscriber-service client integration with delayed startup.

```bash
ros2 launch cex_pkg sub_client_launch.py
```

**Nodes launched:**
- `pub_two_num` - Publishes NumPair messages
- `add_two_int` - Service server
- `sub_client_add` - Subscribes and calls service (3-second delay)

---

## Usage

### Basic Publisher-Subscriber

```bash
# Terminal 1: Start subscriber
ros2 run cex_pkg simple_subscriber.py

# Terminal 2: Start publisher
ros2 run cex_pkg simple_publisher.py

# Or use launch file
ros2 launch cex_pkg simple_launch.py
```

### Service Example

```bash
# Terminal 1: Start service server
ros2 run cex_pkg add_two_int.py

# Terminal 2: Call service
ros2 service call /add_two_ints cex_pkg/srv/AddTwoInt "{a: 5, b: 3}"
# Response: sum: 8
```

### Action Example

```bash
# Terminal 1: Start turtlesim
ros2 run turtlesim turtlesim_node

# Terminal 2: Start action server
ros2 run cex_pkg action_server.py

# Terminal 3: Send goal
ros2 run cex_pkg action.py
```

### Integrated Demo

```bash
# Launch the full service integration demo
ros2 launch cex_pkg sub_client_launch.py

# Watch the service being called when even numbers are published
```

---

## Learning Path

### Level 1: Publishers & Subscribers
1. Run `simple_launch.py` and observe message flow
2. Modify `simple_publisher.py` to change message content
3. Create your own subscriber that processes messages differently

### Level 2: Custom Messages
1. Study `NumPair.msg` definition
2. Run `pub_two_num.py` and echo the topic
3. Create a new message type with three fields

### Level 3: Services
1. Run `add_two_int.py` and call it manually
2. Study `sub_client_add.py` for integrated patterns
3. Create a service that multiplies numbers

### Level 4: Actions
1. Run the action example with turtlesim
2. Observe feedback during execution
3. Implement cancellation handling

---

## Dependencies

- `rclpy` - ROS2 Python client library
- `std_msgs` - Standard messages
- `geometry_msgs` - Geometry messages
- `action_msgs` - Action support
- `turtlesim` - For turtle demos
- `rosidl_default_generators` - Interface generation

---

## Related Resources

- [ROS2 Humble Tutorials](https://docs.ros.org/en/humble/Tutorials.html)
- [Creating Custom Interfaces](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html)
