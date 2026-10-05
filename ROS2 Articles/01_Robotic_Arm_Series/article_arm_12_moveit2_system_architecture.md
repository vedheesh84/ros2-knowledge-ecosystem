## ARM 12: MOVEIT2 SYSTEM ARCHITECTURE: PLANNING SCENE, SRDF & FCL

*Purpose: Deconstruct the internal software architecture of the MoveIt2 manipulation framework. Master the move_group master node, Planning Scene Monitor, Flexible Collision Library (FCL), Semantic Robot Description Format (SRDF), and Allowed Collision Matrices (ACM).*

### Must Answer
- What is the internal architecture of MoveIt2, and what are the core responsibilities of `move_group`?
- What is the Planning Scene Monitor, and how does it maintain an accurate world model via `/planning_scene`?
- What is the Semantic Robot Description Format (SRDF / `arm.srdf`), and how does it define planning groups and named poses?
- What is the Allowed Collision Matrix (ACM), and why does disabling adjacent link collision checks yield a 10x planning speedup?
- How does the Flexible Collision Library (FCL) perform broadphase and narrowphase collision queries?

### Key Insight
MoveIt2 is not a single algorithm; it is a modular software integration framework that synchronizes kinematics plugins, motion planners, 3D perception collision scenes, and controller action interfaces into a cohesive manipulation brain.

---

### 1. MoveIt2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MOVEIT2 ARCHITECTURE GRAPH                         │
│                                                                             │
│   [User Interface / Script]                                                 │
│       │ (MoveGroupInterface C++ / Python)                                   │
│       ▼                                                                     │
│   [move_group Master Node]                                                  │
│       ├── [Planning Scene Monitor] ◄── /joint_states, TF, /octomap          │
│       ├── [Kinematics Plugin]      ──▶ KDL / Analytical Solvers             │
│       ├── [OMPL Motion Planner]    ──▶ RRTConnect / PRM                     │
│       └── [FCL Collision Checker]  ──▶ SRDF Allowed Collision Matrix (ACM)  │
│       │                                                                     │
│       ▼                                                                     │
│   [FollowJointTrajectory Action] ──▶ ros2_control Controller Manager        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Semantic Robot Description Format (SRDF)

While URDF specifies the robot's physical structure, the **SRDF (`arm.srdf`)** defines semantic concepts needed for motion planning:
1. **Planning Groups**: Collections of joints/links acting together (e.g. `arm`, `gripper`).
2. **Named States**: Pre-defined joint poses (e.g. `home`, `ready`, `open`, `close`).
3. **End-Effector Attachments**: Designating the tool link.
4. **Allowed Collision Matrix (ACM)**: Disabling collision checks between links that physically cannot touch.

#### Excerpt from `ros2_arm_kit/src/arm_moveit/config/arm.srdf`:
```xml
<robot name="arm">
  <!-- Group Definition -->
  <group name="arm">
    <joint name="joint_1"/>
    <joint name="joint_2"/>
    <joint name="joint_3"/>
    <joint name="joint_4"/>
    <joint name="gripper_base_joint"/>
  </group>

  <!-- Named Poses -->
  <group_state name="home" group="arm">
    <joint name="joint_1" value="0.0"/>
    <joint name="joint_2" value="0.0"/>
    <joint name="joint_3" value="0.0"/>
    <joint name="joint_4" value="0.0"/>
    <joint name="gripper_base_joint" value="0.0"/>
  </group_state>

  <!-- Allowed Collision Pairs (ACM) -->
  <disable_collisions link1="base_link" link2="link_1" reason="Adjacent"/>
  <disable_collisions link1="link_1" link2="link_2" reason="Adjacent"/>
  <disable_collisions link1="link_2" link2="link_3" reason="Adjacent"/>
  <disable_collisions link1="link_3" link2="link_4" reason="Adjacent"/>
</robot>
```

---

### 3. The Allowed Collision Matrix (ACM) Optimization

In an $N$-link robot arm, testing every link against every other link requires $\frac{N(N-1)}{2}$ collision tests per iteration.
- For our 10-link arm + gripper: $\frac{10 \times 9}{2} = 45$ checks per sampled point.
- With 1,000 iterations in RRT: **45,000 collision queries!**

The ACM disables:
1. **Adjacent Links**: Links connected by a revolute joint can never collide because their relative range is bounded by joint limits.
2. **Never-in-Collision Links**: Distant links that cannot touch due to link length geometry.

By populating the ACM in `arm.srdf`, active collision queries drop from 45 to **4**, resulting in an **instant 10x reduction in planning time**.

---

### 4. Hands-On Lab & Practical Code References

#### 1. Auditing the SRDF:
- File: [`ros2_arm_kit/src/arm_moveit/config/arm.srdf`](../../Ros2%20learning%20kits/ros2_arm_kit/src/arm_moveit/config/arm.srdf)


