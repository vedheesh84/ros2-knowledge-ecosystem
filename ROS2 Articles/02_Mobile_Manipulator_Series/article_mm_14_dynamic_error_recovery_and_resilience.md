## MM 14: DYNAMIC ERROR RECOVERY & MULTI-SUBSYSTEM FAULT RESILIENCE

*Purpose: Build bulletproof fault resilience in mobile manipulation. Master multi-subsystem error recovery, handle vision occlusion, solve IK infeasibility via chassis nudges, recover from missed grasps, and design fail-safe abort sequences.*

### Must Answer
- What are the five most common catastrophic failures in autonomous mobile manipulation?
- What causes Vision Occlusion, and how does active camera panning/base rotation re-acquire the target?
- What is Chassis Nudging, and how does moving the base by $\pm 3\text{ cm}$ resolve IK singularity traps?
- How do we handle missed grasps or dropped payloads during mobile transit?
- What is a Fail-Safe Home Retraction routine, and how does it prevent mechanical destruction?

### Key Insight
Physical autonomy is not achieved when a robot succeeds in ideal laboratory conditions; autonomy is achieved when a robot experiences unexpected sensory failures and recovers autonomously without human intervention.

---

### 1. The Multi-Tier Recovery Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HIERARCHICAL RECOVERY LEVELS                         │
│                                                                             │
│   LEVEL 1: LOCAL SENSORY RETRY (10 - 50 ms)                                 │
│   • Re-filter point cloud, adjust exposure, re-run contour detection.       │
│                                                                             │
│   LEVEL 2: ACTIVE RE-ACQUISITION (100 - 500 ms)                             │
│   • Pan/tilt camera neck by \pm 5 deg to eliminate specular glare.          │
│                                                                             │
│   LEVEL 3: BASE KINEMATIC NUDGE (1 - 2 seconds)                             │
│   • If arm IK is in singularity or out-of-reach: drive base \Delta x = 0.04m│
│                                                                             │
│   LEVEL 4: SAFE ABORT & RETRACT (3 - 5 seconds)                             │
│   • Open gripper, lift vertically, stow arm in chassis boundary, return home│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Chassis Nudging: Escaping IK Singularities

When an analytical IK solver returns `NO_SOLUTION`:
- Instead of terminating the mission with an error, the recovery node commands a micro-translation:
  $$\mathbf{p}_{\text{base, new}} = \mathbf{p}_{\text{base}} + \Delta d \cdot \hat{\mathbf{u}}_{\text{reach}}$$
- Moving the base by just **$3\text{ cm}$** shifts the object from the outer singularity boundary back into the center of the arm's dextrous workspace.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Running Intentional Breakers in Mobile Manipulation:
```bash
# Test controller breakdown
ros2 run mobile_manipulator_demos break_controller.py

# Test IK failure recovery
ros2 run mobile_manipulator_demos break_ik.py
```
