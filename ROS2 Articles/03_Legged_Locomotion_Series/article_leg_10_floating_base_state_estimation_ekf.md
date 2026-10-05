## LEG 10: FLOATING-BASE STATE ESTIMATION & EXTENDED KALMAN FILTERING (EKF)

*Purpose: Solve the floating-base state estimation problem in legged robotics. Master the fusion of high-frequency IMU linear accelerations and angular velocities with leg forward kinematics and contact switches via Extended Kalman Filtering (EKF).*

### Must Answer
- Why can legged robots not use wheel encoders for dead-reckoning odometry?
- What is the Floating-Base State Vector ($\mathbf{x} = [\mathbf{p}_b, \mathbf{v}_b, \mathbf{q}_b, \mathbf{p}_{f1}, \dots, \mathbf{p}_{f4}]^T$)?
- How does an IMU predict high-frequency ($500\text{ Hz}$) floating-base position and velocity?
- How do Leg Forward Kinematics on grounded stance feet correct IMU integration drift?
- How does the EKF handle asynchronous contact state changes when feet lift off and land?

### Key Insight
When a foot is planted on the ground, its world velocity is zero ($\mathbf{v}_{\text{foot}} = \mathbf{0}$); measuring hip-to-foot velocity via leg kinematics provides an absolute velocity measurement to bound IMU accelerometer integration drift.

---

### 1. The Floating-Base Estimation Problem

Because a quadruped's feet slip, lift, and land intermittently, direct wheel odometry does not exist.
- **Integrating IMU Accelerometer ($a = \ddot{x}$)**: Double integration causes position drift growing quadratically ($O(t^2)$).
- **Leg Kinematics ($\mathbf{p}_{\text{foot}} = \text{FK}(\mathbf{q})$)**: Provides relative hip-to-foot distance, but knows nothing about world position if the base tilts.

**Solution**: The **Contact-Aided Floating-Base EKF** fuses IMU dynamics in the prediction step with kinematic contact constraints in the update step.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONTACT-AIDED FLOATING-BASE EKF                          │
│                                                                             │
│   [6-Axis IMU (500 Hz)]                                                     │
│   (Linear Accel \mathbf{a}, Angular Rate \boldsymbol{\omega})                │
│          │                                                                  │
│          ▼                                                                  │
│   [EKF PREDICTION STEP] ──▶ \hat{\mathbf{x}}_{k|k-1} = f(\hat{\mathbf{x}}, u)│
│                                           │                                 │
│   [Leg Encoders q, \dot{q}]               │                                 │
│   [Contact Sensors s_i \in {0, 1}]        │                                 │
│          │                                │                                 │
│          ▼                                ▼                                 │
│   [EKF UPDATE STEP] ──────▶ \hat{\mathbf{x}}_k = \hat{\mathbf{x}}_{k|k-1} + K (z - h(\hat{x}))
│   (Enforce v_foot = 0 on stance feet)     │                                 │
│                                           ▼                                 │
│                             Publish /odom & /tf [odom -> base_link]         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Contact Kinematic Measurement Model

For each leg $i$ that is currently in **STANCE** ($s_i = 1$):
$$\mathbf{z}_i = -\mathbf{v}_{\text{base}} - \boldsymbol{\omega}_{\text{base}} \times \mathbf{p}_{\text{hip}, i} - J_{\text{leg}, i} \mathbf{\dot{q}}_i = \mathbf{0} + \mathbf{v}_{\text{noise}}$$

This measurement provides a direct observation of the base linear velocity $\mathbf{v}_{\text{base}}$, completely eliminating velocity drift!

---

### 3. Hands-On Lab & Practical Code References

#### 1. State Estimator Source Code:
- EKF Estimator: [`ros2_quadruped_kit/src/quadruped_estimation/quadruped_estimation/state_estimator.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_estimation/quadruped_estimation/state_estimator.py)
- Breaker Test: `ros2 run quadruped_demos break_imu.py`

