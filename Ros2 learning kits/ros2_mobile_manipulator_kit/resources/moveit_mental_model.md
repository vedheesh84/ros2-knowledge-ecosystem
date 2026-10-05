# MoveIt Mental Model

MoveIt is powerful. MoveIt is also a black box if you don't understand what's inside.
This document exposes the internals so failures make sense.

---

## The Core Loop

```
Goal Pose ─────────────────────────────────────────────────┐
    │                                                      │
    ▼                                                      │
┌─────────────────────┐                                    │
│  IK Solver (KDL)    │  "Can I reach this pose?"          │
│  - Uses kinematics  │                                    │
│  - Returns FAIL or  │                                    │
│    joint angles     │                                    │
└─────────────────────┘                                    │
    │                                                      │
    │ joint angles                                         │
    ▼                                                      │
┌─────────────────────┐                                    │
│  Motion Planner     │  "What path avoids collisions?"    │
│  (OMPL)             │                                    │
│  - Samples configs  │                                    │
│  - Checks collisions│                                    │
│  - Returns FAIL or  │                                    │
│    trajectory       │                                    │
└─────────────────────┘                                    │
    │                                                      │
    │ trajectory                                           │
    ▼                                                      │
┌─────────────────────┐                                    │
│  Trajectory         │  "Can we execute this safely?"     │
│  Execution          │                                    │
│  - Sends to         │                                    │
│    controller       │                                    │
│  - Monitors         │                                    │
│    feedback         │                                    │
└─────────────────────┘                                    │
    │                                                      │
    │ result                                               │
    ▼                                                      │
  SUCCESS / FAIL ◄─────────────────────────────────────────┘
```

---

## What Each Stage Can Fail

### IK Failure (Inverse Kinematics)

**Error:** "No IK solution found"

**Causes:**
- Pose is outside workspace (too far/close)
- Pose orientation is impossible (joint limits)
- Pose is at singularity (arm fully extended)
- Wrong planning frame specified

**Debug:**
```bash
# Check workspace visually
ros2 run rviz2 rviz2  # Add InteractiveMarker, drag to see limits

# Check IK solver
ros2 param get /move_group robot_description_kinematics
```

### Planning Failure

**Error:** "Unable to find valid path"

**Causes:**
- Collision with self or environment
- Start state invalid (current pose in collision)
- Goal state unreachable without collision
- Planning time too short

**Debug:**
```bash
# Visualize planning scene
ros2 topic echo /planning_scene  # Check collision objects

# Increase planning time
# In code: move_group.set_planning_time(10.0)
```

### Execution Failure

**Error:** "Trajectory execution failed"

**Causes:**
- Controller not active
- Joint hit limit during motion
- Collision detected mid-trajectory
- Communication timeout

**Debug:**
```bash
# Check controller state
ros2 control list_controllers

# Check joint states during motion
ros2 topic echo /joint_states
```

---

## Key Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| SRDF | Groups, poses, end effector | `arm_control/config/mobile_manipulator.srdf` |
| kinematics.yaml | IK solver selection | `arm_control/config/kinematics.yaml` |
| joint_limits.yaml | Motion speed limits | `arm_control/config/joint_limits.yaml` |
| moveit_controllers.yaml | Controller mapping | `arm_control/config/moveit_controllers.yaml` |

---

## Planning Frame vs End-Effector Frame

This is a critical distinction.

### Planning Frame: `arm_base_link`
- The "world" for planning
- Goal poses are relative to this
- Must be stable (not moving during plan)

### End-Effector Frame: `tool_frame`
- Where the gripper fingers meet
- What you're actually trying to position
- Defined in SRDF as end effector

**Common mistake:** Sending goal in `camera_link_optical` without transforming to `arm_base_link`.

---

## IK Solver: KDL

This kit uses KDL (Kinematics and Dynamics Library).

**Pros:**
- Works for any arm
- No setup required
- Handles joint limits

**Cons:**
- Slower than analytical solvers
- May find suboptimal solutions
- Can get stuck at singularities

**Configuration:**
```yaml
# kinematics.yaml
arm:
  kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin
  kinematics_solver_search_resolution: 0.005  # Smaller = slower but better
  kinematics_solver_timeout: 0.5              # Increase if failing often
```

---

## Joint Limits: Where They Come From

MoveIt uses joint limits from **multiple sources** (merged):

1. **URDF** - Physical limits of hardware
2. **joint_limits.yaml** - Velocity/acceleration scaling
3. **SRDF** - Can further restrict (not expand)

**Scaling factors in joint_limits.yaml:**
```yaml
default_velocity_scaling_factor: 0.2   # 20% of max speed
default_acceleration_scaling_factor: 0.2
```

**Why slow defaults?**
- Safer for learning
- Less servo strain
- Time to e-stop if needed

---

## Planning vs Execution

These are **separate systems**.

### Planning (move_group)
- Computes trajectory
- Checks collisions
- Returns list of waypoints + times
- Does NOT move the robot

### Execution (controller_manager)
- Receives trajectory
- Sends to hardware
- Monitors progress
- Reports success/failure

**MoveIt bridges them** via FollowJointTrajectory action.

---

## Named Poses (from SRDF)

```xml
<group_state name="home" group="arm">
    <joint name="joint_1" value="0"/>
    ...
</group_state>
```

These are **joint-space** goals, not Cartesian.

**Advantage:** No IK required, always reachable.
**Use for:** Safe positions, known configurations.

---

## Debugging Checklist

When a motion fails, check in order:

1. **Is the controller active?**
   ```bash
   ros2 control list_controllers
   ```

2. **Is the goal reachable?**
   - Try in RViz with InteractiveMarker
   - Check joint limits in URDF

3. **Is the current state valid?**
   - No self-collision?
   - All joints publishing?

4. **Is TF working?**
   ```bash
   ros2 run tf2_ros tf2_echo arm_base_link tool_frame
   ```

5. **Are parameters loaded?**
   ```bash
   ros2 param list /move_group
   ```

---

## What MoveIt Does NOT Do

- **Decide what to grasp** (that's perception)
- **Coordinate with navigation** (that's manipulation/state machine)
- **Handle grasp failure** (that's your recovery logic)
- **Understand objects** (it only knows collision geometries)

MoveIt is a **motion planner**, not a manipulation system.
Manipulation = Perception + Planning + Control + Recovery.
