## D2: FAILURE, RECOVERY, AND CONTROL IN ROS2 SYSTEMS

*Purpose: Teach resilience. Show how lifecycle enables graceful degradation.*

### Must Answer
- What happens when a node fails?
- How does lifecycle enable recovery?
- What is graceful degradation?
- How do supervisors manage failures?

### Key Insight
Real systems fail. Graceful degradation is better than catastrophic collapse. Lifecycle and supervision enable robots to recover.

---

### When Nodes Fail

**Scenario: Sensor dies mid-operation**

Without lifecycle:
- Sensor node crashes
- Other nodes reading from sensor: still waiting
- Robot freezes or executes undefined behavior

With lifecycle:
- Sensor node crashes
- Supervisor detects failure
- Supervisor transitions remaining nodes to INACTIVE
- Robot enters safe state
- Operator can investigate and recover

---

### Graceful Degradation

A robot doesn't need all sensors to operate. It degrades gracefully:

**Ideal:** Cameras + lidar + IMU
**Degraded:** Cameras + lidar (lidar fails)
**More degraded:** Cameras only (both lidar and IMU fail)
**Unsafe:** No sensors (stop immediately)

Lifecycle enables this. As sensors fail, supervisor deactivates dependent nodes. Robot continues with reduced capability.

---

### Supervisor Pattern

A **supervisor node** monitors lifecycle transitions:

```
Supervisor reads node states
- Camera: ACTIVE ✓
- Lidar: ACTIVE ✓
- Motor: ACTIVE ✓

Lidar disappears (fails)

Supervisor detects: Lidar not responding
Supervisor: "Lidar failed"
Supervisor transitions Motor to INACTIVE (safe)
Supervisor transitions Planner to INACTIVE
Supervisor: "System in safe state, reduced capability"
Operator can now decide: restart lidar or continue with cameras only
```

---

### Recovery Strategies

**Strategy 1: Automatic Restart**
Supervisor detects failure → automatically restarts node

**Strategy 2: Degradation**
Supervisor detects failure → deactivates dependent nodes → continues with remaining capability

**Strategy 3: Human Intervention**
Supervisor detects failure → alerts operator → waits for instructions

---

### Real Example: Mobile Manipulator

Robot has camera, lidar, gripper, arm:

**Nominal state:**
- Camera: ACTIVE (navigation)
- Lidar: ACTIVE (obstacle detection)
- Arm: ACTIVE (manipulation)
- Gripper: ACTIVE (grasping)

**Gripper fails:**
- Supervisor deactivates gripper
- Arm transitions to INACTIVE (can't manipulate without gripper)
- Navigation (camera + lidar) continues
- Robot can navigate but not manipulate

**Lidar fails:**
- Navigation degraded (relies on camera only)
- Can still navigate with camera
- Supervisor reduces speed (safer with less sensor data)

**Both fail:**
- Only camera remains
- Supervisor: "Critical state, limited navigation"
- May trigger emergency stop

---

### Hands-On Lab & Practical Code References

To study intentional failure injection, exception propagation, and supervisor recovery:

- **Fundamentals Debugging Reference:** [`ROS2_kits_ws/src/ros2_learning_common/learning_debugging/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_debugging/README.md)
  - `learning_debugging/faulty_node.py` — Simulates runtime crashes, unhandled exceptions, and deadlocks
- **AMR Sensor Failure Breaker:** [`ros2_turtlebot_kit/src/turtlebot_demos/`](../Ros2%20learning%20kits/ros2_turtlebot_kit/README.md)
  - `turtlebot_demos/break_odom.py` — Injects systematic noise and drift into odometry to evaluate graceful degradation in EKF state estimation

#### 1. Launch the Debugging & Faulty Node Simulation
```bash
cd ROS2_kits_ws
source install/setup.bash
ros2 launch learning_debugging debug_demo.launch.py
```

#### 2. Run Failure Injection Breaker
In an AMR simulation environment:

```bash
cd ros2_turtlebot_kit
source install/setup.bash

# Run odometry breaker to simulate encoder slip/failure
ros2 run turtlebot_demos break_odom.py --ros-args -p mode:=drift

# Observe how EKF localization degrades vs total collapse
ros2 topic echo /odometry/filtered
```

---

### How This Connects Forward

Next: In Article E1 ("Why Robots Need Coordinate Frames"), you'll learn about space. Lifecycle manages execution states. Coordinate frames manage spatial relationships. Together, they enable robots to understand and operate in 3D space.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Design** a supervision strategy for a multi-component robot
2. **Predict** what happens if a sensor fails (graceful degradation path)
3. **Explain** why lifecycle is necessary for safety
4. **Identify** which nodes should be supervised vs. autonomous
5. **Reason** about recovery: "If lidar fails, the system should..."

---

*Word Count: 900*
*Reading Time: 6 minutes*
*Prerequisites: A0, A1, C1, D1*
*Next: E1*