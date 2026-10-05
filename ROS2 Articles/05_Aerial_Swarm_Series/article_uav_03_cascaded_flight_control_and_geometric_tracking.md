## UAV 03: CASCADED GEOMETRIC FLIGHT CONTROL & TRAJECTORY TRACKING

*Purpose: Implement robust flight controllers. Master the 3-tier Cascaded Geometric Controller on $SE(3)$ (Position PID $\to$ Desired Thrust/Attitude $\to$ Angular Rate PID $\to$ Motor Allocation), and evaluate anti-windup and actuator saturation.*

### Must Answer
- What is Cascaded Control, and why must the inner attitude loop run $5 - 10\times$ faster than the outer position loop?
- How does the Outer Position Controller convert position error $\mathbf{e}_p$ into a desired 3D acceleration vector $\mathbf{a}_{\text{des}}$?
- How is the desired attitude rotation matrix $R_{\text{des}} \in SO(3)$ extracted geometrically from $\mathbf{a}_{\text{des}}$ and yaw $\psi_{\text{des}}$?
- What is Geometric $SO(3)$ Attitude Tracking (Lee, Leok & McClamroch, 2010), and why does it avoid Euler angle singularities?
- How does Motor Output Saturation clamping prevent catastrophic loss of attitude control during high-thrust maneuvers?

### Key Insight
Controlling a quadrotor requires an attitude loop running at $500\text{ Hz}$ to stabilize fast rotational dynamics while an outer position loop runs at $50\text{ Hz}$ to track spatial coordinates; decoupling them geometrically avoids Gimbal Lock even during extreme inverted flips.

---

### 1. The 3-Tier Cascaded Control Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CASCADED GEOMETRIC CONTROL ARCHITECTURE                  │
│                                                                             │
│   [Position Target p*, v*] (50 Hz)                                          │
│             │                                                               │
│             ▼                                                               │
│   [OUTER POSITION LOOP] ──▶ Computes: Desired Accel \mathbf{a}_des, Thrust T│
│             │                                                               │
│             ▼ (Geometric SO(3) Attitude Extraction)                         │
│   [Attitude Target R_des] (200 Hz)                                          │
│             │                                                               │
│             ▼                                                               │
│   [INNER ATTITUDE LOOP] ──▶ Computes: Desired Angular Acceleration \dot{\omega}
│             │                                                               │
│             ▼                                                               │
│   [RATE LOOP] (500 Hz)  ──▶ Computes: Body Torques \tau_x, \tau_y, \tau_z   │
│             │                                                               │
│             ▼                                                               │
│   [MOTOR ALLOCATION MATRIX] ──▶ PWM Duty Cycles [u_1, u_2, u_3, u_4]        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Geometric $SO(3)$ Attitude Error

Unlike Euler angle error (which suffers from Gimbal Lock), geometric attitude error on $SO(3)$ is defined as:

$$\mathbf{e}_R = \frac{1}{2} \left( R_{\text{des}}^T R - R^T R_{\text{des}} \right)^\vee \in \mathbb{R}^3$$
$$\mathbf{e}_\omega = \boldsymbol{\omega} - R^T R_{\text{des}} \boldsymbol{\omega}_{\text{des}}$$

The commanded body torque vector is:
$$\boldsymbol{\tau}_{\text{cmd}} = -K_R \mathbf{e}_R - K_\omega \mathbf{e}_\omega + \boldsymbol{\omega} \times (J \boldsymbol{\omega})$$

---

### 3. Hands-On Lab & Practical Code References

#### 1. Testing Flight Control Pipeline:
- Source: [`ros2_drone_swarm_kit/src/swarm_control/swarm_control/flight_controller_node.py`](../../Ros2%20learning%20kits/ros2_drone_swarm_kit/src/swarm_control/swarm_control/flight_controller_node.py)
