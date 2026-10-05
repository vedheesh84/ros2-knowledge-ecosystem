## ARM 18: REACTIVE REPLANNING, SLIP DETECTION & FAULT RECOVERY

*Purpose: Master resilience and error recovery in autonomous manipulation. Learn how to detect physical grasp failure, handle dynamic obstacles during trajectory execution, implement hierarchical recovery behaviors, and guarantee safe home retraction.*

### Must Answer
- What are the most common physical failure modes in pick-and-place manipulation?
- How is mid-air object slippage detected using tactile or current feedback?
- How does MoveIt2 dynamic replanning preempt active trajectories when obstacles encroach into the arm path?
- What is Hierarchical Error Recovery, and how does it prevent robot freezing?
- How do safe retraction maneuvers prevent the arm from colliding with surrounding equipment during emergency aborts?

### Key Insight
A truly intelligent manipulation system is defined not by how smoothly it executes when everything is perfect, but by how reliably it detects failures, recovers gracefully, and protects its physical embodiment.

---

### 1. The Taxonomy of Manipulation Failures

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MANIPULATION FAILURE TAXONOMY                        │
│                                                                             │
│   1. KINEMATIC FAULTS      ──▶ Target unreachable / Singularity boundary    │
│   2. SENSORY FAULTS        ──▶ Vision occlusion / False positive detection  │
│   3. CONTACT FAULTS        ──▶ Missed grasp / Jammed fingers                │
│   4. TRANSPORT FAULTS      ──▶ Payload slippage / External collision        │
│   5. ACTUATION FAULTS      ──▶ Over-current / Thermal shutdown / Brownout   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Mid-Air Slip Detection & Reactive Regrasping

If an object begins to slip during high-speed transport:
1. The contact normal force drops momentarily, followed by high-frequency shear vibrations.
2. Motor current on the gripper fluctuates.

#### Reactive Slip Response:
- **Level 1 (Immediate)**: Increase gripper closing effort by $+25\%$.
- **Level 2 (If slip continues)**: Decelerate arm velocity scaling factor from $1.0 \to 0.2$ to minimize inertial centrifugal forces.
- **Level 3 (If payload lost)**: Abort transport, record failure event, and return arm to safe `home` standby.

---

### 3. Hierarchical Error Recovery State Machine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HIERARCHICAL FAULT RECOVERY                          │
│                                                                             │
│   [Fault Detected]                                                          │
│          │                                                                  │
│          ▼                                                                  │
│   [Retry Local Action] (Up to 2 retries, e.g. re-attempt grasp)             │
│          │ (If still failing)                                               │
│          ▼                                                                  │
│   [Safe Retract] (Ascend vertically \Delta z = +0.10 m)                     │
│          │                                                                  │
│          ▼                                                                  │
│   [Return to Home Pose] (Known collision-free standby state)                │
│          │                                                                  │
│          ▼                                                                  │
│   [Publish Diagnostic Alert] ──▶ /diagnostics (Notify Operator)             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 4. Hands-On Lab & Practical Code References

#### 1. Testing Failure Breakers:
```bash
# Test gripper stall failure handling
ros2 run arm_demos break_gripper_stall

# Test IK singularity boundary rejection
ros2 run arm_demos break_ik_singularity
```


