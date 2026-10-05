## G2: READING THE ROS2 GRAPH LIKE A SYSTEM ENGINEER

*Purpose: Teach system-level debugging. Identify bottlenecks, trace responsibility, find failure modes.*

### Must Answer
- How do you analyze the ROS2 graph?
- What patterns reveal bottlenecks?
- How do you trace data flow failures?
- What does graph topology tell you?

### Key Insight
The graph tells you everything. High-frequency topics bottleneck low-frequency consumers. Missing nodes reveal incomplete systems. Graph structure reveals failure modes.

---

### Reading Patterns in the Graph

**Pattern 1: Bottleneck**

```
[High-freq sensor] (100 Hz) → [Slow processor] (1 Hz) → [Consumer]
```

Problem: Sensor produces data 100x faster than processor consumes. Queue backs up. Latency increases.

Fix: Either speed up processor or throttle sensor.

**Pattern 2: Missing Node**

```
[Sensor] → [Topic] ← No subscriber!
```

Data published to empty topic. Processor not running? Node crashed?

**Pattern 3: Circular Dependency**

```
Node A → Node B → Node C → Node A
```

Deadlock risk. Nodes waiting on each other in circle.

---

### Tracing Failures in the Graph

**Scenario: Robot stops moving**

1. **Check graph:** Is motor controller node present? Yes.
2. **Check connection:** Is motor controller subscribed to command topic? Yes.
3. **Check upstream:** Is command topic being published? Use `ros2 topic echo`
4. **Check further upstream:** Is motion planner publishing? Use `ros2 topic hz`
5. **Root cause:** Motion planner crashed. Motor controller waiting for dead upstream node.

Fix: Restart planner or diagnose why it crashed.

---

### Graph Structure = System Design

**Linear pipeline (simple):**
```
Sensor → Processor → Actuator
```
Pro: Simple. Con: Single point of failure at any stage.

**Distributed processing (robust):**
```
        ┌─ Processor 1
Sensor ─┼─ Processor 2 → Aggregator → Actuator
        └─ Processor 3
```
Pro: Any single processor can fail, others continue. Con: More complex.

**Hierarchical (scalable):**
```
        [Level 2: Decision]
             ↓
[Level 1: Sensors] → [Level 1: Motors]
```
Pro: Scales to complexity. Con: More coordination overhead.

---

### Real Example: Multi-Robot System

**Good graph structure:**
```
Robot1 subsystem (isolated by namespace)
  ├─ camera
  ├─ planner
  └─ motor

Robot2 subsystem (isolated by namespace)
  ├─ camera
  ├─ planner
  └─ motor

Central coordinator (bridges robots)
  ├─ subscribes to /robot1/status
  └─ subscribes to /robot2/status
```

**Bad graph structure:**
```
All robots share same topic names
Robot1 camera → /image
Robot2 camera → /image
(All mixed up, conflicts)
```

Graph structure reveals if system is designed correctly.

---

### Hands-On Lab & Practical Code References

To diagnose graph bottlenecks, missing topics, and circular message topologies:

- **Fundamentals Graph Reference:** [`ROS2_kits_ws/src/ros2_learning_common/learning_core/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_core/README.md)
  - `learning_core/graph_introspector_node.py` — Introspects active publisher/subscriber counts and QoS compatibility
- **AMR Graph Diagnostic Reference:** [`ros2_turtlebot_kit/src/turtlebot_demos/`](../Ros2%20learning%20kits/ros2_turtlebot_kit/README.md)
  - `turtlebot_demos/break_tf.py` — Simulates TF graph disconnection and missing coordinate parent links

#### 1. Analyze Full System Graph Topology
```bash
cd "Ros2 learning kits/ros2_turtlebot_kit"
source install/setup.bash
ros2 launch turtlebot_bringup simulation.launch.py
```

#### 2. Inspect Graph Connections & Isolate Bottlenecks
In a second terminal:

```bash
# 1. Open visual computation graph with unhidden debug topics
rqt_graph

# 2. Check for missing subscribers on high-throughput topics
ros2 topic info /scan -v

# 3. Detect unadvertised service or action server endpoints
ros2 service list -t
```

#### 3. Inject Conflicting TF Transform & Diagnose Loop/Flicker
```bash
# Inject conflicting TF transform to observe graph disconnection/flicker
ros2 run turtlebot_demos break_tf --mode duplicate
```

---

### How This Connects Forward

Next: In Article H1 ("From Nodes to Systems"), you'll apply all of this to design complete systems. Graph reading is the foundation of systems thinking.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Identify** bottlenecks in a graph
2. **Trace** data flow failures to root cause
3. **Design** graph structures for specific constraints
4. **Diagnose** system problems by reading graph
5. **Reason** about robustness: "This graph fails if node X dies because..."

---

*Word Count: 900*
*Reading Time: 6 minutes*
*Prerequisites: A0, A1, A2, C1, D1, G1*
*Next: H1*