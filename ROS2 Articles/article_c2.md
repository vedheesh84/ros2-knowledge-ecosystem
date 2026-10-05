## C2: NAMESPACING, REMAPPING, AND SCALING ROBOTS

*Purpose: Show how to run the same node multiple times without collision. Scale from single robot to multi-robot.*

### Must Answer
- What is a namespace and why do you need it?
- What is remapping and when do you use it?
- How do you run the same node twice?
- How do multi-robot systems work?

### Key Insight
Namespaces prevent name collisions. Remapping enables flexibility. Together, they let you scale from one robot to 100 robots without code changes.

---

### The Problem: Name Collisions

You have two robots, each with a camera node:

```
Robot 1: camera_driver_node publishes to /camera/image
Robot 2: camera_driver_node publishes to /camera/image
```

Both publish to the same topic. Messages mix. Everything breaks.

**Solution: Namespaces**

```
Robot 1: camera_driver_node publishes to /robot1/camera/image
Robot 2: camera_driver_node publishes to /robot2/camera/image
```

Same nodes. Different namespaces. No collision.

---

### Namespaces: Topic Isolation

A namespace is a prefix that groups related topics/services.

**Without namespace:**
```
/camera/image
/lidar/scan
/motor/command
```

**With namespace:**
```
/robot1/camera/image
/robot1/lidar/scan
/robot1/motor/command
```

**Multiple robots:**
```
/robot1/camera/image
/robot1/lidar/scan
/robot2/camera/image
/robot2/lidar/scan
```

Each robot publishes to its own namespace. No collision. Easy to identify which data comes from which robot.

---

### How to Use Namespaces in Launch Files

**Launch file:**

```python
def generate_launch_description():
  return LaunchDescription([
    # Robot 1 namespace
    Node(package='camera_driver', executable='camera_driver_node',
      namespace='robot1'),
    Node(package='obstacle_detector', executable='detector_node',
      namespace='robot1'),
    
    # Robot 2 namespace
    Node(package='camera_driver', executable='camera_driver_node',
      namespace='robot2'),
    Node(package='obstacle_detector', executable='detector_node',
      namespace='robot2'),
  ])
```

Two robots, same nodes, different namespaces. No collision.

---

### Remapping: Topic Flexibility

Remapping renames topics at launch time (no code change).

**Why?**
- Legacy node publishes to /old_topic_name
- New system expects /new_topic_name
- Solution: Remap /old_topic_name → /new_topic_name
- No code modification

**Example:**

```python
Node(package='camera_driver', executable='camera_driver_node',
  remappings=[
    ('/camera/image', '/front_camera/image'),
    ('/camera/info', '/front_camera/info'),
  ])
```

Same node. Different topic names. Detector subscribes to /front_camera/image? It works.

---

### Real Example: Dual-Robot System

Two TurtleBots navigating simultaneously:

```python
def generate_launch_description():
  robot1 = LaunchDescription([
    Node(package='lidar_driver', executable='lidar_node', namespace='robot1'),
    Node(package='slam', executable='slam_node', namespace='robot1'),
    Node(package='planner', executable='planner_node', namespace='robot1'),
    Node(package='motor', executable='motor_node', namespace='robot1'),
  ])
  
  robot2 = LaunchDescription([
    Node(package='lidar_driver', executable='lidar_node', namespace='robot2'),
    Node(package='slam', executable='slam_node', namespace='robot2'),
    Node(package='planner', executable='planner_node', namespace='robot2'),
    Node(package='motor', executable='motor_node', namespace='robot2'),
  ])
  
  return LaunchDescription(robot1 + robot2)
```

One launch file. Two complete robots. All isolated by namespace.

**Topics published:**
```
/robot1/lidar/scan
/robot1/slam/pose
/robot1/planner/path
/robot1/motor/command
/robot2/lidar/scan
/robot2/slam/pose
/robot2/planner/path
/robot2/motor/command
```

Each robot's data clearly identified. No interference.

---

### Scaling: From One to Many

Same pattern scales to 10, 100, or more robots:

```python
robots = []
for i in range(100):
  robot_ns = f'robot{i}'
  robots.append(Node(package='lidar_driver', namespace=robot_ns))
  robots.append(Node(package='slam', namespace=robot_ns))
  robots.append(Node(package='planner', namespace=robot_ns))
  robots.append(Node(package='motor', namespace=robot_ns))

return LaunchDescription(robots)
```

100 robots. 400 nodes. All coordinated by one launch file. All isolated by namespace.

---

### Anti-Patterns

**Anti-Pattern 1: Hardcoded topics in code**

```cpp
publisher = node->create_publisher<std_msgs::msg::Float32>("/camera/image", 10);
```

Problem: Can't remap. Must recompile for each use case.

**Anti-Pattern 2: Manual namespace management**

Manually prefixing topics in code instead of using namespace:

```cpp
// BAD
publisher = node->create_publisher<...>("/robot1_camera_image", 10);
```

Problem: Code is brittle. Hard to scale. Hard to remap.

---

### Hands-On Lab & Practical Code References

To explore namespace isolation, multi-instance instantiation, and topic remapping:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_execution/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_execution/README.md)
- **Launch Orchestration to Inspect:**
  - `launch/multi_robot.launch.py` — Uses `PushRosNamespace` and remappings for multi-robot isolation
  - `launch/remapped.launch.py` — Demonstrates connecting decoupled topics via `remappings=[('/data_in', '/data_out')]`

#### 1. Launch Multi-Robot Namespaced Instances
```bash
cd ROS2_kits_ws
source install/setup.bash

# Launch multiple namespaced node instances
ros2 launch learning_execution multi_robot.launch.py
```

#### 2. Verify Namespace Isolation via CLI
In a second terminal:

```bash
# 1. Observe namespaced nodes
ros2 node list
# Output:
# /robot_1/simple_node_a
# /robot_2/simple_node_a

# 2. Verify topic separation preventing data collisions
ros2 topic list
# Output:
# /robot_1/output_data
# /robot_2/output_data
```

---

### How This Connects Forward

Next: In Article D1 ("Why Robots Must Have States"), you'll learn lifecycle management. Namespaces are for organization. Lifecycle is for safety. Together, they enable robust multi-robot systems.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Design** a namespace structure for any multi-robot system
2. **Explain** why remapping is necessary
3. **Predict** topic names in a multi-namespace system
4. **Scale** a system from 1 robot to N robots
5. **Debug** name collision issues (identify the root cause)

---

*Word Count: 1,200*
*Reading Time: 8 minutes*
*Prerequisites: A0, A1, A2, C1*
*Next: D1*