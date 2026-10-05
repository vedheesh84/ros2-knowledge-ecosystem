# learning_core

**ROS2 Mental Model & Workspace Fundamentals**

This is the first package you should study. It answers the question: *What IS ROS2, really?*

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

1. **Explain** what a ROS2 node is and why it's the fundamental unit
2. **Describe** the computation graph and how nodes connect
3. **Create** a minimal ROS2 node from scratch
4. **Use** parameters for runtime configuration
5. **Introspect** the graph using command-line tools

---

## Prerequisites

Before starting this package, ensure you have:

- [ ] ROS2 Humble installed (`ros2 --version` works)
- [ ] This workspace built (`colcon build` completed)
- [ ] Basic Python knowledge (functions, classes)
- [ ] Basic terminal skills (cd, ls, running commands)

---

## Concept Overview

### What is ROS2?

ROS2 (Robot Operating System 2) is NOT an operating system. It's a **middleware framework** that helps robot software components communicate.

Think of ROS2 as the **nervous system** of a robot:
- Different body parts (nodes) do different things
- They need to send signals to each other (messages)
- There's no central brain - it's distributed

### The Computation Graph

The computation graph is the network of all ROS2 entities at runtime.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE ROS2 COMPUTATION GRAPH                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                              ┌───────────┐                                  │
│                              │  Topic:   │                                  │
│    ┌──────────┐   publish    │ /chatter  │   subscribe   ┌──────────┐      │
│    │  Talker  │ ────────────▶│           │◀──────────────│ Listener │      │
│    │   Node   │              │ (String)  │               │   Node   │      │
│    └──────────┘              └───────────┘               └──────────┘      │
│         │                                                      │            │
│         │                                                      │            │
│         │    ┌───────────────────────────────────────────┐    │            │
│         │    │              Service:                      │    │            │
│         └────│           /add_two_ints                    │────┘            │
│              │                                            │                 │
│              │    Request ──────▶ Response                │                 │
│              └───────────────────────────────────────────┘                 │
│                                                                             │
│    Key insight: The graph is DYNAMIC - nodes come and go at any time!      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### What is a Node?

A node is:
1. **A process** - It runs as a separate program
2. **Named** - It has a unique name in the graph
3. **A container** - It holds publishers, subscribers, services, timers
4. **Discoverable** - Other nodes can find it automatically

```python
# The simplest node
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')  # <-- This name appears in the graph

rclpy.init()
node = MyNode()
rclpy.spin(node)  # <-- Keeps the node alive, processes callbacks
```

### What are Parameters?

Parameters are **runtime configuration values**. They let you change behavior WITHOUT changing code.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CONSTANTS vs PARAMETERS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CONSTANT (in code):              PARAMETER (configurable):               │
│   ┌─────────────────────┐          ┌─────────────────────┐                 │
│   │ SPEED = 1.0         │          │ ros2 param set      │                 │
│   │                     │          │   /node speed 2.0   │                 │
│   │ Change = recompile! │          │                     │                 │
│   └─────────────────────┘          │ Change = instant!   │                 │
│                                    └─────────────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Package Structure

```
learning_core/
├── package.xml                # Package manifest (dependencies, metadata)
├── setup.py                   # Python build configuration
├── setup.cfg                  # Python install configuration
├── resource/
│   └── learning_core          # Package marker file
├── README.md                  # This file!
├── learning_core/
│   ├── __init__.py            # Python package marker
│   ├── hello_node.py          # Simplest possible node
│   ├── graph_introspector_node.py  # Explore the graph
│   └── parameter_echo_node.py # Parameter demonstration
├── launch/
│   ├── hello.launch.py        # Launch hello_node
│   ├── introspect.launch.py   # Launch introspector
│   └── all_core.launch.py     # Launch all nodes
└── config/
    └── example_params.yaml    # Example parameter file
```

---

## Nodes

### hello_node

| Property | Value |
|----------|-------|
| Executable | `hello_node` |
| Purpose | The simplest possible ROS2 node |
| Complexity | Beginner |

**What it does:** Prints "Hello, ROS2!" every second using a timer.

**Why it exists:** To show the bare minimum required for a functioning node.

**Topics:** None

**Services:** None (only default parameter services)

**Parameters:** None

**Key Concepts Demonstrated:**
- `rclpy.init()` and `rclpy.spin()`
- Node class inheritance
- Timer callbacks
- Logging

---

### graph_introspector_node

| Property | Value |
|----------|-------|
| Executable | `graph_introspector_node` |
| Purpose | Explore the ROS2 computation graph |
| Complexity | Beginner |

**What it does:** Periodically scans the graph and reports all nodes, topics, and services.

**Why it exists:** To demonstrate that the graph is dynamic and discoverable.

