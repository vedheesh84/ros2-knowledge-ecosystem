## MM 11: CLOSED-LOOP BASE DOCKING & VISUAL SERVOING CONTROLLERS

*Purpose: Master precision closed-loop docking. Formulate visual servoing controllers for differential-drive mobile bases, derive kinematic error models, and drive the chassis directly from optical feature tracking.*

### Must Answer
- Why do open-loop Nav2 waypoints fail to achieve millimeter alignment at grasping tables?
- How does Image-Based Visual Servoing (IBVS) guide the mobile base using optical feature error?
- What is the non-holonomic kinematic constraint of differential-drive bases ($\dot{y} = 0$), and how does it restrict docking trajectories?
- How do proportional-integral (PI) velocity controllers convert image centroid offsets into $(v, \omega)$ `cmd_vel` commands?
- How does the docking controller transition from high-speed navigation to micro-inch visual tracking?

### Key Insight
Nav2 delivers the robot to the workstation neighborhood ($\pm 10\text{ cm}$); the closed-loop visual docking controller locks onto the target object and drives the wheels directly, centering the object with sub-millimeter precision.

---

### 1. Differential-Drive Kinematics & Non-Holonomic Constraints

A differential-drive mobile base has two independently driven wheels of radius $r$ separated by track width $b$:

$$\begin{bmatrix} \dot{x} \\ \dot{y} \\ \dot{\theta} \end{bmatrix} = \begin{bmatrix} \cos\theta & 0 \\ \sin\theta & 0 \\ 0 & 1 \end{bmatrix} \begin{bmatrix} v \\ \omega \end{bmatrix}$$

#### The Non-Holonomic Constraint:
$$\dot{x} \sin\theta - \dot{y} \cos\theta = 0$$
The base **cannot move sideways instantaneously** ($\dot{y}_{\text{body}} = 0$). To adjust lateral error, it must turn, drive forward, and turn back.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLOSED-LOOP VISUAL DOCKING                         │
│                                                                             │
│   Target Bounding Box Center (u_c, v_c) vs. Image Center (W/2, H/2)         │
│                                                                             │
│   Horizontal Pixel Error: e_x = u_c - W/2  ──▶ Angular Velocity: \omega     │
│   Depth / Height Error:   e_z = Z_meas - Z_opt ──▶ Linear Velocity: v       │
│                                                                             │
│   • \omega = -K_p,\omega \cdot e_x                                          │
│   • v = -K_p,v \cdot e_z                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Visual Docking Control Law

Let $(u_c, v_c)$ be the centroid of the target object in the camera image, and $(u^*, v^*)$ be the calibrated center of the arm's grasping zone:

$$e_{\text{azimuth}} = \frac{u_c - u^*}{f_x}$$
$$e_{\text{distance}} = Z_{\text{measured}} - d_{\text{optimal}}$$

The commanded base velocities published to `/cmd_vel`:
$$\omega_{\text{cmd}} = -K_{\omega} \cdot e_{\text{azimuth}}$$
$$v_{\text{cmd}} = \begin{cases} K_v \cdot e_{\text{distance}}, & \text{if } |e_{\text{azimuth}}| < \theta_{\text{threshold}} \\ 0.0, & \text{otherwise (Turn in place first)} \end{cases}$$

---

### 3. Hands-On Lab & Practical Code References

#### 1. Testing Closed-Loop Base Docking:
```bash
# Run Demo 06 mobile pick-and-place sequence
ros2 run mobile_manipulator_demos demo_06_mobile_pick_place.py
```
Observe how the base rotates and aligns before the arm state machine triggers pre-grasp descent.
