## ARM 08: POLYNOMIAL TRAJECTORY GENERATION & S-CURVE PROFILES

*Purpose: Master the mathematics of smooth motion generation. Learn why step commands destroy gearboxes, derive Cubic (3rd-order) and Quintic (5th-order) polynomial splines, formulate boundary conditions, and analyze S-curve (Jerk-limited) velocity profiles.*

### Must Answer
- Why can a robot never execute a step velocity or instantaneous position change?
- What is Continuity in trajectory generation ($C^0, C^1, C^2, C^3$), and why does $C^2$ continuity protect robot hardware?
- How do we derive the 6 coefficients of a Quintic Polynomial from position, velocity, and acceleration boundary conditions?
- What is Jerk ($j(t) = \dddot{q}(t)$), and how do S-curve profiles minimize mechanical resonance and vibration?
- How does `joint_trajectory_controller` interpolate discrete trajectory waypoints into high-rate 1000 Hz motor commands?

### Key Insight
Position continuity ($C^0$) prevents teleportation; velocity continuity ($C^1$) prevents infinite acceleration; acceleration continuity ($C^2$) prevents infinite jerk, motor current spikes, and mechanical resonance.

---

### 1. The Trajectory Generation Problem

A **Path** is a purely geometric sequence of configurations in space $\mathbf{q}(s)$ with no time parameter.
A **Trajectory** is a time-parameterized path $\mathbf{q}(t)$ that specifies the exact position, velocity, acceleration, and jerk at every instant $t \in [0, T]$.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TRAJECTORY DERIVATIVE TIERS                        │
│                                                                             │
│   Position      q(t)           ── Link displacement in space                │
│   Velocity      \dot{q}(t)     ── Kinetic energy / motor speed              │
│   Acceleration  \ddot{q}(t)    ── Motor torque / mechanical force (\tau=ma) │
│   Jerk          \dddot{q}(t)   ── Rate of change of torque / vibration      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Quintic (5th-Order) Polynomial Trajectories

A Cubic polynomial ($q(t) = a_0 + a_1 t + a_2 t^2 + a_3 t^3$) ensures continuous velocity, but its acceleration is discontinuous at start and end ($t=0, t=T$), causing instantaneous torque jumps.

To guarantee continuous acceleration ($C^2$), we use a **Quintic Polynomial**:
$$q(t) = a_0 + a_1 t + a_2 t^2 + a_3 t^3 + a_4 t^4 + a_5 t^5$$
$$\dot{q}(t) = a_1 + 2 a_2 t + 3 a_3 t^2 + 4 a_4 t^3 + 5 a_5 t^4$$
$$\ddot{q}(t) = 2 a_2 + 6 a_3 t + 12 a_4 t^2 + 20 a_5 t^3$$

#### The Six Boundary Conditions:
At $t = 0$: $q(0) = q_0, \ \dot{q}(0) = v_0, \ \ddot{q}(0) = a_0$
At $t = T$: $q(T) = q_1, \ \dot{q}(T) = v_1, \ \ddot{q}(T) = a_1$

For standard rest-to-rest motions ($v_0 = v_1 = 0, a_0 = a_1 = 0$), the coefficients solve algebraically:
$$a_0 = q_0, \quad a_1 = 0, \quad a_2 = 0$$
$$a_3 = \frac{10(q_1 - q_0)}{T^3}, \quad a_4 = \frac{-15(q_1 - q_0)}{T^4}, \quad a_5 = \frac{6(q_1 - q_0)}{T^5}$$

#### The Normalized Phase Profile:
Let normalized time $s = t / T \in [0, 1]$:
$$q(s) = q_0 + (q_1 - q_0) \left[ 10 s^3 - 15 s^4 + 6 s^5 \right]$$

---

### 3. S-Curve (Jerk-Limited 7-Segment) Profiles

In high-speed industrial manipulation, trapezoidal velocity profiles produce step changes in acceleration, resulting in **infinite jerk**. 

An **S-Curve Profile** bounds jerk to a maximum allowable threshold ($|j(t)| \le j_{\max}$), dividing motion into 7 distinct phases:
1. Constant positive jerk (Acceleration increases smoothly)
2. Zero jerk (Constant maximum acceleration)
3. Constant negative jerk (Acceleration decreases to zero)
4. Zero acceleration (Constant maximum velocity)
5. Constant negative jerk (Deceleration builds up)
6. Zero jerk (Constant maximum deceleration)
7. Constant positive jerk (Deceleration smoothly returns to zero at goal)

---

### 4. Hands-On Lab & Practical Code References

#### 1. Executing Smooth Multi-Joint Trajectories:
```bash
# Run Demo 01 to observe quintic spline trajectory execution
ros2 run arm_demos demo_01_joint_control
```

#### 2. Plotting Trajectory Velocity & Acceleration:
```bash
# In a separate terminal, plot joint velocities in real-time
ros2 run rqt_plot rqt_plot /joint_states/velocity[0] /joint_states/velocity[1]
```


