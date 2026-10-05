## A2: THE ROS2 GRAPH: NODES, TOPICS, SERVICES, ACTIONS

*Purpose: Give learners a single mental image of ROS2. Teach how data actually flows. Ground abstract concepts in visual representation.*

### Must Answer
- What is the ROS graph?
- Why is everything a node?
- How does data actually flow through the system?
- How can you visualize a ROS2 system?

### Key Insight
The ROS2 graph is a live, inspectable network of independent agents (nodes) communicating via standardized channels (topics, services, actions). Understanding the graph is understanding ROS2.

---

### The Simplest Mental Picture

Imagine your robot as a city. Each neighborhood is a node (an independent program). The roads between neighborhoods are topics, services, and actions.

A camera node publishes images to the `/camera` topic. The obstacle detection node subscribes to `/camera`, processes images, and publishes obstacles to `/obstacles`. The path planner subscribes to `/obstacles` and publishes plans to `/motion_plan`.

That network of nodes and their connections? That's the ROS2 graph.

---

### Nodes: Independent Workers

A **node** is a single executable program. It does one thing (or a few related things).

- **Camera driver node:** Reads camera hardware, publishes images
- **Obstacle detector node:** Reads images, publishes obstacle data
- **Path planner node:** Reads obstacles, publishes safe paths
- **Motor controller node:** Reads paths, publishes motor commands

Each runs independently. Each does its job. They communicate via standardized channels.

Why break it into nodes instead of one big program?

**Reason 1: Parallelism.** Nodes run in parallel. The camera doesn't wait for the detector. The detector doesn't wait for the planner. Everything happens simultaneously.

**Reason 2: Reusability.** The camera driver node is generic—it works with any obstacle detector, any planner. Plug and play.

**Reason 3: Modularity.** A broken obstacle detector doesn't kill the entire system. Camera keeps publishing. Motor controller keeps running.

**Reason 4: Language Freedom.** One node in Python, another in C++, another in JavaScript. Doesn't matter. They all speak ROS2.

---

### How Nodes Talk: The Three Communication Channels

**Topic: Broadcast Channel**

A node publishes messages to a topic. All subscribers receive them.

```
Camera node publishes to /camera/image
  └─ Image subscriber 1 receives
  └─ Image subscriber 2 receives
  └─ Obstacle detector receives and processes
```

It's one-way (or one-to-many). The publisher doesn't know who's listening. Subscribers don't ask permission.

**Service: Telephone Call**

A node calls a service on another node. The service responds.

```
Planner calls battery service on battery node
  └─ Battery node receives call
  └─ Battery node responds with "85% charged"
  └─ Planner receives response, continues
```

It's synchronous (both parties wait). Request and response must match.

**Action: Contractor Work**

A node sends a goal to another node. The other node works on it, sends feedback, and returns results.

```
Navigator sends "go to room 5" action goal
  └─ Navigation node accepts goal
  └─ Navigation node starts moving, publishes "20% done"
  └─ Navigation node continues, publishes "50% done"
  └─ Navigation node finishes, publishes "100% done"
  └─ Navigator receives final result
```

It's asynchronous with feedback. Goal, progress updates, and result.

---

### The ROS2 Graph: Seeing the Connections

The **graph** is the visual representation of all nodes and how they're connected.

Example graph:

```
[Camera] --images--> [Obstacle Detector]
                           |
                           v
                      [Path Planner]
                           |
                           v
                    [Motor Controller] --commands--> [Motors]

[Battery Node] <--query-- [Power Monitor]

[Navigation] <--goal-- [User Interface]
```

Each arrow represents a topic, service, or action. The graph shows the entire flow of data through your robot.

**Why is this important?**

1. **Debugging.** Can't understand why obstacle detection isn't working? Check the graph. Is the camera publishing? Is the detector subscribing? Is the message type correct?

2. **Design.** Sketching the graph before writing code helps you see the overall architecture. Where are the bottlenecks? Which nodes depend on which?

3. **Scalability.** Want to add a second robot? Clone the graph (with different namespaces). Want to add logging? Plug in a logger node. The graph shows how it all connects.

4. **Communication.** Explaining your system to a teammate: "The camera publishes to `image`, detector subscribes to `image` and publishes to `obstacles`..."

---

### Real Example: TurtleBot Navigation System

A simple robot that navigates autonomously:

**Nodes:**
- `lidar_driver`: Reads lidar sensor, publishes scans
- `slam_node`: Fuses lidar scans, publishes map and robot pose
- `costmap_node`: Reads map and obstacles, publishes cost data
- `planner_node`: Reads costmap, publishes trajectory
- `controller_node`: Reads trajectory, publishes velocity commands
- `motor_driver`: Reads velocity commands, drives motors

**Connections:**
```
[Lidar] → [SLAM] → [Costmap] → [Planner] → [Controller] → [Motors]
                        ↑
                        └─ [Map Server] (provides starting map)

[Costmap] --queries--> [Obstacle Detector] (when needed)

[Navigation Goal Service] <-- [User/Higher Level System]
```

