## LEG 08: BÉZIER SWING TRAJECTORIES & IMPACT SHOCK MITIGATION

*Purpose: Master swing foot trajectory generation. Formulate 12-point Bézier polynomial curves, achieve $C^2$ acceleration continuity, ensure zero ground touchdown impact velocity ($\dot{z}_{\text{touchdown}} = 0$), and prevent ground stubbing.*

### Must Answer
- What happens when a swinging foot strikes the ground with high downward velocity?
- Why do simple sinusoidal or cubic trajectories produce violent ground impact shock?
- What are Bézier Curves, and how do control points define clearance height and touchdown slope?
- How does the boundary condition $\mathbf{\dot{p}}_{\text{touchdown}} = \mathbf{0}$ prevent foot bounce and motor gear stripping?
- How do early-touchdown and late-touchdown reflexes handle unexpected terrain variations?

### Key Insight
A proper swing trajectory does not slam into the floor; it lifts vertically, arcs forward smoothly, and decelerates to zero vertical velocity at the exact instant of ground contact, converting dynamic flight into seamless force transmission.

---

### 1. The Physics of Foot Touchdown Impact

When a foot of mass $m_{\text{foot}}$ strikes rigid ground with vertical impact velocity $v_z$:
$$F_{\text{impact}} \approx m_{\text{foot}} \frac{\Delta v_z}{\Delta t_{\text{contact}}}$$

For $\Delta t \approx 2\text{ ms}$, an impact velocity of $v_z = 0.5\text{ m/s}$ generates impulsive shock spikes exceeding $200\text{ N}$. This strips servo gears, triggers false IMU spikes, and destabilizes the body.

---

### 2. 12-Point Bézier Swing Trajectory Formulation

A Bézier curve of degree $n = 11$ maps normalized swing phase $s \in [0, 1]$ to 3D foot position $\mathbf{p}(s)$:

$$\mathbf{p}(s) = \sum_{k=0}^{n} B_{k, n}(s) \mathbf{P}_k = \sum_{k=0}^{n} \binom{n}{k} (1 - s)^{n - k} s^k \mathbf{P}_k$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       BÉZIER SWING TRAJECTORY PROFILE                       │
│                                                                             │
│                        P4 ─────────── P5 ─────────── P6                     │
│                        /                               \   Max Clearance    │
│                       /                                 \    Height h_clear │
│                     P3                                   P7                 │
│                    /                                       \                │
│                   P2                                       P8               │
│                  /                                           \              │
│     Lift-off P0-P1 ═════════════════════════════════════════ P9-P11 Touchdown
│     (\dot{z} = 0)                                            (\dot{z} = 0)  │
│     Current Liftoff Pos                                      Target Foothold│
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Boundary Conditions for Smooth Contact:
1. **Liftoff**: $\mathbf{P}_0 = \mathbf{P}_1 = \mathbf{p}_{\text{liftoff}}$ ($\mathbf{\dot{p}}(0) = \mathbf{0}$).
2. **Apex**: $\mathbf{P}_5, \mathbf{P}_6$ enforce maximum obstacle clearance $z = z_0 + h_{\text{clear}}$.
3. **Touchdown**: $\mathbf{P}_9 = \mathbf{P}_{10} = \mathbf{P}_{11} = \mathbf{p}_{\text{target}}$ ($\mathbf{\dot{p}}(1) = \mathbf{0}, \mathbf{\ddot{p}}(1) = \mathbf{0}$).

---

### 3. Hands-On Lab & Practical Code References

#### 1. Swing Trajectory Generator Source:
- Trajectory Source: [`ros2_quadruped_kit/src/quadruped_locomotion/quadruped_locomotion/swing_trajectory.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_locomotion/quadruped_locomotion/swing_trajectory.py)

