## SOC 12: NON-VERBAL GESTURES: NODS, TILTS & BREATHING OSCILLATIONS

*Purpose: Master physical non-verbal communication. Design 2-DOF head nodding, shaking, curiosity tilts, and continuous harmonic breathing micro-movements to eliminate the uncanny "dead robot" stillness.*

### Must Answer
- Why does a completely motionless robot look unsettling ("dead robot effect")?
- What are Harmonic Breathing Micro-Movements ($0.25\text{ Hz}$ subtle pitch oscillations), and how do they signal life?
- How are Nodding (Agreement / Acknowledgment) and Shaking (Disapproval / Negation) parameterized via sinusoidal spline trajectories?
- What is the Curiosity Head Tilt (Neck Roll / Tilt angle of $\pm 12^\circ$), and why does it convey empathy and attentiveness?
- How do gesture overlays combine with active gaze tracking without clipping physical servo limits?

### Key Insight
Even when totally silent, a living creature breathes; adding a continuous $0.5^\circ$ vertical breathing oscillation and periodic subtle head tilts makes the robot feel warm, present, and alive.

---

### 1. The Harmonic Breathing Micro-Movement Equation

To inject subtle lifelike breathing motion into the tilt servo:

$$q_{\text{tilt, breathing}}(t) = A_{\text{breathe}} \sin(2 \pi f_{\text{breathe}} t) + A_{\text{noise}} \cdot \eta(t)$$

- $A_{\text{breathe}} \approx 0.01\text{ rad}$ ($\sim 0.6^\circ$).
- $f_{\text{breathe}} \approx 0.25\text{ Hz}$ (1 breath every $4\text{ seconds}$).

---

### 2. Expressive Gesture Kinematics

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXPRESSIVE HEAD GESTURES                          │
│                                                                             │
│   1. ACKNOWLEDGMENT NOD (Pitch):                                            │
│   q_tilt(t) = -A_nod \sin^2(\pi t / T_nod) for t \in [0, T_nod]             │
│   • Quick dip downward by 10 deg, smooth return to center.                  │
│                                                                             │
│   2. CURIOSITY HEAD TILT (Roll / Angle):                                    │
│   • Tilts head diagonally by 12 deg when listening to an interesting query. │
│                                                                             │
│   3. DISAGREEMENT SHAKE (Yaw):                                              │
│   q_pan(t) = A_shake \sin(2 \pi f_shake t) for 2 cycles                    │
│   • Rapid left-right oscillation at 3 Hz.                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Hands-On Lab & Practical Code References

#### 1. Gesture Generator Source:
- Gesture Node: [`ros2_companion_head_kit/src/companion_head_control/companion_head_control/gesture_generator.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_control/companion_head_control/gesture_generator.py)
