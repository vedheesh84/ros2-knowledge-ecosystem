## ARM 17: CLOSED-LOOP AUTONOMOUS PICK-AND-PLACE STATE MACHINE

*Purpose: The Capstone of Manipulation. Formulate the complete closed-loop Sensor-to-Decision-to-Action-to-Feedback control architecture. Master the 10-stage deterministic pick-and-place finite state machine, pre-grasp approach offsets, grasp verification, and payload transport.*

### Must Answer
- Why do open-loop manipulation scripts fail catastrophically in physical environments?
- What is the complete closed-loop Sensor $\rightarrow$ Decision $\rightarrow$ Action $\rightarrow$ Feedback cycle?
- What are the 10 formal states of an autonomous pick-and-place state machine?
- Why must a robot always approach an object from an offset vector ($\Delta z$) before closing fingers?
- How does the state machine handle asynchronous action feedback from MoveIt2 and the Gripper server?

### Key Insight
Pick-and-place is not a single trajectory; it is a discrete supervisory state machine orchestrating continuous trajectory actions, sensory checkpoints, and verification barriers.

---

### 1. The Closed-Loop Manipulation Paradigm

An open-loop system sends commands and hopes for the best. A closed-loop manipulation system verifies state at every transition boundary:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLOSED-LOOP MANIPULATION ARCHITECTURE                    │
│                                                                             │
│      [Perception / Target Pose] ──▶ [Decision: IK / Reachability]           │
│                   ▲                                │                        │
│                   │                                ▼                        │
│          [Sensory Feedback]             [Action: Trajectory Plan]           │
│          (Effort / Touch / TF)                     │                        │
│                   │                                ▼                        │
│          [Verification Barrier] ◀────── [Actuation: Motor Move]             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The 10-Stage Finite State Machine (FSM)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   THE 10-STAGE PICK-AND-PLACE STATE MACHINE                 │
│                                                                             │
│   [1. IDLE] ──▶ [2. PRE_GRASP_APPROACH] ──▶ [3. GRASP_OPEN]                │
│                                                  │                          │
│                                                  ▼                          │
│   [6. LIFT] ◀── [5. VERIFY_GRASP] ◀── [4. REACH_DOWN_CLOSE]                 │
│       │                                                                     │
│       ▼                                                                     │
│   [7. TRANSPORT] ──▶ [8. PRE_PLACE_LOWER] ──▶ [9. RELEASE] ──▶ [10. RETRACT]│
│                                                                     │       │
│                                                                     ▼       ▼
│                                                                 [1. IDLE]   │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Detailed State Transition Logic:
1. **`IDLE`**: Wait for Cartesian target command $(x_t, y_t, z_t)$.
2. **`PRE_GRASP_APPROACH`**: Move arm to offset position $(x_t, y_t, z_t + 0.05\text{ m})$ directly above object (prevents knocking object over during lateral transit).
3. **`GRASP_OPEN`**: Fully open parallel fingers.
4. **`REACH_DOWN_CLOSE`**: Descend linearly along the Z-axis to grasp height $z_t$ and command fingers closed.
5. **`VERIFY_GRASP`**: Query gripper effort. If force $> F_{\text{threshold}}$, proceed; if empty, transition to `RETRY` or `IDLE`.
6. **`LIFT`**: Move vertically upward to $(x_t, y_t, z_t + 0.10\text{ m})$ with grasped payload.
7. **`TRANSPORT`**: Execute collision-free C-space trajectory to destination approach pose $(x_d, y_d, z_d + 0.10\text{ m})$.
8. **`PRE_PLACE_LOWER`**: Descend linearly to placement surface $z_d$.
9. **`RELEASE`**: Open fingers to release payload onto surface.
10. **`RETRACT`**: Ascend vertically away from placed object and return to `home` position.

---

### 3. Production Code Walkthrough

From `ros2_arm_kit/src/arm_manipulation/arm_manipulation/pick_place_state_machine.py`:

```python
class PickPlaceFSM:
    def __init__(self, arm_client, gripper_client):
        self.state = 'IDLE'
        self.arm = arm_client
        self.gripper = gripper_client

    def step(self, target_pose, place_pose):
        if self.state == 'IDLE':
            self.state = 'PRE_GRASP_APPROACH'
            self.arm.move_to(target_pose.x, target_pose.y, target_pose.z + 0.05)
        elif self.state == 'PRE_GRASP_APPROACH':
            self.gripper.open()
            self.state = 'REACH_DOWN'
            self.arm.move_to(target_pose.x, target_pose.y, target_pose.z)
        elif self.state == 'REACH_DOWN':
            grasp_success = self.gripper.close_and_verify()
            if grasp_success:
                self.state = 'LIFT'
                self.arm.move_to(target_pose.x, target_pose.y, target_pose.z + 0.10)
            else:
                self.state = 'ERROR_MISSED_GRASP'
```

---

### 4. Hands-On Lab & Practical Code References

#### 1. Executing Full Autonomous Pick-and-Place:
```bash
# Launch master simulation environment
ros2 launch arm_bringup arm_sim.launch.py

# In another terminal, run autonomous pick-and-place state machine
ros2 run arm_manipulation pick_place_state_machine
```


