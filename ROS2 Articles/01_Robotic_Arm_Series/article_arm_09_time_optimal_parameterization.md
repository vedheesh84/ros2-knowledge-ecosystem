## ARM 09: TIME-OPTIMAL TRAJECTORY GENERATION (TOTG & TOPP-RA)

*Purpose: Master the state-of-the-art algorithms for time-parameterizing geometric paths. Learn how Time-Optimal Trajectory Generation (TOTG) and Time-Optimal Path Parameterization based on Reachability Analysis (TOPP-RA) scale motion to physical limits without motor saturation.*

### Must Answer
- What is the difference between a geometric path in C-Space and a time-parameterized trajectory?
- What are joint velocity, acceleration, and torque constraints, and how do they restrict trajectory speed?
- What is the Phase-Plane representation $(s, \dot{s})$, and how does it visualize velocity limits along a path?
- How does the Time-Optimal Trajectory Generation (TOTG) algorithm work in MoveIt2?
- How do velocity and acceleration scaling factors prevent mechanical overshoot?

### Key Insight
Sampling-based planners (like RRTConnect) output only a jagged sequence of geometric waypoints; TOTG transforms these waypoints into the fastest possible physically executable trajectory that hugs the velocity limit curve without violating acceleration limits.

---

### 1. Path Parameterization Formulation

Let a geometric path be parameterized by the scalar arc length $s \in [0, s_{\text{end}}]$:
$$\mathbf{q} = \mathbf{q}(s)$$

Using the chain rule, joint velocity and acceleration become:
$$\mathbf{\dot{q}} = \mathbf{q}'(s) \dot{s}$$
$$\mathbf{\ddot{q}} = \mathbf{q}''(s) \dot{s}^2 + \mathbf{q}'(s) \ddot{s}$$
where $\mathbf{q}'(s) = \frac{d\mathbf{q}}{ds}$ is the path tangent vector, $\dot{s} = \frac{ds}{dt}$ is the path velocity, and $\ddot{s} = \frac{d^2s}{dt^2}$ is the path acceleration.

---

### 2. Physical Constraint Bounds

Every physical robot has hard actuator limits:
1. **Velocity Limits**: $|\dot{q}_i| \le v_{i,\max} \implies \dot{s} \le \frac{v_{i,\max}}{|q_i'(s)|}$
2. **Acceleration Limits**: $|\ddot{q}_i| \le a_{i,\max} \implies -a_{i,\max} \le q_i''(s) \dot{s}^2 + q_i'(s) \ddot{s} \le a_{i,\max}$
3. **Torque Limits**: $|\tau_i| \le \tau_{i,\max}$

These inequalities form a **Maximum Velocity Curve (MVC)** in the phase plane $(s, \dot{s})$.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PHASE PLANE (s, \dot{s})                          │
│                                                                             │
│    \dot{s} (Path Velocity)                                                  │
│       ▲                                                                     │
│       │           /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\  Maximum Velocity Curve (MVC)           │
│       │          /  Optimal        \                                        │
│       │         /   Trajectory      \                                       │
│       │        /     Profile         \                                      │
│       │       /                       \                                     │
│       └──────o─────────────────────────o────────► s (Path Distance)         │
│            Start                              Goal                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. TOTG & TOPP-RA Execution in MoveIt2

1. **Forward Integration**: Integrate acceleration from start $(s=0, \dot{s}=0)$ forward along the maximum acceleration curve until reaching the MVC.
2. **Backward Integration**: Integrate maximum deceleration backward from goal $(s=s_{\text{end}}, \dot{s}=0)$.
3. **Intersection & Switching Points**: The intersection of the forward and backward integration profiles defines the **Time-Optimal Trajectory**.

#### Configuring Scaling Factors in MoveIt2:
In `ompl_planning.yaml`:
```yaml
arm:
  default_velocity_scaling_factor: 0.5     # Run at 50% max speed for safety
  default_acceleration_scaling_factor: 0.5 # Run at 50% max acceleration
```

---

### 4. Hands-On Lab & Practical Code References

#### 1. MoveIt2 Planning Pipeline Execution:
```bash
# Launch MoveIt2 motion planning environment
ros2 launch arm_bringup arm_sim.launch.py

# In another terminal, run MoveIt trajectory generation demo
ros2 run arm_demos demo_05_moveit_planning
```

#### 2. Configuration Source:
- [`ros2_arm_kit/src/arm_moveit/config/ompl_planning.yaml`](../../Ros2%20learning%20kits/ros2_arm_kit/src/arm_moveit/config/ompl_planning.yaml)


