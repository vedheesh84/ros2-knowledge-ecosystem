# learning_execution

**Launch Files, Composition, and Runtime Control**

Learn how to orchestrate multi-node systems without hardcoding connections.

---

## Table of Contents

- [Learning Objectives](#learning-objectives)
- [Prerequisites](#prerequisites)
- [Concept Overview](#concept-overview)
- [Package Structure](#package-structure)
- [Nodes](#nodes)
- [Launch Files](#launch-files)
- [Usage](#usage)
- [Demos](#demos)
- [Challenges](#challenges)
- [Reflection Prompts](#reflection-prompts)
- [Common Mistakes](#common-mistakes)
- [Further Reading](#further-reading)

---

## Learning Objectives

After completing this package, you will be able to:

1. **Write** Python launch files from scratch
2. **Use** remapping to connect nodes without code changes
3. **Apply** conditional launching based on arguments
4. **Pass** parameters through launch files
5. **Understand** composition for performance optimization

---

## Prerequisites

- [ ] Completed [learning_core](../learning_core/README.md)
- [ ] Completed [learning_comms](../learning_comms/README.md)
- [ ] Can create simple publisher/subscriber nodes

---

## Concept Overview

### Why Launch Files?

Launch files are the SYSTEM DESIGN of your robot.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LAUNCH FILE MENTAL MODEL                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   WITHOUT LAUNCH FILES:                                                     │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  Terminal 1: ros2 run pkg node1                                     │  │
│   │  Terminal 2: ros2 run pkg node2 --ros-args -r /in:=/out            │  │
│   │  Terminal 3: ros2 run pkg node3 --ros-args -p param:=value         │  │
│   │  Terminal 4: ros2 run pkg node4 ...                                 │  │
│   │  ... (open 10 terminals for a real robot!)                          │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   WITH LAUNCH FILES:                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │  Terminal 1: ros2 launch my_robot robot.launch.py                   │  │
│   │              (starts everything configured correctly!)               │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Concepts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LAUNCH CONCEPTS                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. NODE ACTION                                                            │
│      Node(package, executable, name, parameters, remappings)                │
│      → Starts a node with configuration                                     │
│                                                                             │
│   2. REMAPPING                                                              │
│      remappings=[('/old_topic', '/new_topic')]                              │
│      → Change topic names without changing code                             │
│                                                                             │
│   3. PARAMETERS                                                             │
│      parameters=[{'key': 'value'}, 'file.yaml']                            │
│      → Pass configuration to nodes                                          │
│                                                                             │
│   4. LAUNCH ARGUMENTS                                                       │
│      DeclareLaunchArgument('name', default_value='x')                       │
│      → User-configurable options                                            │
│                                                                             │
│   5. CONDITIONS                                                             │
│      condition=IfCondition(LaunchConfiguration('arg'))                      │
│      → Enable/disable nodes based on arguments                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Remapping: The Key to Flexibility

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REMAPPING EXPLAINED                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   THE PROBLEM:                                                              │
│                                                                             │
│   Node A code:  pub = create_publisher('/data_out')                         │
│   Node B code:  sub = create_subscription('/data_in')                       │
│                                                                             │
│   /data_out ≠ /data_in → No connection!                                     │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────     │
│                                                                             │
│   BAD SOLUTION: Change the code                                             │
│                                                                             │
│   - Requires recompiling                                                    │
│   - Breaks other systems using these nodes                                  │
│   - Hardcodes system design into code                                       │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────     │
│                                                                             │
│   GOOD SOLUTION: Remapping                                                  │
│                                                                             │
│   Node(                                                                     │
│       ...,                                                                  │
│       remappings=[('/data_in', '/data_out')]                               │
│   )                                                                         │
│                                                                             │
│   Node B thinks it's using /data_in, but ROS2 redirects to /data_out       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Package Structure

```
learning_execution/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/learning_execution
├── README.md
├── learning_execution/
│   ├── __init__.py
│   ├── simple_node_a.py          # Publisher (for launch demos)
│   ├── simple_node_b.py          # Subscriber (for remapping demos)
│   └── composed_node.py          # Multi-node in one process
├── launch/
│   ├── separate_processes.launch.py  # Basic multi-node
│   ├── remapped.launch.py            # Topic remapping
│   ├── composed.launch.py            # Single-process composition
│   ├── conditional.launch.py         # If/Unless conditions
│   └── parameterized.launch.py       # Parameter passing
└── config/
    ├── node_a_params.yaml
    └── node_b_params.yaml
```

---

## Nodes

### simple_node_a

| Property | Value |
|----------|-------|
| Executable | `simple_node_a` |
| Purpose | Publish data for launch demos |

**Topics Published:** `/data_out` (std_msgs/String)

**Parameters:**
- `publish_rate` (float): Publishing rate in Hz
- `message_prefix` (string): Message prefix

---

### simple_node_b

| Property | Value |
|----------|-------|
| Executable | `simple_node_b` |
| Purpose | Subscribe to data for remapping demos |

**Topics Subscribed:** `/data_in` (std_msgs/String) - can be remapped!

---

### composed_node

| Property | Value |
|----------|-------|
| Executable | `composed_node` |
| Purpose | Demonstrate multi-node composition |

Creates three internal components in one process.

---

## Launch Files

| Launch File | Purpose | Key Concept |
|-------------|---------|-------------|
| `separate_processes.launch.py` | Basic multi-node | Shows nodes don't connect by default |
| `remapped.launch.py` | Topic remapping | Connects nodes via remapping |
| `composed.launch.py` | Composition | One process, multiple nodes |
| `conditional.launch.py` | Conditions | Enable/disable nodes with args |
| `parameterized.launch.py` | Parameters | Pass config to nodes |
| `multi_robot.launch.py` | Namespaces & Scaling | PushRosNamespace multi-instance isolation |

---

## Usage

### Quick Start

```bash
colcon build --packages-select learning_execution
source install/setup.bash
```

### Run Launch Files

```bash
# Basic (nodes don't connect)
ros2 launch learning_execution separate_processes.launch.py

# With remapping (nodes connect!)
ros2 launch learning_execution remapped.launch.py

# Composition demo
ros2 launch learning_execution composed.launch.py

# Conditional (customize what launches)
ros2 launch learning_execution conditional.launch.py enable_a:=false

# Parameterized
ros2 launch learning_execution parameterized.launch.py rate:=5.0
```

---

## Demos

### Demo 1: The Remapping Problem

```bash
# Terminal 1: Launch without remapping
ros2 launch learning_execution separate_processes.launch.py
```

**Observe:** Node A publishes, Node B waits... but receives nothing!

```bash
# Terminal 2: Check topics
ros2 topic list
# /data_out (from A) and Node B is waiting on /data_in
```

### Demo 2: The Remapping Solution

```bash
# Terminal 1: Launch WITH remapping
ros2 launch learning_execution remapped.launch.py
```

**Observe:** Node B receives messages from Node A!

```bash
# Terminal 2: Verify
ros2 topic echo /data_out
```

### Demo 3: Conditional Launch

```bash
# All nodes
ros2 launch learning_execution conditional.launch.py

# Only Node A
ros2 launch learning_execution conditional.launch.py enable_b:=false

# With debug
ros2 launch learning_execution conditional.launch.py debug:=true
```

---

## Challenges

### Challenge 1: Multi-Robot Namespace (Difficulty: Easy)

**Objective:** Launch two instances of Node A for different "robots".

**Requirements:**
1. Create a new launch file `multi_robot.launch.py`
2. Launch Node A twice with different namespaces (/robot1, /robot2)
3. Each should publish to its own namespaced topic

**Hints:**
- Use the `namespace` parameter in Node()
- Or use remapping: `/data_out` → `/robot1/data_out`

---

### Challenge 2: Include Other Launch Files (Difficulty: Medium)

**Objective:** Create a master launch file that includes others.

**Requirements:**
1. Create `master.launch.py`
2. Use IncludeLaunchDescription to include other launch files
3. Pass arguments through to included files

**Hints:**
```python
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
```

---

### Challenge 3: Event Handlers (Difficulty: Hard)

**Objective:** React to node lifecycle events in launch.

**Requirements:**
1. Start Node B only AFTER Node A has started
2. Log when each node starts
3. Handle node exit gracefully

**Hints:**
```python
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart, OnProcessExit
```

---

## Reflection Prompts

1. **Why is remapping better than changing topic names in code?**

2. **When would you use composition vs separate processes?**

3. **How do launch files improve robot deployment?**

4. **What's the relationship between launch files and configuration management?**

---

## Common Mistakes

### Mistake 1: Forgetting to source after building

```bash
# Wrong: Run launch after colcon build but before sourcing
ros2 launch learning_execution ...  # "Package not found!"

# Right: Source first
source install/setup.bash
ros2 launch learning_execution ...
```

### Mistake 2: Wrong parameter namespace in YAML

```yaml
# Wrong: Missing ros__parameters
node_name:
  my_param: value

# Right: Include ros__parameters
node_name:
  ros__parameters:
    my_param: value
```

---

## Further Reading

- [ROS2 Launch System](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Launch-Main.html)
- [Launch File Examples](https://docs.ros.org/en/humble/Tutorials/Intermediate/Launch/Using-ROS2-Launch-For-Large-Projects.html)

**Previous:** [learning_comms](../learning_comms/README.md)

**Next:** [learning_lifecycle](../learning_lifecycle/README.md)
