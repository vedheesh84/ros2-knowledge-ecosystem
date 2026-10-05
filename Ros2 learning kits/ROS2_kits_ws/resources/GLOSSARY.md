# ROS2 Glossary

A comprehensive reference of ROS2 terminology, organized alphabetically.

---

## Table of Contents

- [A](#a) | [B](#b) | [C](#c) | [D](#d) | [E](#e) | [F](#f) | [G](#g)
- [H](#h) | [I](#i) | [J](#j) | [K](#k) | [L](#l) | [M](#m) | [N](#n)
- [O](#o) | [P](#p) | [Q](#q) | [R](#r) | [S](#s) | [T](#t) | [U](#u)
- [V](#v) | [W](#w) | [X](#x) | [Y](#y) | [Z](#z)

---

## A

### Action
A communication pattern for long-running tasks that provide feedback during execution. Actions have three parts: **Goal** (request), **Feedback** (progress), and **Result** (final outcome).

```
┌────────────┐         Goal          ┌────────────┐
│   Action   │ ─────────────────────▶│   Action   │
│   Client   │                       │   Server   │
│            │◀───── Feedback ───────│            │
│            │◀────── Result ────────│            │
└────────────┘                       └────────────┘
```

**When to use:** Navigation, arm movements, any task that takes time and needs progress updates.

**See:** [learning_comms](../src/ros2_learning_common/learning_comms/README.md)

### Action Client
A ROS2 entity that sends goals to an action server and receives feedback/results.

### Action Server
A ROS2 entity that receives goals, executes them, provides feedback, and returns results.

### ament
The build system used by ROS2. There are two main types:
- **ament_cmake** - For C++ packages
- **ament_python** - For Python packages

---

## B

### Bag (rosbag2)
A file format for recording and playing back ROS2 topic data. Useful for debugging and testing.

```bash
# Record all topics
ros2 bag record -a

# Play back
ros2 bag play bagfile
```

### Build (colcon build)
The process of compiling ROS2 packages. Uses `colcon` as the build tool.

```bash
colcon build
source install/setup.bash
```

---

## C

### Callback
A function that is called when an event occurs (message received, timer fires, service requested).

```python
def callback(self, msg):
    self.get_logger().info(f'Received: {msg.data}')
```

### Callback Group
A mechanism to control how callbacks are executed. Types:
- **MutuallyExclusiveCallbackGroup** - Only one callback at a time
- **ReentrantCallbackGroup** - Multiple callbacks can run simultaneously

### Clock
ROS2's time source. Can be wall time (real time) or simulation time (from `/clock` topic).

### colcon
The command-line tool for building ROS2 workspaces.

```bash
colcon build                    # Build all packages
colcon build --packages-select pkg  # Build one package
colcon test                     # Run tests
```

### Composition
Running multiple nodes in a single process to reduce communication overhead.

**See:** [learning_execution](../src/ros2_learning_common/learning_execution/README.md)

---

## D

### DDS (Data Distribution Service)
The underlying middleware that ROS2 uses for communication. Provides discovery, serialization, and transport.

### Domain ID
A number (0-232) that isolates ROS2 communication. Nodes with different domain IDs can't see each other.

```bash
export ROS_DOMAIN_ID=42
```

---

## E

### Executor
The component that manages callback execution. Types:
- **SingleThreadedExecutor** - One callback at a time
- **MultiThreadedExecutor** - Parallel callback execution

### Entry Point
In Python packages, the mapping from an executable name to a Python function.

```python
entry_points={
    'console_scripts': [
        'my_node = my_package.my_module:main',
    ],
}
```

---

## F

### Frame
A coordinate system in 3D space. Robots typically have many frames (base, sensors, end-effector).

**See:** [learning_tf](../src/ros2_learning_common/learning_tf/README.md)

---

## G

### Graph (Computation Graph)
The network of all ROS2 nodes and their connections (topics, services, actions).

```bash
# Visualize the graph
rqt_graph
```

### Gazebo
A 3D robot simulator that integrates with ROS2.

**See:** [learning_simulation](../src/ros2_learning_common/learning_simulation/README.md)

---

## H

### Header
Message field containing timestamp and frame_id. Used for time synchronization and TF lookups.

```python
msg.header.stamp = self.get_clock().now().to_msg()
msg.header.frame_id = 'base_link'
```

### Humble
ROS2 Humble Hawksbill - A Long-Term Support (LTS) release targeting Ubuntu 22.04.

---

## I

### Interface
The formal definition of message, service, or action types. Stored in `.msg`, `.srv`, or `.action` files.

### Introspection
The ability to examine the ROS2 system at runtime.

```bash
ros2 node list      # List nodes
ros2 topic list     # List topics
ros2 service list   # List services
ros2 action list    # List actions
```

---

## J

### Joint State
Message type (`sensor_msgs/JointState`) describing robot joint positions, velocities, and efforts.

---

## K

### Kinematics
The mathematics of robot motion. Forward kinematics: joint angles → end-effector position. Inverse kinematics: position → joint angles.

---

## L

### Launch File
A Python file that describes how to start multiple nodes with their configurations.

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(package='pkg', executable='node'),
    ])
```

**See:** [learning_execution](../src/ros2_learning_common/learning_execution/README.md)

### Lifecycle Node
A node with managed state transitions (unconfigured → inactive → active → finalized).

**See:** [learning_lifecycle](../src/ros2_learning_common/learning_lifecycle/README.md)

### Logger
ROS2's logging system with levels: DEBUG, INFO, WARN, ERROR, FATAL.

```python
self.get_logger().info('Information message')
self.get_logger().warn('Warning message')
self.get_logger().error('Error message')
```

---

## M

### Message
A data structure used in topic communication. Defined in `.msg` files.

```
# Example: std_msgs/String
string data
```

### Middleware
The communication layer between nodes. ROS2 uses DDS implementations (Fast-DDS, Cyclone-DDS, etc.).

---

## N

### Namespace
A prefix for node names, topics, and services to organize and isolate components.

```bash
ros2 run my_package my_node --ros-args -r __ns:=/robot1
```

### Node
The fundamental computation unit in ROS2. A node is a process that can publish, subscribe, provide services, etc.

```python
class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
```

**See:** [learning_core](../src/ros2_learning_common/learning_core/README.md)

---

## O

### Odometry
The estimation of robot position based on wheel encoders or other sensors. Published as `nav_msgs/Odometry`.

---

## P

### Package
A directory containing ROS2 code, resources, and metadata. The unit of organization in ROS2.

```
my_package/
├── package.xml        # Metadata
├── setup.py           # Python build config
├── my_package/
│   └── my_node.py
└── launch/
    └── demo.launch.py
```

### Parameter
A runtime-configurable value for a node. Can be set at launch or changed dynamically.

```python
self.declare_parameter('my_param', 'default_value')
value = self.get_parameter('my_param').value
```

**See:** [learning_core](../src/ros2_learning_common/learning_core/README.md)

### Publisher
A node component that sends messages on a topic.

```python
self.publisher = self.create_publisher(String, '/topic', 10)
self.publisher.publish(msg)
```

---

## Q

### QoS (Quality of Service)
Settings that control message delivery reliability, history, and durability.

```python
from rclpy.qos import QoSProfile, ReliabilityPolicy

qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    depth=10
)
```

### Queue
The buffer that stores messages waiting to be processed. Controlled by QoS depth.

---

## R

### rclpy
The ROS2 Python client library.

```python
import rclpy
from rclpy.node import Node
```

### Remapping
Changing topic/service/action names at runtime without modifying code.

```bash
ros2 run my_package my_node --ros-args -r /old_topic:=/new_topic
```

### ROS_DOMAIN_ID
Environment variable that isolates ROS2 communication.

### RViz2
The 3D visualization tool for ROS2. Displays robot models, sensor data, TF frames, etc.

```bash
rviz2
```

---

## S

### Service
A synchronous request-response communication pattern.

```
┌────────────┐       Request       ┌────────────┐
│   Service  │ ──────────────────▶ │   Service  │
│   Client   │ ◀────────────────── │   Server   │
└────────────┘       Response      └────────────┘
```

**See:** [learning_comms](../src/ros2_learning_common/learning_comms/README.md)

### Simulation Time
Virtual time provided by a simulator (like Gazebo) via the `/clock` topic.

**See:** [learning_simulation](../src/ros2_learning_common/learning_simulation/README.md)

### Spin
The process of executing callbacks. `rclpy.spin(node)` runs forever; `spin_once()` runs one callback.

### Subscriber
A node component that receives messages from a topic.

```python
self.subscription = self.create_subscription(
    String, '/topic', self.callback, 10)
```

---

## T

### TF2 (Transform Library 2)
The library for tracking coordinate frames over time.

**See:** [learning_tf](../src/ros2_learning_common/learning_tf/README.md)

### Timer
A component that triggers callbacks at regular intervals.

```python
self.timer = self.create_timer(1.0, self.timer_callback)  # Every 1 second
```

### Topic
A named bus over which nodes exchange messages. Many-to-many communication.

```
┌────────┐                            ┌────────┐
│ Node A │ ─── publish ───▶ /topic ───│ Node B │
└────────┘                            └────────┘
```

**See:** [learning_comms](../src/ros2_learning_common/learning_comms/README.md)

### Transform
The position and orientation of one frame relative to another. Consists of translation (x, y, z) and rotation (quaternion).

---

## U

### Underlay
A workspace that is sourced before the current workspace. Typically `/opt/ros/humble`.

### URDF (Unified Robot Description Format)
An XML format for describing robot structure (links, joints, sensors).

### use_sim_time
A parameter that tells a node to use simulation time (`/clock`) instead of wall time.

```bash
ros2 run my_package my_node --ros-args -p use_sim_time:=true
```

---

## V

### Visibility Control
C++ macros that control symbol visibility in shared libraries.

---

## W

### Wall Time
Real, physical time (as opposed to simulation time).

### Workspace
A directory containing ROS2 packages. Standard structure:

```
my_workspace/
├── src/           # Source code
├── build/         # Build artifacts
├── install/       # Installed packages
└── log/           # Build logs
```

---

## X

### Xacro
An XML macro language for simplifying URDF files.

```xml
<xacro:macro name="my_link" params="name">
  <link name="${name}"/>
</xacro:macro>
```

---

## Y

### YAML
The configuration file format used for ROS2 parameters.

```yaml
my_node:
  ros__parameters:
    my_param: value
```

---

## Z

### Zero-Copy
A DDS feature that allows large messages to be shared between nodes in the same process without copying data.

---

## Quick Reference Commands

```bash
# Node operations
ros2 node list
ros2 node info /node_name

# Topic operations
ros2 topic list
ros2 topic echo /topic_name
ros2 topic hz /topic_name
ros2 topic pub /topic_name std_msgs/String "data: 'hello'"

# Service operations
ros2 service list
ros2 service call /service_name std_srvs/srv/Empty

# Action operations
ros2 action list
ros2 action info /action_name

# Parameter operations
ros2 param list
ros2 param get /node_name param_name
ros2 param set /node_name param_name value

# Build operations
colcon build
colcon build --packages-select package_name
source install/setup.bash

# Visualization
rqt_graph
rviz2
```

---

## See Also

- [ROS2 Official Concepts](https://docs.ros.org/en/humble/Concepts.html)
- [README.md](../README.md) - Main workspace overview
- [LEARNING_PATH.md](LEARNING_PATH.md) - Learning guide

