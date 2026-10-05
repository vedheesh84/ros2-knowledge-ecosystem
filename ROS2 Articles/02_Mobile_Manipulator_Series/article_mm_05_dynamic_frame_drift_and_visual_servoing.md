## MM 05: DYNAMIC FRAME DRIFT, BASE COMPLIANCE & VISUAL SERVOING

*Purpose: Overcome physical non-idealities in mobile manipulation. Learn how tire compliance, suspension rocking, and wheel slip induce dynamic frame drift during reaching, and implement closed-loop Visual Servoing to achieve millimeter grasping accuracy.*

### Must Answer
- Why does a mobile robot base rock or sag when the arm extends forward with a heavy payload?
- How does base suspension tilt translate into massive end-effector Cartesian errors?
- Why can open-loop Cartesian target commands never achieve reliable grasping on mobile platforms?
- What is Visual Servoing, and what is the difference between Image-Based Visual Servoing (IBVS) and Position-Based Visual Servoing (PBVS)?
- How does an Interaction Matrix (Image Jacobian $L_e$) map feature velocity on the camera sensor directly to robot velocities?

### Key Insight
A mobile manipulator is not a rigid granite table; when the arm extends forward, the chassis tilts on its rubber tires by $1^\circ$, displacing the end-effector downward by several millimeters; continuous visual feedback closes the loop directly at the tool tip.

---

### 1. The Physics of Base Compliance & Suspension Tilt

When the robotic arm extends a mass $m_{\text{arm}}$ with payload $m_{\text{load}}$ forward by distance $r$:
$$\tau_{\text{pitch}} = (m_{\text{arm}} r_{\text{arm}} + m_{\text{load}} r) \cdot g$$

This overturning moment compresses the front rubber tires and unloads the rear tires:
$$\Delta \theta_{\text{chassis}} = \frac{\tau_{\text{pitch}}}{K_{\text{suspension}}}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CHASSIS SUSPENSION TILT                            │
│                                                                             │
│                             Extended Arm (Mass m)                           │
│                         o─────────────────────────▼ (Payload F_g)           │
│                        /                                                    │
│                       /                                                     │
│                  ┌───┴───┐                                                  │
│     (Compressed) │ Base  │ (Unloaded)                                       │
│          o═══════│ Link  │═══════o                                          │
│        [Front]   └───────┘   [Rear]                                         │
│        (Tire \Delta z)                                                      │
│                                                                             │
│   • A 1.0 degree chassis tilt at 0.35 m reach = 6.1 mm vertical drop!       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Visual Servoing: Eliminating World Drift

Instead of commanding the arm to an open-loop coordinate calculated 3 seconds ago, **Visual Servoing** continuously tracks visual features until the moment of grasp closure.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VISUAL SERVOING CLOSED-LOOP CONTROL                      │
│                                                                             │
│   [Target Features s*] ──▶ (+) ──▶ [Error e = s - s*] ──▶ [Image Jacobian L]│
│                             ▲ -                                  │          │
│                             │                                    ▼          │
│   [Camera Vision] ──────────┴─────────────────────────── [Velocity Command] │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 1. Position-Based Visual Servoing (PBVS):
- Reconstructs 3D pose in real-time ($30\text{ Hz}$).
- Computes Cartesian error $\mathbf{e}(t) = \mathbf{x}_{\text{target}}(t) - \mathbf{x}_{\text{tcp}}(t)$.
- Commands differential arm velocity: $\mathbf{\dot{x}} = -\lambda \mathbf{e}(t)$.

#### 2. Image-Based Visual Servoing (IBVS):
- Operates directly in 2D image pixel space without explicit 3D reconstruction!
- Feature error vector: $\mathbf{e} = \mathbf{s}_{\text{actual}} - \mathbf{s}_{\text{desired}}$.
- Using the Image Jacobian $L_s$:
  $$\mathbf{v}_{\text{camera}} = -\lambda L_s^\dagger (\mathbf{s} - \mathbf{s}^*)$$

---

### 3. Hands-On Lab & Practical Code References

#### 1. Executing Continuous Vision Tracking:
```bash
# Run object detector and continuous pose estimator
ros2 run mobile_manipulator_perception object_detector.py
ros2 run mobile_manipulator_perception pose_estimator.py
```
Observe how the estimated 3D target coordinates dynamically update in real-time as the mobile base moves.