**Data Flows:**
- Lidar publishes at 10 Hz (continuous)
- SLAM processes scans, publishes pose at 5 Hz
- Costmap reads pose and scans continuously, updates at 5 Hz
- Planner reads costmap changes, computes new trajectory when obstacle detected
- Controller reads trajectory, publishes velocity at 30 Hz
- Motors receive velocity commands, move

If any node fails:
- Lidar dies? SLAM stops updating. Robot stops (safely).
- Planner dies? Controller has old trajectory. Robot might hit obstacles (bad, but recoverable).
- Motor driver dies? Robot can't move (obviously).

Each point of failure has different consequences. Good system design thinks through these.

---

### Visualizing the Graph with Tools

ROS2 provides tools to visualize your graph:

**`rqt_graph`:** Shows all nodes and connections visually.

You don't need to draw it manually. ROS2 introspects the system and shows you the graph in real-time.

```
Launch your robot:
$ ros2 launch my_robot navigation.launch.py

In another terminal:
$ rqt_graph

(A window opens showing all nodes, topics, services)
```

This is how you debug. "Why isn't my detector getting camera images? Let me check the graph."

---

### Naming Conventions: Keeping the Graph Readable

Nodes, topics, and services have names. Good naming keeps your graph readable.

**Node names:** `camera_driver`, `obstacle_detector`, `path_planner` (descriptive, underscored)

**Topic names:** `/camera/image`, `/obstacles`, `/motor/velocity` (hierarchical, forward slashes, descriptive)

**Service names:** `get_battery_level`, `set_max_speed`, `reset_map` (verb_noun or get_noun format)

**Action names:** `navigate_to_pose`, `pick_and_place` (descriptive, underscored)

The graph uses these names. Clear names = clear graph = easy debugging.

Bad naming:
```
[node1] --ch1--> [node2] --ch2--> [node3]
```

What does this do? No idea.

Good naming:
```
[camera] --images--> [detector] --obstacles--> [planner]
```

What does this do? Clear.

---

### The Graph Evolves (Dynamic Graph)

The ROS2 graph is not static. Nodes can start and stop. New connections appear and disappear.

Why?

1. **Flexibility.** Start with just a camera and motor. Later, add a planner. No restart needed. The graph adapts.

2. **Redundancy.** Two obstacle detectors running? Both subscribe to camera. The graph shows both. If one fails, the other continues.

3. **Debugging.** Record the robot's behavior, then replay it with a modified detector. Plug and play.

---

### Common Graph Patterns

**Pattern 1: Linear Pipeline**

```
[Sensor] → [Processor] → [Decision] → [Actuator]
```

Simple. Data flows in one direction. Common for straightforward robots.

**Pattern 2: Hub and Spoke**

```
        [Planner]
         /   \
        /     \
   [Sensor] [Actuator]
        \     /
         \   /
        [Integrator]
```

One central node (integrator) coordinates multiple sensors and actuators. More complex, more powerful.

**Pattern 3: Parallel Processing**

```
        ┌─→ [Detector 1]
[Source]┼─→ [Detector 2] ─→ [Aggregator]
        └─→ [Detector 3]
```

Multiple nodes process simultaneously. Useful for parallel tasks (image processing, sensor fusion).

---

### Hands-On Lab & Practical Code References

To explore graph introspection and visualize computational connections in real-time:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_core/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_core/README.md)
- **Source Code to Inspect:** `learning_core/graph_introspector_node.py`
- **Launch Orchestration:** `launch/introspect.launch.py`

#### 1. Launch the Multi-Node Graph
```bash
cd ROS2_kits_ws
source install/setup.bash
ros2 launch learning_core introspect.launch.py
```

#### 2. Visualize and Query the Computational Graph
In a separate terminal:

```bash
# 1. Open the interactive graph visualizer
rqt_graph

# 2. Query node connectivity via CLI
ros2 node info /graph_introspector_node

# 3. Inspect topic endpoints and subscriber counts
ros2 topic list -v
```

---

### How This Connects Forward

Next: In Article A3 ("Workspaces, Packages, Builds"), you'll learn how to organize code so the graph works. Where do nodes live? How does the build system know to include them? Why does sourcing change everything?

---

### Learning Outcome Test

After reading this article, you should be able to:

1. **Sketch** a graph for any robot system (sensor → processor → actuator)
2. **Identify** nodes, topics, services, and actions in a diagram
3. **Explain** what happens if one node dies (and how the system degrades)
4. **Read** a real ROS2 graph output from `rqt_graph`
5. **Describe** the data flow: "Lidar publishes scans, SLAM subscribes and publishes pose, planner subscribes to pose..."

If you can do these, you understand ROS2's architecture.

---

*Word Count: 2,100*
*Reading Time: 13 minutes*
*Prerequisites: A0, A1, B4a*
*Next: A3*