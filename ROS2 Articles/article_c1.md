## C1: WHY LAUNCH FILES ARE SYSTEM DESIGN, NOT CONVENIENCE

*Purpose: Shift thinking from scripts to systems. Teach launch files as system architecture tools.*

### Must Answer
- Why don't real robots start with ros2 run?
- What do launch files actually control?
- Why is parameterization crucial?
- How do launch files enable reuse?

### Key Insight
Launch files are where you design your system. They wire together nodes, configure parameters, manage startup/shutdown. They're not convenience scripts—they're system architecture.

---

### The Problem: Launching Multiple Nodes Manually

Imagine your robot needs three nodes running:

```bash
Terminal 1: $ ros2 run camera_driver camera_driver_node
Terminal 2: $ ros2 run obstacle_detector detector_node
Terminal 3: $ ros2 run path_planner planner_node
```

Problems:
1. **Manual and error-prone** — Did you start all three? Which order?
2. **Hard to scale** — 20 nodes? Open 20 terminals? Impossible.
3. **No coordination** — Nodes don't know about each other's config
4. **Difficult to reproduce** — "How did you set up the system?" (hard to explain)
5. **No graceful shutdown** — Stop one? Others keep running. Stop main? Others orphaned.

**Solution: Launch file**

---

### What a Launch File Does

A launch file is a Python script (or YAML, or XML) that:

1. **Starts multiple nodes** with specific configurations
2. **Sets parameters** that all nodes can read
3. **Remaps topics/services** (change their names)
4. **Manages startup order** (node A before node B)
5. **Handles shutdown** (kill all nodes when main exits)
6. **Enables reuse** (same nodes, different parameters = different behavior)

Example (pseudocode):

```python
launch_description = [
  Node(package='camera_driver', executable='camera_driver_node'),
  Node(package='obstacle_detector', executable='detector_node'),
  Node(package='path_planner', executable='planner_node'),
  
  Parameter('max_speed', value=0.5),
  Parameter('is_simulation', value=False),
]

return LaunchDescription(launch_description)
```

One command launches everything:

```bash
$ ros2 launch my_robot navigation.launch.py
```

All three nodes start. All read the parameters. All coordinate via topics/services.

---

### Real Example: TurtleBot Navigation System

**navigation.launch.py:**

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import SetEnvironmentVariable

def generate_launch_description():
  return LaunchDescription([
    # Start lidar driver
    Node(package='lidar_driver', executable='lidar_node'),
    
    # Start SLAM (mapping)
    Node(package='slam_toolbox', executable='slam_node',
      parameters=[{'map_frame': 'map'}]),
    
    # Start path planner
    Node(package='path_planner', executable='planner_node',
      parameters=[
        {'max_speed': 0.5},
        {'planning_timeout': 5.0}
      ]),
    
    # Start motor controller
    Node(package='motor_driver', executable='motor_controller',
      parameters=[{'is_simulation': False}]),
  ])
```

One launch file. All nodes start with coordinated parameters. Entire system ready.

```bash
$ ros2 launch my_robot navigation.launch.py
Starting >>> lidar_driver
Starting >>> slam_node
Starting >>> planner_node
Starting >>> motor_controller
All nodes running. Press Ctrl+C to stop.
```

Press Ctrl+C? All nodes gracefully shutdown.

---

### Parameterization: The Key to Reuse

Same nodes, different parameters = different behavior.

**Real robots:**
- TurtleBot (small, slow): max_speed=0.3
- Husky (large, fast): max_speed=1.0
- Simulation: is_simulation=true, planning_timeout=10.0

**One package, three behaviors:**

```python
# TurtleBot launch
turtlebot.launch.py:
  parameters: max_speed=0.3, is_simulation=false

# Husky launch
husky.launch.py:
  parameters: max_speed=1.0, is_simulation=false

# Simulation launch
sim.launch.py:
  parameters: max_speed=0.5, is_simulation=true
```

All use the same `planner_node` package. Different parameters = different behavior. No code changes.

---

### Anti-Patterns

**Anti-Pattern 1: Hardcoded values in source code**

```cpp
// BAD
const float MAX_SPEED = 0.5;  // Hardcoded!
```

Problem: Change max_speed? Recompile. Bad.

**Anti-Pattern 2: Manual node startup scripts**

```bash
#!/bin/bash
ros2 run camera_driver camera_driver_node &
ros2 run detector detector_node &
ros2 run planner planner_node &
wait
```

Problem: No parameter coordination. No graceful shutdown. Fragile.

---

### Hands-On Lab & Practical Code References

To explore declarative launch file parameterization and conditional node execution:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_execution/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_execution/README.md)
- **Launch Files to Inspect:**
  - `launch/parameterized.launch.py` — Declares launch arguments and dynamically overrides node parameters
  - `launch/conditional.launch.py` — Uses `IfCondition` and `UnlessCondition` to toggle subsystems

#### 1. Pass Launch Arguments via Command Line
```bash
cd ROS2_kits_ws
source install/setup.bash

# Launch with customized publishing frequency
ros2 launch learning_execution parameterized.launch.py publish_frequency:=5.0
```

#### 2. Execute Conditional Subsystem Startups
```bash
# Launch only Node A, conditionally suppressing Node B
ros2 launch learning_execution conditional.launch.py enable_node_b:=false

# In another terminal, verify Node B was not spawned
ros2 node list
```

---

### How This Connects Forward

Next: In Article C2 ("Namespacing, Remapping, and Scaling Robots"), you'll learn how launch files handle multiple instances. Same node running twice with different names? Launch files make it trivial.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Explain** why manual node startup is insufficient
2. **Design** a launch file structure for any system
3. **Identify** which values should be parameters (not hardcoded)
4. **Predict** what happens if parameter is missing
5. **Reason** about reuse: "This parameter enables..."

---

*Word Count: 1,400*
*Reading Time: 9 minutes*
*Prerequisites: A0, A1, A2, A3, B1, B2, B3*
*Next: C2*