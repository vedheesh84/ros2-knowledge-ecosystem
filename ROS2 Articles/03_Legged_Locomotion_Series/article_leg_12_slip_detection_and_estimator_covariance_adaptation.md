## LEG 12: SLIP DETECTION & ADAPTIVE ESTIMATOR COVARIANCE TUNING

*Purpose: Maintain state estimation robustness under extreme physical uncertainty. Detect foot slip on ice/mud, dynamically adapt EKF measurement covariance ($R_k$), and handle extended aerial flight phases.*

### Must Answer
- What happens to an EKF state estimator when a stance foot slips horizontally on ice or wet tile?
- How is Foot Slip detected mathematically ($\|\mathbf{v}_{\text{foot, tangential}}\| > v_{\text{threshold}}$)?
- What is Adaptive Covariance Tuning ($R_k \to \infty$), and how does it prevent slipped feet from corrupting the base velocity estimate?
- How does the estimator transition to dead-reckoning during 4-leg flight phases (e.g. during a pronk or run)?
- How do divergence-protection thresholds reset the estimator if covariance explodes?

### Key Insight
When a foot slips, the assumption that ground contact velocity is zero ($\mathbf{v}_{\text{foot}} = \mathbf{0}$) is violated; the estimator must immediately inflate measurement noise $R_k$ to discard the corrupted leg and rely on IMU integration.

---

### 1. The Physics of Foot Slip on Low-Friction Terrains

When the ratio of tangential to normal force exceeds the static friction coefficient ($\frac{\|\mathbf{f}_t\|}{f_n} > \mu$), the foot accelerates horizontally across the terrain:

$$\mathbf{v}_{\text{foot, world}} = \mathbf{v}_{\text{base}} + \boldsymbol{\omega}_{\text{base}} \times \mathbf{p}_{\text{hip}} + J \mathbf{\dot{q}} \ne \mathbf{0}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FOOT SLIP DETECTION LOGIC                          │
│                                                                             │
│   1. Compute foot horizontal velocity in world frame: v_slip = ||v_xy||.    │
│   2. If v_slip > 0.15 m/s while in STANCE:                                  │
│      ==> SLIP EVENT DETECTED!                                               │
│   3. Inflate EKF Measurement Covariance:                                    │
│      R_k = R_default \cdot \exp(\alpha \cdot v_slip) \to \infty             │
│   4. Kalman Gain K_k \to 0 (Estimator ignores the slipping leg).            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Flight Phase Handling

During dynamic running or pronking, all 4 feet are simultaneously in the air ($\sum s_i = 0$):
- The EKF automatically disables the kinematic update step.
- The state propagates purely via high-rate IMU strapdown integration:
  $$\mathbf{p}_{k+1} = \mathbf{p}_k + \mathbf{v}_k \Delta t + \frac{1}{2} (\mathbf{a}_{\text{imu}} - \mathbf{g}) \Delta t^2$$
- As soon as the first foot re-establishes non-slipping contact, the kinematic update resumes, arresting IMU drift.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Testing Estimator Slip Breakers:
```bash
# Inject foot slip into contact estimator
ros2 run quadruped_demos break_imu.py
```

