## LEG 07: GAIT TAXONOMY, DUTY CYCLES & GAIT PHASE CLOCKS

*Purpose: Master multi-legged gait generation. Analyze the taxonomy of biological and robotic gaits (Crawl, Trot, Pace, Bound, Pronk), formulate duty cycles ($\beta$), construct periodic Gait Phase Clocks, and schedule stance/swing transitions.*

### Must Answer
- What is a Gait, and how is it parameterized by cycle period ($T$), duty factor ($\beta$), and phase offsets ($\phi_i$)?
- What is the difference between Static Gaits (Crawl $\beta = 0.75$) and Dynamic Gaits (Trot $\beta = 0.50$)?
- What are the phase relationships of the 4 legs in a Diagonal Trot vs. Lateral Pace vs. Sagittal Bound?
- How does a Normalized Phase Clock ($\phi(t) \in [0, 1)$) determine whether a leg is in Stance or Swing?
- How do Central Pattern Generators (CPGs) and coupled phase oscillators synchronize leg coordination?

### Key Insight
A gait is not a fixed animation; it is a parameterized periodic phase clock that partitions time into stance phases (where feet exert ground reaction forces) and swing phases (where feet reposition in the air).

---

### 1. The Mathematical Gait Parameterization

Every periodic multi-legged gait is defined by:
1. **Gait Period ($T_{\text{stride}}$)**: Total duration of one complete stride cycle (e.g. $0.4\text{ s} \to 2.5\text{ Hz}$).
2. **Duty Factor ($\beta \in (0, 1)$)**: Fraction of the stride time that a leg spends in ground contact (Stance):
   $$T_{\text{stance}} = \beta \cdot T_{\text{stride}}, \quad T_{\text{swing}} = (1 - \beta) \cdot T_{\text{stride}}$$
3. **Phase Offsets ($\phi_i \in [0, 1)$)**: Timing offsets for each leg $i \in \{\text{FL}, \text{FR}, \text{RL}, \text{RR}\}$.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           QUADRUPED GAIT TAXONOMY                          │
│                                                                             │
│   1. STATIC CRAWL (\beta = 0.75):                                           │
│   FL: [0.00] ──▶ FR: [0.50] ──▶ RL: [0.75] ──▶ RR: [0.25]                   │
│   • 3 legs always on the ground; static equilibrium maintained at all times.│
│                                                                             │
│   2. DYNAMIC TROT (\beta = 0.50):                                           │
│   Diagonal Pair 1 (FL + RR): \phi = 0.00                                    │
│   Diagonal Pair 2 (FR + RL): \phi = 0.50                                    │
│   • High energetic efficiency; dynamic balance via LIPM / MPC.              │
│                                                                             │
│   3. BOUND (\beta = 0.40):                                                  │
│   Front Pair (FL + FR): \phi = 0.00 ──▶ Rear Pair (RL + RR): \phi = 0.50    │
│   • Sagittal pitch oscillations for high-speed sprinting and obstacle jump. │
│                                                                             │
│   4. PRONK (\beta = 0.30):                                                  │
│   All 4 Legs (FL, FR, RL, RR): \phi = 0.00 simultaneously                   │
│   • 4-leg explosive jumping with extended flight phases.                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Normalized Phase Clock Algorithm

For each leg $i$, the continuous phase variable $\theta_i(t) \in [0, 1)$ increments linearly:

$$\theta_i(t) = \left( \frac{t}{T_{\text{stride}}} + \phi_i \right) \pmod 1$$

#### State Decision:
$$\text{Leg State}_i(t) = \begin{cases} \text{STANCE (Force Generation)}, & \text{if } 0 \le \theta_i(t) < \beta \\ \text{SWING (Bézier Trajectory)}, & \text{if } \beta \le \theta_i(t) < 1.0 \end{cases}$$

---

### 3. Hands-On Lab & Practical Code References

#### 1. Inspecting Gait Scheduler:
- Scheduler Source: [`ros2_quadruped_kit/src/quadruped_locomotion/quadruped_locomotion/gait_scheduler.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_locomotion/quadruped_locomotion/gait_scheduler.py)
- Run Demo 04: `ros2 run quadruped_demos demo_04_gait`

