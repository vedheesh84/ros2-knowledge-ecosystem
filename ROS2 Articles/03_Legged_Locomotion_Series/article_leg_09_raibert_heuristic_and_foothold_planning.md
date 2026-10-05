## LEG 09: RAIBERT FOOTHOLD HEURISTICS & CENTRIFUGAL COMPENSATION

*Purpose: Determine optimal foothold locations during dynamic locomotion. Master Marc Raibert's foundational 3-part stepping heuristic (Neutral Point, Velocity Feedback, Centrifugal Turning Bias), and adapt footholds to body accelerations.*

### Must Answer
- How does a quadruped decide where to land its swing feet while running at high speeds?
- What is Marc Raibert's 3-part foothold formula?
- What is the Symmetry / Neutral Point ($\mathbf{p}_{\text{neutral}} = \frac{T_{\text{stance}}}{2} \mathbf{v}_{\text{CoM}}$)?
- What is the Velocity Feedback Term ($K_v (\mathbf{v} - \mathbf{v}_{\text{desired}})$), and how does it regulate forward speed?
- What is the Centrifugal Acceleration Correction ($\mathbf{p}_{\text{centrifugal}} = \frac{1}{2} \sqrt{\frac{z_0}{g}} (\mathbf{v} \times \boldsymbol{\omega})$) during high-speed turns?

### Key Insight
Where a foot lands during swing determines the center of pressure during stance; Raibert's heuristic steers the robot by intentionally displacing footholds relative to the neutral center of support.

---

### 1. Marc Raibert's Foundational Foothold Formulation

In 1986, Marc Raibert (founder of Boston Dynamics) formulated the elegant 3-part heuristic for dynamic legged balance:

$$\mathbf{p}_{\text{foothold}} = \mathbf{p}_{\text{hip}} + \mathbf{p}_{\text{neutral}} + \mathbf{p}_{\text{feedback}} + \mathbf{p}_{\text{centrifugal}}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAIBERT FOOTHOLD BREAKDOWN                        │
│                                                                             │
│   1. NEUTRAL POINT (Steady-State Symmetry):                                 │
│   p_neutral = (T_stance / 2) \cdot v_CoM                                    │
│   • Centers the stance phase symmetrically underneath the hip.              │
│                                                                             │
│   2. VELOCITY FEEDBACK (Speed Regulation):                                  │
│   p_feedback = K_v \cdot (v_CoM - v_desired)                                │
│   • Stepping further forward decelerates the robot (braking torque).        │
│   • Stepping behind accelerates the robot forward (propelling torque).      │
│                                                                             │
│   3. CENTRIFUGAL CORRECTION (Turning Stability):                            │
│   p_centrifugal = 0.5 \cdot \sqrt{z_0 / g} \cdot (v_CoM \times \omega_z)   │
│   • Displaces foot outward during yaw turns to counteract centrifugal roll. │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Physical Intuition of Speed Control via Foothold

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ACCELERATION VIA FOOTHOLD PLACEMENT                   │
│                                                                             │
│   [BRAKING (Decelerate)]:               [ACCELERATION (Speed Up)]:          │
│                                                                             │
│            CoM                                   CoM                        │
│             o ──▶ v                               o ──▶ v                   │
│            /                                       \                        │
│           /                                         \                       │
│          o (Step Far Forward)                        o (Step Backward)      │
│     Gravity creates Counter-Clockwise           Gravity creates Clockwise   │
│     BRAKING Torque \tau = -m g \Delta x.        FORWARD Torque \tau = +m g. │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Hands-On Lab & Practical Code References

#### 1. Testing Speed Regulation & Turning Footholds:
```bash
# Launch quadruped simulation and send velocity commands
ros2 launch quadruped_bringup quadruped_sim.launch.py
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.4}, angular: {z: 0.3}}"
```