**Topics:**

| Direction | Topic | Type | Description |
|-----------|-------|------|-------------|
| Publish | `/graph_info` | `std_msgs/String` | Current graph status report |

**Key Concepts Demonstrated:**
- Publishing to topics
- Introspection API (`get_node_names_and_namespaces()`, etc.)
- The dynamic nature of the graph

---

### parameter_echo_node

| Property | Value |
|----------|-------|
| Executable | `parameter_echo_node` |
| Purpose | Demonstrate ROS2 parameters |
| Complexity | Beginner-Intermediate |

**What it does:** Declares several parameters and echoes their values periodically. Responds to parameter changes in real-time.

**Why it exists:** To teach parameter declaration, retrieval, and callbacks.

**Topics:** None

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `greeting_message` | string | `"Hello, ROS2!"` | Message to echo |
| `echo_rate` | float | `2.0` | Echo interval in seconds |
| `demo_integer` | int | `42` | Demo integer parameter |
| `demo_bool` | bool | `true` | Demo boolean parameter |
| `demo_list` | string[] | `[...]` | Demo list parameter |

**Key Concepts Demonstrated:**
- `declare_parameter()` with defaults
- `get_parameter()` to read values
- `add_on_set_parameters_callback()` for change handling
- Loading parameters from YAML files

---

## Usage

### Quick Start

```bash
# Terminal 1: Source and run
source /opt/ros/humble/setup.bash
source /home/ved/ros2_doc/ROS2_kits_ws/install/setup.bash

ros2 run learning_core hello_node
```

```bash
# Terminal 2: See it in the graph
ros2 node list
# Output: /hello_node
```

### Running Individual Nodes

```bash
# Hello node
ros2 run learning_core hello_node

# Graph introspector
ros2 run learning_core graph_introspector_node

# Parameter echo
ros2 run learning_core parameter_echo_node
```

### Using Launch Files

```bash
# Launch hello_node
ros2 launch learning_core hello.launch.py

# Launch graph introspector
ros2 launch learning_core introspect.launch.py

# Launch all nodes (with optional arguments)
ros2 launch learning_core all_core.launch.py

# Disable specific nodes
ros2 launch learning_core all_core.launch.py launch_hello:=false
```

### Working with Parameters

```bash
# List parameters for a node
ros2 param list /parameter_echo

# Get a parameter value
ros2 param get /parameter_echo greeting_message

# Set a parameter (node must be running!)
ros2 param set /parameter_echo greeting_message "New greeting!"

# Load from YAML file
ros2 run learning_core parameter_echo_node --ros-args \
    --params-file config/example_params.yaml
```

---

## Demos

### Demo 1: See Your First Node in the Graph

**What it demonstrates:** Nodes register with ROS2 and are discoverable.

```bash
# Terminal 1
ros2 run learning_core hello_node
```

```bash
# Terminal 2
ros2 node list
# You should see: /hello_node

ros2 node info /hello_node
# Shows subscriptions, publishers, services, actions
```

**What to observe:**
1. The node name `/hello_node` appears in the list
2. It has several default services (for parameters)
3. It has no custom topics or services yet

---

### Demo 2: Watch the Graph Change

**What it demonstrates:** The graph is dynamic - nodes come and go.

```bash
# Terminal 1: Start the introspector
ros2 run learning_core graph_introspector_node
```

```bash
# Terminal 2: Watch the output
ros2 topic echo /graph_info
```

```bash
# Terminal 3: Start and stop other nodes
ros2 run learning_core hello_node
# Watch Terminal 2 - hello_node appears!

# Kill hello_node (Ctrl+C)
# Watch Terminal 2 - hello_node disappears!
```

**What to observe:**
1. The introspector sees itself in the graph
2. New nodes appear within 3 seconds
3. Stopped nodes disappear from the report

---

### Demo 3: Change Parameters at Runtime

**What it demonstrates:** Parameters can be changed without restarting the node.

```bash
# Terminal 1: Run parameter node
ros2 run learning_core parameter_echo_node
```

```bash
# Terminal 2: Change the greeting
ros2 param set /parameter_echo greeting_message "Hola, ROS2!"
# Watch Terminal 1 - the message changes!

# Change the rate
ros2 param set /parameter_echo echo_rate 0.5
# Watch Terminal 1 - faster output!
```

**What to observe:**
1. The node logs when parameters change
2. The timer is recreated with the new rate
3. Invalid values are rejected (try negative echo_rate)

---

## Challenges

### Challenge 1: Add a Counter Parameter (Difficulty: Easy)

**Objective:** Add a parameter that limits how many greetings hello_node sends.

**Starting Point:** `hello_node.py`

