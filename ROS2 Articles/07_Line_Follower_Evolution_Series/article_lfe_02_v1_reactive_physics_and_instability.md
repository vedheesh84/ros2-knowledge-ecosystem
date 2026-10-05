# Article LFE-02: V1 — Baseline Reactive Control & Physical Instability

**Pedagogical Layer:** Baseline Physical Dynamics  
**Focus Area:** Bang-Bang Thresholding, L298N Voltage Drops, PWM Deadbands, and Latency-Induced Divergence  
**Associated Package:** `line_follower_v1_reactive`

---

## 1. The V1 Architecture

The V1 robot represents the simplest possible line tracker:
- **Compute**: 8-bit Microcontroller (Arduino Uno).
- **Sensors**: 2 discrete phototransistor/LED pairs (Left and Right) spaced $50\,\text{mm}$ apart.
- **Actuation**: L298N Dual H-Bridge motor driver driving two geared DC motors in open-loop.

```text
       ┌───────────────────┐
       │   Arduino Uno     │
       └─▲───────▲───────┬─┘
         │       │       │ PWM
     Left IR   Right IR  ▼
     Sensor    Sensor  ┌───────────┐
      [ ○ ]     [ ○ ]  │   L298N   │──▶ DC Motors
                       └───────────┘
```

---

## 2. Mathematical Model of Bang-Bang Thresholding

Let $I_L$ and $I_R$ be the reflected light intensities normalized to $[0, 1]$, and let $\theta_{\text{th}}$ be the comparator threshold. The control law is a piecewise discontinuous step function:

$$u(t) = \begin{cases} 
+V_{\text{turn}}, & \text{if } I_L > \theta_{\text{th}} \land I_R \le \theta_{\text{th}} \quad (\text{Hard Left}) \\
-V_{\text{turn}}, & \text{if } I_L \le \theta_{\text{th}} \land I_R > \theta_{\text{th}} \quad (\text{Hard Right}) \\
+V_{\text{fwd}}, & \text{if } I_L > \theta_{\text{th}} \land I_R > \theta_{\text{th}} \quad (\text{Straight}) \\
0, & \text{if } I_L \le \theta_{\text{th}} \land I_R \le \theta_{\text{th}} \quad (\text{Lost Line})
\end{cases}$$

---

## 3. The 4 Inherent Physical Failure Modes

1. **Limit Cycle Oscillation (Zigzagging)**:
   - Because control action is binary, the robot cannot apply a subtle correction. It violently overshoots the line center at every step, creating a high-amplitude limit cycle.
2. **Phase Lag $\tau$ & Instability**:
   - The loop delay $\tau = \tau_{\text{sample}} + \tau_{\text{motor\_inductance}} + \tau_{\text{inertia}}$ causes corrections to arrive out of phase. At speeds $v > 0.25\,\text{m/s}$, the phase lag exceeds $90^\circ$, causing catastrophic track departure.
3. **L298N Voltage Drop & PWM Deadband**:
   - The BJT H-bridge in the L298N incurs a $1.8\,\text{V} - 2.5\,\text{V}$ internal drop. At low PWM duty cycles ($< 35\%$), static Coulomb friction prevents the wheels from turning entirely.
4. **Zero Velocity Regulation**:
   - As battery voltage drains from $12.6\,\text{V} \to 10.5\,\text{V}$, the actual speed drops by over $20\%$ despite identical PWM commands.

---

## 4. Summary & Lessons Learned

V1 establishes the ground truth: **software logic cannot overcome unmodeled physics and lack of feedback**. In [Article LFE-03](article_lfe_03_v2_motion_layer_encoders_and_imu.md), we build V2 to solve physical motion instability.
