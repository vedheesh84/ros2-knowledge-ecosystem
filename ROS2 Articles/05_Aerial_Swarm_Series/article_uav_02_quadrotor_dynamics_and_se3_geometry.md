## UAV 02: QUADROTOR DYNAMICS, DIFFERENTIAL FLATNESS & $SE(3)$ GEOMETRY

*Purpose: Master 6-DOF aerial flight physics on the Special Euclidean Group $SE(3)$. Derive Newton-Euler equations of motion, understand aerodynamic thrust and drag, formulate Differential Flatness, and parameterize 3D flight trajectories using flat outputs $[x, y, z, \psi]$.*

### Must Answer
- What are the 6 degrees of freedom of a quadcopter ($x, y, z \in \mathbb{R}^3$ and $Roll, Pitch, Yaw \in SO(3)$), and why is it underactuated (4 motor inputs for 6 DOF)?
- How do Newton-Euler rigid body equations describe quadrotor translational and rotational acceleration?
- How do motor angular speeds ($\omega_1, \dots, \omega_4$) map to net vertical thrust $T$ and body moments $(\tau_x, \tau_y, \tau_z)$?
- What is Differential Flatness (Mellinger & Kumar, 2011), and how does it map $[x(t), y(t), z(t), \psi(t)]$ to all state and control variables algebraically?
- How does Differential Flatness eliminate numerical integration when planning aggressive $C^4$ snap-continuous trajectories?

### Key Insight
Because a quadrotor is differentially flat, its 12-dimensional dynamic state and 4 motor inputs can be computed algebraically from a 4-dimensional flat output trajectory $[x(t), y(t), z(t), \psi(t)]$ and its time derivatives up to the 4th order (Snap).

---

### 1. 6-DOF Quadrotor Dynamics on $SE(3)$

Let position be $\mathbf{p} = [x, y, z]^T$, velocity $\mathbf{v} = [\dot{x}, \dot{y}, \dot{z}]^T$, orientation rotation matrix $R \in SO(3)$, and body angular velocity $\boldsymbol{\omega} \in \mathbb{R}^3$.

$$\mathbf{\dot{p}} = \mathbf{v}$$
$$m \mathbf{\dot{v}} = -m g \hat{\mathbf{z}}_W + R \begin{bmatrix} 0 \\ 0 \\ T \end{bmatrix} - D_v \mathbf{v}$$
$$\dot{R} = R [\boldsymbol{\omega}]_\times$$
$$J \boldsymbol{\dot{\omega}} = \boldsymbol{\tau} - \boldsymbol{\omega} \times (J \boldsymbol{\omega})$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             QUADROTOR X-GEOMETRY                            │
│                                                                             │
│              Motor 1 (CCW)  \                 /  Motor 2 (CW)               │
│               Thrust f_1     \               /    Thrust f_2                │
│                               \             /                               │
│                                ┌───────────┐                                │
│                                │ Body Mass │                                │
│                                │   m, J    │                                │
│                                └───────────┘                                │
│                               /             \                               │
│                              /               \                              │
│              Motor 4 (CW)   /                 \  Motor 3 (CCW)              │
│               Thrust f_4                         Thrust f_3                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Thrust & Moment Allocation Matrix

$$T = c_T (\omega_1^2 + \omega_2^2 + \omega_3^2 + \omega_4^2)$$
$$\tau_x = d \cdot c_T (-\omega_1^2 - \omega_2^2 + \omega_3^2 + \omega_4^2) / \sqrt{2}$$
$$\tau_y = d \cdot c_T (\omega_1^2 - \omega_2^2 - \omega_3^2 + \omega_4^2) / \sqrt{2}$$
$$\tau_z = c_D (\omega_1^2 - \omega_2^2 + \omega_3^2 - \omega_4^2)$$

---

### 3. Differential Flatness Formulation

A system is differentially flat if states and inputs can be expressed in terms of flat outputs $\boldsymbol{\sigma}(t) = [x(t), y(t), z(t), \psi(t)]^T$:

1. **Total Thrust**: $T = m \|\mathbf{\ddot{p}} + g \hat{\mathbf{z}}_W\|$.
2. **Body Z-Axis**: $\mathbf{z}_B = \frac{\mathbf{\ddot{p}} + g \hat{\mathbf{z}}_W}{\|\mathbf{\ddot{p}} + g \hat{\mathbf{z}}_W\|}$.
3. **Body X and Y Axes**: Constructed from $\mathbf{z}_B$ and desired yaw $\psi(t)$.
4. **Body Angular Velocity $\boldsymbol{\omega}$**: Computed from the 3rd derivative of position (Jerk: $\mathbf{p}^{(3)}$).
5. **Body Angular Acceleration $\boldsymbol{\dot{\omega}}$**: Computed from the 4th derivative of position (Snap: $\mathbf{p}^{(4)}$).

---

### 4. Hands-On Lab & Practical Code References

#### 1. Flight Controller Simulator Source:
- Controller Node: [`ros2_drone_swarm_kit/src/swarm_control/swarm_control/flight_controller_node.py`](../../Ros2%20learning%20kits/ros2_drone_swarm_kit/src/swarm_control/swarm_control/flight_controller_node.py)
- Run Demo 01: `ros2 run swarm_demos demo_01_single_drone_flight`