**Requirements:**
1. Add a parameter called `max_greetings` (int, default: 0 means unlimited)
2. Stop greeting after reaching the limit
3. Log a message when the limit is reached

**Hints:**
1. Use `self.declare_parameter('max_greetings', 0)`
2. Check the count in `timer_callback()`
3. Use `self.timer.cancel()` to stop the timer

**Success Criteria:**
- [ ] `ros2 param list /hello_node` shows `max_greetings`
- [ ] Setting `max_greetings:=5` stops after 5 greetings

---

### Challenge 2: Add Topic Publisher to Hello Node (Difficulty: Medium)

**Objective:** Make hello_node publish its greeting to a topic instead of (or in addition to) logging.

**Starting Point:** `hello_node.py`

**Requirements:**
1. Create a publisher for `/greetings` (std_msgs/String)
2. Publish the greeting message to the topic
3. Keep the logging too (publish AND log)

**Hints:**
1. See `graph_introspector_node.py` for publisher example
2. Import `from std_msgs.msg import String`
3. Create publisher in `__init__`
4. Publish in `timer_callback`

**Success Criteria:**
- [ ] `ros2 topic list` shows `/greetings`
- [ ] `ros2 topic echo /greetings` shows the messages

---

### Challenge 3: Build a Node Discovery Service (Difficulty: Hard)

**Objective:** Create a new node that provides a service to query the graph.

**Starting Point:** Create `graph_query_node.py`

**Requirements:**
1. Create a service `/query_nodes` (std_srvs/Trigger)
2. When called, return the number of active nodes as the message
3. Add it to `setup.py` entry points

**Hints:**
1. Study service examples in `learning_comms` package
2. Use `from std_srvs.srv import Trigger`
3. Use `self.create_service()`

**Success Criteria:**
- [ ] `ros2 service list` shows `/query_nodes`
- [ ] `ros2 service call /query_nodes std_srvs/srv/Trigger` returns node count

---

## Reflection Prompts

After completing this package, consider these questions:

### Conceptual Understanding

1. **What happens if two nodes have the same name?**
   - Run two instances of hello_node and observe what happens
   - Why does ROS2 behave this way?

2. **Why is the graph "dynamic"?**
   - What would it mean if the graph were static?
   - How does dynamic discovery help robots?

3. **Why are parameters better than constants?**
   - When would you choose a constant over a parameter?
   - What are the downsides of parameters?

### Practical Application

4. **What parameters would a mobile robot need?**
   - Think about wheel diameter, max speed, sensor offsets
   - Why are these better as parameters than code?

5. **When would you use introspection?**
   - During development? During production?
   - What problems does introspection help you solve?

### Mental Model

6. **Draw the computation graph for a simple robot:**
   - Nodes: Motor controller, camera, path planner, teleop
   - What topics connect them?
   - What services might exist?

---

## Common Mistakes

### Mistake 1: Forgetting to source the workspace

**Symptom:** `Package 'learning_core' not found`

**Cause:** ROS2 doesn't know about your workspace

**Solution:**
```bash
source /opt/ros/humble/setup.bash
source /home/ved/ros2_doc/ROS2_kits_ws/install/setup.bash
```

---

### Mistake 2: Forgetting rclpy.spin()

**Symptom:** Node starts then immediately exits

**Cause:** Without spin(), there's no event loop

**Solution:**
```python
# Wrong
rclpy.init()
node = MyNode()
rclpy.shutdown()  # Exits immediately!

# Right
rclpy.init()
node = MyNode()
rclpy.spin(node)  # Blocks until Ctrl+C
rclpy.shutdown()
```

---

### Mistake 3: Using undeclared parameters

**Symptom:** `ParameterNotDeclaredException`

**Cause:** ROS2 requires parameters to be declared before use

**Solution:**
```python
# Wrong
value = self.get_parameter('my_param').value  # Crashes!

# Right
self.declare_parameter('my_param', 'default')
value = self.get_parameter('my_param').value  # Works!
```

---

### Mistake 4: Wrong YAML format for parameters

**Symptom:** Parameters not loaded correctly

**Cause:** Missing `ros__parameters` key

**Solution:**
```yaml
# Wrong
node_name:
  param1: value1

# Right
node_name:
  ros__parameters:
    param1: value1
```

---

## Further Reading

- [ROS2 Concepts: Nodes](https://docs.ros.org/en/humble/Concepts/Basic/About-Nodes.html)
- [ROS2 Concepts: Parameters](https://docs.ros.org/en/humble/Concepts/Basic/About-Parameters.html)
- [ROS2 Tutorials: Understanding Nodes](https://docs.ros.org/en/humble/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Nodes/Understanding-ROS2-Nodes.html)

**Next Package:** [learning_comms](../learning_comms/README.md) - Topics, Services, and Actions
