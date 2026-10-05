# learning_comms

**ROS2 Communication Primitives: Topics, Services, and Actions**

Master the three fundamental ways ROS2 nodes communicate with each other.

---

## Table of Contents

- [Learning Objectives](#learning-objectives)
- [Prerequisites](#prerequisites)
- [Concept Overview](#concept-overview)
- [Package Structure](#package-structure)
- [Nodes](#nodes)
- [Usage](#usage)
- [Demos](#demos)
- [Challenges](#challenges)
- [Reflection Prompts](#reflection-prompts)
- [Common Mistakes](#common-mistakes)
- [Further Reading](#further-reading)

---

## Learning Objectives

After completing this package, you will be able to:

1. **Explain** the three communication patterns (topics, services, actions)
2. **Create** publishers and subscribers for streaming data
3. **Build** service servers and clients for request-response
4. **Implement** action servers and clients for long-running tasks
5. **Choose** the right pattern for any communication need

---

## Prerequisites

Before starting this package, ensure you have:

- [ ] Completed [learning_core](../learning_core/README.md)
- [ ] Understand what a ROS2 node is
- [ ] Can run `ros2 topic list` and `ros2 node list`

---

## Concept Overview

### The Three Communication Patterns

ROS2 has exactly three ways for nodes to communicate:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ROS2 COMMUNICATION PATTERNS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. TOPICS (Many-to-Many Streaming)                                       │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │                                                                  │     │
│   │    Publisher ──┐         ┌──▶ Subscriber                         │     │
│   │    Publisher ──┼──▶ Topic ├──▶ Subscriber                        │     │
│   │    Publisher ──┘         └──▶ Subscriber                         │     │
│   │                                                                  │     │
│   │    Fire-and-forget, no confirmation, continuous data            │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│   2. SERVICES (One-to-One Request-Response)                                │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │                                                                  │     │
│   │    Client ─────Request────▶ Server                               │     │
│   │           ◀────Response────                                      │     │
│   │                                                                  │     │
│   │    Synchronous, blocking, guaranteed response                    │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│   3. ACTIONS (Long-Running with Feedback)                                  │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │                                                                  │     │
│   │    Client ─────Goal──────▶ Server                                │     │
│   │           ◀────Feedback────        (repeated)                    │     │
│   │           ◀────Result──────        (once, at end)                │     │
│   │           ─────Cancel─────▶        (optional)                    │     │
│   │                                                                  │     │
│   │    Asynchronous, cancellable, progress tracking                  │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to Use Each Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DECISION TREE                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Is this continuous/streaming data?                                        │
│       │                                                                     │
│       ├── YES ──▶ Use TOPIC                                                 │
│       │           (sensor data, cmd_vel, joint states)                      │
│       │                                                                     │
│       └── NO                                                                │
│            │                                                                │
│            ▼                                                                │
│   Does the task take significant time (> few seconds)?                      │
│       │                                                                     │
│       ├── YES ──▶ Use ACTION                                                │
│       │           (navigation, arm motion, file transfer)                   │
│       │                                                                     │
│       └── NO ──▶ Use SERVICE                                                │
│                   (get status, trigger reset, set parameter)                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Comparison Table

| Aspect | Topic | Service | Action |
|--------|-------|---------|--------|
| **Pattern** | Publish-Subscribe | Request-Response | Goal-Feedback-Result |
| **Direction** | Unidirectional | Bidirectional | Bidirectional |
| **Timing** | Asynchronous | Synchronous | Asynchronous |
| **Blocking** | Never | Client blocks | Optional |
| **Feedback** | N/A | N/A | Yes |
| **Cancellation** | N/A | N/A | Yes |
| **Confirmation** | None | Response | Result |
| **Use case** | Sensors, commands | Quick queries | Long tasks |

---

## Package Structure

```
learning_comms/
├── package.xml                    # Package manifest (ament_cmake)
├── CMakeLists.txt                 # Build configuration
├── README.md                      # This file!
├── action/
│   └── CountToNumber.action       # Custom action definition
├── learning_comms/
│   ├── __init__.py
│   ├── talker_node.py             # Topic publisher
│   ├── listener_node.py           # Topic subscriber
│   ├── service_server_node.py     # Service provider
│   ├── service_client_node.py     # Service consumer
│   ├── action_server_node.py      # Action provider
│   └── action_client_node.py      # Action consumer
├── launch/
│   ├── pubsub_demo.launch.py      # Topic demo
│   ├── service_demo.launch.py     # Service demo
│   ├── action_demo.launch.py      # Action demo
│   └── all_comms.launch.py        # All demos together
└── config/
    └── comms_params.yaml          # Configuration file
```

---

## Nodes

### talker_node

| Property | Value |
|----------|-------|
| Executable | `talker_node.py` |
| Purpose | Publish messages to a topic |
| Complexity | Beginner |

**Topics Published:**

| Topic | Type | Description |
|-------|------|-------------|
| `/chatter` | `std_msgs/String` | Numbered greeting messages |

---

### listener_node

| Property | Value |
|----------|-------|
| Executable | `listener_node.py` |
| Purpose | Subscribe to messages from a topic |
| Complexity | Beginner |

**Topics Subscribed:**

| Topic | Type | Description |
|-------|------|-------------|
| `/chatter` | `std_msgs/String` | Receives and logs messages |

---

### service_server_node

| Property | Value |
|----------|-------|
| Executable | `service_server_node.py` |
| Purpose | Provide a service that toggles a counter |
| Complexity | Beginner-Intermediate |

**Services Provided:**

| Service | Type | Description |
|---------|------|-------------|
| `/toggle_counter` | `std_srvs/SetBool` | Enable/disable counter |

---

### service_client_node

| Property | Value |
|----------|-------|
| Executable | `service_client_node.py` |
| Purpose | Call a service and demonstrate request-response |
| Complexity | Beginner-Intermediate |

---

### action_server_node

| Property | Value |
|----------|-------|
| Executable | `action_server_node.py` |
| Purpose | Provide a counting action with feedback |
| Complexity | Intermediate |

**Actions Provided:**

| Action | Type | Description |
|--------|------|-------------|
| `/count_to_number` | `learning_comms/CountToNumber` | Count with progress feedback |

---

### action_client_node

| Property | Value |
|----------|-------|
| Executable | `action_client_node.py` |
| Purpose | Send action goals and receive feedback |
| Complexity | Intermediate |

---

## Usage

### Quick Start

```bash
# Build the workspace first!
cd /home/ved/ros2_doc/ROS2_kits_ws
colcon build --packages-select learning_comms
source install/setup.bash
```

### Run Individual Demos

```bash
# Topic demo (separate terminals)
ros2 run learning_comms talker_node.py      # Terminal 1
ros2 run learning_comms listener_node.py    # Terminal 2

# Service demo (separate terminals)
ros2 run learning_comms service_server_node.py   # Terminal 1
ros2 run learning_comms service_client_node.py   # Terminal 2

# Action demo (separate terminals)
ros2 run learning_comms action_server_node.py    # Terminal 1
ros2 run learning_comms action_client_node.py    # Terminal 2
```

### Use Launch Files

```bash
# All-in-one demos
ros2 launch learning_comms pubsub_demo.launch.py
ros2 launch learning_comms service_demo.launch.py
ros2 launch learning_comms action_demo.launch.py
ros2 launch learning_comms all_comms.launch.py
```

### CLI Interaction

```bash
# Topics
ros2 topic list
ros2 topic echo /chatter
ros2 topic hz /chatter
ros2 topic pub /chatter std_msgs/String "data: 'manual message'"

# Services
ros2 service list
ros2 service call /toggle_counter std_srvs/srv/SetBool "data: true"

# Actions
ros2 action list
ros2 action send_goal /count_to_number learning_comms/action/CountToNumber \
    "{target_number: 5, delay_between_counts: 0.5}" --feedback
```

---

## Demos

### Demo 1: Topics - Streaming Data

**What it demonstrates:** Continuous data flow between publisher and subscriber.

```bash
# Terminal 1
ros2 launch learning_comms pubsub_demo.launch.py
```

**What to observe:**
1. Talker publishes "Hello, ROS2! Message #N" every second
2. Listener receives and logs each message
3. Message numbers match between sender and receiver

**Try this:**
1. Kill the listener - talker keeps publishing
2. Restart listener - it picks up where the stream is now
3. Run 3 listeners - all receive every message
4. Run 2 talkers - listener receives from both

---

### Demo 2: Services - Request-Response

**What it demonstrates:** Synchronous communication with confirmation.

```bash
# Terminal 1: Start server
ros2 run learning_comms service_server_node.py
```

```bash
# Terminal 2: Manual calls
ros2 service call /toggle_counter std_srvs/srv/SetBool "data: true"
ros2 service call /toggle_counter std_srvs/srv/SetBool "data: false"
```

**What to observe:**
1. Server starts and waits (no CPU usage)
2. Call triggers immediate response
3. Server state changes with each call
4. Response confirms success

---

### Demo 3: Actions - Long-Running Tasks

**What it demonstrates:** Progress tracking and cancellation.

```bash
# Terminal 1: Start server
ros2 run learning_comms action_server_node.py
```

```bash
# Terminal 2: Send goal with feedback
ros2 action send_goal /count_to_number learning_comms/action/CountToNumber \
    "{target_number: 10, delay_between_counts: 1.0}" --feedback
```

**What to observe:**
1. Goal is accepted
2. Feedback shows progress (0%, 10%, 20%...)
3. Result shows final count and timing
4. Try Ctrl+C during execution - goal is cancelled!

---

## Challenges

### Challenge 1: Custom Message Counter (Difficulty: Easy)

**Objective:** Modify talker to count different types of messages.

**Starting Point:** `talker_node.py`

**Requirements:**
1. Add a parameter for message prefix
2. Track and display messages per second
3. Reset counter after 100 messages

**Success Criteria:**
- [ ] Prefix can be changed via parameter
- [ ] Rate is displayed periodically

---

### Challenge 2: Calculator Service (Difficulty: Medium)

**Objective:** Create a new service that performs calculations.

**Starting Point:** Create `calculator_server.py`

**Requirements:**
1. Create a service `/calculate` (use std_srvs or custom)
2. Accept operation (add, subtract, multiply, divide)
3. Return result or error message
4. Handle division by zero

**Hints:**
1. You might want to create a custom service type
2. Or use a creative encoding with existing types

---

### Challenge 3: Cancellable Download Action (Difficulty: Hard)

**Objective:** Create an action that simulates a file download.

**Starting Point:** Create new action definition and server

**Requirements:**
1. Define `Download.action` with filename, size, progress
2. Server simulates download with configurable speed
3. Feedback shows bytes downloaded, percentage, speed
4. Support cancellation at any point
5. Handle errors (file not found, etc.)

**Success Criteria:**
- [ ] Can download "files" of various sizes
- [ ] Progress is reported accurately
- [ ] Cancellation works cleanly

---

## Reflection Prompts

After completing this package, consider these questions:

### Conceptual Understanding

1. **Why does ROS2 have THREE patterns instead of just one?**
   - What would happen if everything used topics?
   - What would happen if everything used services?
   - How does each pattern optimize for different needs?

2. **Why are topics "fire and forget"?**
   - What would change if topics required acknowledgment?
   - How does this design help with sensor data?

3. **Why can actions be cancelled but services cannot?**
   - What would it mean to "cancel" a service call?
   - How does this relate to task duration?

### Practical Application

4. **Classify these robot behaviors:**
   - Publishing wheel encoder counts → Topic/Service/Action?
   - Requesting current battery level → Topic/Service/Action?
   - Navigating to a waypoint → Topic/Service/Action?
   - Triggering emergency stop → Topic/Service/Action?
   - Streaming camera images → Topic/Service/Action?

5. **What happens if...?**
   - Publisher publishes faster than subscriber can process?
   - Service server is slow to respond?
   - Action is cancelled during a critical operation?

### Mental Model

6. **Draw a robot system communication diagram:**
   - Include: sensors, actuators, planner, UI
   - Show which connections are topics, services, actions
   - Explain your choices

---

## Common Mistakes

### Mistake 1: Using services for continuous data

**Symptom:** High latency, missed updates

**Cause:** Services block and have overhead

**Solution:** Use topics for streaming data

```python
# Wrong: Polling a service for sensor data
while True:
    response = client.call(request)
    process(response)
    time.sleep(0.01)

# Right: Subscribe to a topic
subscription = node.create_subscription(
    SensorData, '/sensor', callback, 10)
```

---

### Mistake 2: Blocking in action callbacks

**Symptom:** Feedback doesn't arrive, goals can't be cancelled

**Cause:** Long-running code blocks the executor

**Solution:** Use async execution or check for cancellation

```python
# Wrong
def execute_callback(self, goal_handle):
    time.sleep(60)  # Blocks everything!
    return result

# Right
async def execute_callback(self, goal_handle):
    for i in range(60):
        if goal_handle.is_cancel_requested:
            return cancelled_result
        await asyncio.sleep(1)
        goal_handle.publish_feedback(feedback)
    return result
```

---

### Mistake 3: Not waiting for services

**Symptom:** "Service not available" or hanging

**Cause:** Calling before server is ready

**Solution:** Always wait for service

```python
# Wrong
response = client.call(request)  # Might fail!

# Right
if client.wait_for_service(timeout_sec=5.0):
    response = client.call(request)
else:
    logger.error('Service not available')
```

---

### Mistake 4: Mismatched types

**Symptom:** "Type mismatch" errors

**Cause:** Publisher and subscriber using different message types

**Solution:** Always verify types match

```bash
# Check what type a topic uses
ros2 topic info /topic_name
```

---

## Further Reading

- [ROS2 Concepts: Topics](https://docs.ros.org/en/humble/Concepts/Basic/About-Topics.html)
- [ROS2 Concepts: Services](https://docs.ros.org/en/humble/Concepts/Basic/About-Services.html)
- [ROS2 Concepts: Actions](https://docs.ros.org/en/humble/Concepts/Basic/About-Actions.html)
- [ROS2 Tutorial: Writing a Simple Publisher/Subscriber](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Publisher-And-Subscriber.html)

**Previous Package:** [learning_core](../learning_core/README.md)

**Next Package:** [learning_execution](../learning_execution/README.md) - Launch files and composition
