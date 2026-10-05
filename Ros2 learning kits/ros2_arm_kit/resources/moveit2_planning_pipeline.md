# MoveIt2 Planning Pipeline

**Architecture & Configuration for Articulated Arm Planning**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MOVEIT2 PLANNING ARCHITECTURE                        │
│                                                                             │
│   [Goal Pose / Waypoint] ──▶ [OMPL Motion Planner] (RRTConnect)             │
│                                      │                                      │
│                                      ▼                                      │
│                       [Collision Scene Checker] (FCL)                       │
│                                      │                                      │
│                                      ▼                                      │
│                     [Time Parameterization] (TOTG)                          │
│                                      │                                      │
│                                      ▼                                      │
│                /arm_controller/follow_joint_trajectory                      │
│                                      │                                      │
│                                      ▼                                      │
│                       [ros2_control / Hardware]                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **OMPL Interface (`ompl_planning.yaml`)**: Uses RRTConnect to explore the 5-dimensional joint C-space.
2. **Kinematics Plugin (`kinematics.yaml`)**: Uses the KDL (Kinematics and Dynamics Library) analytical IK solver.
3. **Collision Avoidance (`arm.srdf`)**: Disables adjacent link collisions while enforcing strict self-collision boundaries against the tabletop mounting stand.
