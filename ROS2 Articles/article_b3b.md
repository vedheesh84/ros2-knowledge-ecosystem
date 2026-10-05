## B3b: COORDINATING MULTIPLE ACTIONS IN A SYSTEM

*Purpose: Connect individual actions (B3) to systems that use multiple actions. Show orchestration patterns.*

### Must Answer
- How do you coordinate multiple action servers?
- How do actions share parameters?
- What patterns emerge in multi-action systems?
- How does a launch file orchestrate actions?

### Key Insight
Individual actions are powerful. Coordinating multiple actions creates complex behaviors. Launch files and shared parameters enable this orchestration.

---

### The Problem: One Action Is Not Enough

A robot with a single action server (e.g., "navigate") is limited:

```
Client: "Navigate to kitchen"
Navigation server: works on it
Result: Robot arrives at kitchen
```

But real robots need **sequences of actions**:

1. "Navigate to charging dock"
2. "Align with charger" (different action)
3. "Extend charging contact" (different action)
4. "Monitor charging status" (feedback loop)

Four different action servers. How do they coordinate?

---

### Pattern 1: Sequential Actions (One Then Another)

**Scenario:** Robot needs to navigate, then manipulate, then navigate away.

```
Client sends: "Navigate to object location"
Navigation server: works on it
Navigation server: sends result (success)
Client receives: task complete

Client sends: "Pick object"
Manipulation server: works on it
Manipulation server: sends result (success)
Client receives: task complete

Client sends: "Navigate to drop location"
Navigation server: works on it
Navigation server: sends result (success)
Client receives: task complete
```

The **client** orchestrates the sequence. Wait for one action to finish, then start the next.

**Advantage:** Simple. Clear causality.
**Disadvantage:** Rigid. If first action fails, sequence breaks.

---

### Pattern 2: Parallel Actions (Simultaneous)

**Scenario:** Robot picks up object AND monitors battery simultaneously.

```
Client sends: "Pick object" → Pick action server
Client sends: "Monitor battery" → Battery monitor action

Both servers work in parallel:
  Pick server: "5% done", "10% done", ...
  Battery monitor: "Battery: 85%", "Battery: 80%", ...

Pick server: "Task complete"
Battery monitor continues: "Battery: 75%", ...

Client: continues operation with object
```

Both actions running independently. Each sends progress. Client monitors both.

**Advantage:** Efficient. Multiple tasks happen simultaneously.
**Disadvantage:** Complex. Must handle both finishing or failing at different times.

---

### Pattern 3: Hierarchical Actions (Action Calls Another Action)

**Scenario:** "Navigate to dock" action internally calls alignment action.

```
Client: "Navigate to dock"
Navigation server receives goal

Navigation server internally:
  1. Calls align_with_dock action server
  2. Waits for alignment to complete
  3. Moves to dock
  4. Publishes progress: "Aligned", "Moving", "Complete"

Client receives: "Navigate complete"
```

The action server itself acts as a client to another action server.

**Advantage:** Composable. Complex behaviors from simpler building blocks.
**Disadvantage:** Adds latency. Multiple layers of async/sync.

---

### Shared Parameters: Passing Configuration

How do all action servers know the robot's max speed, or whether it's in simulation?

**Via Parameters:**

```
Server reads:
  /max_speed = 0.5 m/s
  /is_simulation = true
  /planning_timeout = 5.0 seconds

Each action server uses these params to configure behavior
```

**In launch file:**

```yaml
my_robot_launch.py:
  navigation_server:
    params:
      max_speed: 0.5
      planning_timeout: 5.0
      is_simulation: true
  
  manipulation_server:
    params:
      max_speed: 0.2  ← Different speed for gripper
      is_simulation: true
```

Both servers read parameters. They coordinate indirectly via shared config.

---

### Real Example: Mobile Manipulator Workflow

A robot that navigates to pick up objects:

```
Nodes:
  - navigation_action_server (does pathfinding)
  - manipulation_action_server (does picking)
  - battery_monitor_action_server (watches battery)
  - orchestrator_node (coordinates everything)

Workflow:
  1. Orchestrator sends "Navigate to object"
  2. Navigation works, sends progress updates
  3. When navigation finishes, orchestrator sends "Pick object"
  4. Manipulation works
  5. When picking finishes, orchestrator sends "Navigate to bin"
  6. Throughout, battery monitor sends updates
  7. If battery < 10%, orchestrator cancels all actions, sends "Return to dock"
```

Each action server does its job. The orchestrator (a regular node) decides the sequence based on feedback.

---

### Anti-Pattern: Overly Complex Orchestration

**Wrong:**

Creating one monolithic action server that does everything (navigate AND pick AND monitor in one).

This defeats the purpose of modularity. Don't do it.

**Right:**

Multiple focused action servers + lightweight orchestrator node.

---

### Hands-On Lab & Practical Code References

To see multi-action orchestration and sequential behavior execution in practice:

- **Core Fundamentals Reference:** [`ROS2_kits_ws/src/ros2_learning_common/learning_execution/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_execution/README.md)
  - `launch/composed.launch.py` — Multi-node process execution
- **Embodied Manipulation Orchestrator:** [`ros2_mobile_manipulator_kit/src/mobile_manipulator_manipulation/`](../Ros2%20learning%20kits/ros2_mobile_manipulator_kit/README.md)
  - `mobile_manipulator_manipulation/state_machine.py` — Orchestrates sequential action goals: detect object $\rightarrow$ plan arm trajectory action $\rightarrow$ close gripper action $\rightarrow$ retract arm action

#### 1. Execute Multi-Action Orchestration Demo
```bash
cd ros2_mobile_manipulator_kit
source install/setup.bash

# Run Demo 05: Static Pick and Place Action Orchestration
ros2 launch mobile_manipulator_demos demo_01_joint_control.launch.py
```

#### 2. Monitor Action Execution Transitions
In a second terminal:

```bash
# Monitor active action goals and transition states
ros2 action list
ros2 topic echo /arm_controller/follow_joint_trajectory/_action/status
```

---

### How This Connects Forward

Next: In Article C1 ("Why Launch Files Are System Design"), you'll learn how launch files set up all these action servers, configure their parameters, and wire them together. The launch file is where system-level thinking happens.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Design** a workflow using multiple actions (navigate → pick → navigate away)
2. **Identify** which pattern (sequential, parallel, hierarchical) fits each scenario
3. **Explain** how shared parameters enable coordination without hard-coding
4. **Predict** what happens if an action fails mid-sequence
5. **Reason** about cancellation: "If battery dies, orchestrator must..."

If you can design a multi-action workflow, you're ready for system-level thinking.

---

*Word Count: 1,200*
*Reading Time: 8 minutes*
*Prerequisites: A0, A1, A2, A3, B3*
*Next: C1*