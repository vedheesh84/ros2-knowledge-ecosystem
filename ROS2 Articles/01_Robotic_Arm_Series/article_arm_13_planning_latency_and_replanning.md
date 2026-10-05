## ARM 13: PLANNING LATENCY, TIME PARAMETERIZATION & REPLANNING

*Purpose: Explore real-time constraints, latency budgets, asynchronous execution, and dynamic trajectory replanning in MoveIt2. Learn how to handle planning timeouts and adapt trajectories when obstacles enter the workspace.*

### Must Answer
- What is the latency budget for motion planning in interactive and industrial robotics?
- What causes planning timeouts, and how do we tune planning time parameters in MoveIt2?
- Why must planning and execution be asynchronous, and how does the FollowJointTrajectory action handle execution feedback?
- How does dynamic obstacle detection trigger trajectory preemption and real-time replanning?
- What are path smoothing algorithms, and how do they remove jagged waypoints from raw RRT paths?

### Key Insight
A motion planner that takes 5 seconds to find a collision-free path is useless in a dynamic environment where an obstacle moves in 0.5 seconds; production systems require sub-100ms planning budgets and real-time preemption.

---

### 1. The Manipulation Latency Budget

In closed-loop autonomous manipulation, the total system cycle time decomposes into:

$$T_{\text{total}} = T_{\text{perception}} + T_{\text{IK}} + T_{\text{plan}} + T_{\text{parameterize}} + T_{\text{execute}}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LATENCY BUDGET BREAKDOWN                           │
│                                                                             │
│   Perception (Object Pose via Camera)  ──▶ 20 - 50 ms  (30 FPS camera)      │
│   Inverse Kinematics (Analytical)      ──▶ < 0.01 ms   (Microseconds)       │
│   Motion Planning (OMPL RRTConnect)    ──▶ 10 - 80 ms  (C-Space search)     │
│   Time Parameterization (TOTG)         ──▶ 2 - 5 ms    (Spline fitting)     │
│   Action Handshake & Pre-flight        ──▶ 1 - 2 ms    (DDS QoS)            │
│   Trajectory Execution                 ──▶ 1000 - 3000 ms (Physical motion) │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Path Shortcut Smoothing

Sampling-based planners produce jagged, non-optimal paths because random points are connected incrementally.

Before trajectory time parameterization, MoveIt2 applies a **Path Shortcutter**:
1. Select two random non-adjacent waypoints $\mathbf{q}_A, \mathbf{q}_B$ along the path.
2. Check if a straight-line segment in C-space between $\mathbf{q}_A$ and $\mathbf{q}_B$ is collision-free.
3. If free, replace all intermediate waypoints with the direct segment $\mathbf{q}_A \to \mathbf{q}_B$.
4. Repeat 50–100 times to prune unnecessary bends and minimize path length.

---

### 3. Asynchronous Trajectory Execution & Preemption

MoveIt2 executes trajectories via the `FollowJointTrajectory` ROS2 action client:
- **Asynchronous Non-Blocking Execution**: The controller executes motion in the background while the supervisory node monitors sensors.
- **Preemption / Abort**: If a sensor detects an unexpected obstacle or human hand entering the workspace, the supervisory node sends an immediate `cancel_goal()` action request, triggering controlled deceleration to a safe stop.

---

### 4. Hands-On Lab & Practical Code References

#### 1. Testing Trajectory Timing Limits:
```bash
# Run intentional trajectory timing breaker to observe controller aborts
ros2 run arm_demos break_trajectory_timing
```


