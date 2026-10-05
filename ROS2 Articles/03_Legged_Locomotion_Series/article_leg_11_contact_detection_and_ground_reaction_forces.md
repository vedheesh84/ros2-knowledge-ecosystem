## LEG 11: CONTACT SENSING, PROBABILISTIC DETECTION & REACTION FORCES

*Purpose: Detect physical ground contact accurately. Compare physical foot switches, motor current/torque residuals, and generalized momentum observers, and build probabilistic contact classifiers.*

### Must Answer
- Why does an incorrect contact state classification cause immediate controller collapse?
- What are the limitations of physical micro-switches and optical foot contact sensors (mechanical failure, dirt)?
- How do Joint Torque Residual Observers estimate 3D ground reaction forces ($\mathbf{f}_{\text{grf}} = J^{-T} \boldsymbol{\tau}_{\text{residual}}$)?
- What is a Generalized Momentum Observer, and how does it detect contact without numerical acceleration derivatives?
- How do Probabilistic Contact Classifiers (Schmitt triggers, Bayesian filters) eliminate false contact bounces?

### Key Insight
If the state estimator believes a leg is in stance when it is actually in mid-air, the EKF corrupts velocity estimates; if the MPC believes a leg is in swing when it is in stance, it commands zero force and the robot collapses.

---

### 1. Contact Detection Modalities

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTACT DETECTION MODALITIES                         │
│                                                                             │
│   1. PHYSICAL CONTACT SWITCH (Foot Dome / Optocoupler):                     │
│   • Direct binary signal s \in {0, 1}.                                      │
│   • Cons: Fragile on outdoor gravel; switch bounce during high-speed strike.│
│                                                                             │
│   2. MOTOR EFFORT / TORQUE RESIDUAL OBSERVER:                               │
│   • \tau_residual = \tau_measured - \tau_model(q, \dot{q})                  │
│   • Ground reaction force: \mathbf{f}_grf = (J^T)^\dagger \tau_residual     │
│   • Contact confirmed if f_z > F_threshold (e.g., > 15 N).                  │
│                                                                             │
│   3. GENERALIZED MOMENTUM OBSERVER:                                         │
│   • Integrates body momentum r(t) = K_o (p(t) - \int (\tau + J^T \lambda))  │
│   • Eliminates noisy acceleration derivatives \ddot{q}.                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Schmitt Trigger De-Bouncing Filter

Raw contact signals oscillate violently upon touchdown (**chatter**). A **Schmitt Trigger with hysteresis** eliminates bounce:

$$\text{Contact State}(t) = \begin{cases} 1 (\text{STANCE}), & \text{if } f_z(t) > F_{\text{high}} \quad (20\text{ N}) \\ 0 (\text{SWING}), & \text{if } f_z(t) < F_{\text{low}} \quad (5\text{ N}) \\ \text{Unchanged}, & \text{if } F_{\text{low}} \le f_z(t) \le F_{\text{high}} \end{cases}$$

---

### 3. Hands-On Lab & Practical Code References

#### 1. Contact Detector Node:
- Source: [`ros2_quadruped_kit/src/quadruped_estimation/quadruped_estimation/contact_estimator.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_estimation/quadruped_estimation/contact_estimator.py)

