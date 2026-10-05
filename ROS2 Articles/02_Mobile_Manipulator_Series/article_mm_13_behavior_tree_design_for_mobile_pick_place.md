## MM 13: BEHAVIOR TREE ARCHITECTURE FOR MOBILE PICK-AND-PLACE

*Purpose: Design production Behavior Trees for end-to-end mobile manipulation. Build complete XML/Python behavior trees coordinating Nav2 navigation, OpenCV perception, MoveIt2 planning, and dynamic fault recovery.*

### Must Answer
- How do we structure a complete Behavior Tree for an autonomous warehouse mobile pick-and-place robot?
- How does the Blackboard share data (detected 3D coordinates, target IDs) between perception and manipulation nodes?
- How do Fallback (Selector) nodes implement automatic retry logic without polluting the main sequence?
- How do Parallel nodes continuously monitor obstacle laser scans while the arm is executing a pick action?
- How is a Behavior Tree executed inside a ROS2 Python/C++ node?

### Key Insight
The Blackboard acts as the centralized shared memory of the Behavior Tree; perception nodes write Cartesian target coordinates to the Blackboard, which are immediately read by docking and manipulation action nodes.

---

### 1. Master Mobile Pick-and-Place Tree Structure

```text
[Root: ReactiveSequence]
  ├── [Subtree: Battery & Safety Monitor (Parallel)]
  └── [Fallback: Mobile Pick and Place Task]
        ├── [Sequence: Execute Full Pick and Place]
        │     ├── [Action: Navigate to Pick Station]
        │     ├── [Action: Deploy Arm to Perception Pose]
        │     ├── [Fallback: Detect Target Object]
        │     │     ├── [Action: Vision Detect & Write to Blackboard]
        │     │     └── [Action: Nudge Base 5cm & Retry Detect]
        │     ├── [Action: Precision Base Docking]
        │     ├── [Action: Execute Grasp Action]
        │     ├── [Condition: Verify Grasp Force Feedback]
        │     ├── [Action: Stow Arm with Payload]
        │     ├── [Action: Navigate to Place Station]
        │     └── [Action: Place Payload & Retract]
        │
        └── [Action: Fallback Safe Abort & Alert Operator]
```

---

### 2. The Blackboard Shared Data Schema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BLACKBOARD DATA FLOW                             │
│                                                                             │
│   [Detect Object Action] ──▶ Writes: target_pose_camera [x, y, z]           │
│                                           │                                 │
│                                           ▼                                 │
│   [Transform Pose Node]  ──▶ Writes: target_pose_base [x, y, z]             │
│                                           │                                 │
│                                           ▼                                 │
│   [MoveIt Action Server] ──▶ Reads:  target_pose_base                       │
│                              Writes: grasp_status [SUCCESS / FAILED]        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Hands-On Lab & Practical Code References

#### 1. Executing Full Manipulation State Machine:
```bash
# Launch manipulation state machine
ros2 launch mobile_manipulator_manipulation manipulation.launch.py
```
- Source: [`ros2_mobile_manipulator_kit/src/mobile_manipulator_manipulation/scripts/manipulation_node.py`](file:///e:/Intelligent%20Systems%20Knowledge%20Ecosystem/02%20—%20Domains/ROS2/Ros2%20learning%20kits/ros2_mobile_manipulator_kit/src/mobile_manipulator_manipulation/scripts/manipulation_node.py)
