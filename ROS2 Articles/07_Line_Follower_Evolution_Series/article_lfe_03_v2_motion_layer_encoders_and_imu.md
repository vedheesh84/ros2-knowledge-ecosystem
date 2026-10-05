# Article LFE-03: V2 — The Motion Layer: Encoders, IMU & Velocity Control

**Pedagogical Layer:** Inner-Loop Motion Control  
**Focus Area:** Wheel Odometry, IMU Gyroscopic Damping, Inner Velocity PID, and Acceleration Limiting  
**Associated Package:** `line_follower_v2_v3_stabilized`

---

## 1. Upgrading from Open-Loop to Inner-Loop Motion

In V2, we separate **line tracking** from **motor execution**. The motors are governed by a high-rate ($100\,\text{Hz}$) closed-loop velocity controller that guarantees the robot executes exact linear velocity $v$ and yaw rate $\omega$.

```text
[Desired v, ω] ──▶ [Differential Drive IK] ──▶ [Wheel Velocity PID] ──▶ [Motors]
                          ▲                             ▲
                          │                             │ Encoders
                   [IMU Gyro Rate] ──────────────[Wheel Odometry]
```

---

## 2. Differential Drive Inverse Kinematics

Given target chassis speed $v$ and turning rate $\omega$, wheel setpoints $(\omega_R, \omega_L)$ are:
$$\omega_R = \frac{v + \frac{\omega L}{2}}{r}, \qquad \omega_L = \frac{v - \frac{\omega L}{2}}{r}$$
where $r$ is wheel radius and $L$ is track width.

---

## 3. Gyroscopic Damping Control Law

To eliminate rotational overshoot caused by chassis inertia $J_z$, the yaw rate command is damped using direct IMU angular rate feedback $\Omega_{\text{gyro}}$:

$$\omega_{\text{cmd}} = \omega_{\text{outer}} - K_{\text{gyro}} \cdot \Omega_{\text{gyro}}$$

This introduces active artificial viscosity, preventing rotational oscillation and enabling crisp, critically damped turning.

---

## 4. Summary & Lessons Learned

With V2, the robot possesses **physical motion competence**: it drives at precise speeds, accelerates smoothly, and rejects wheel slip. In [Article LFE-04](article_lfe_04_v3_perception_arrays_and_pid_tracking.md), we upgrade the perception layer with an 8-channel array.
