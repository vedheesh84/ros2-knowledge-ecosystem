## UAV 06: DISTRIBUTED STATE ESTIMATION & COVARIANCE INTERSECTION (CI)

*Purpose: Fuse noisy multi-agent sensory observations without central servers. Master Decentralized Kalman Filtering (DKF), analyze the Double-Counting Information problem in cyclic networks, and formulate Covariance Intersection (CI).*

### Must Answer
- Why does broadcasting raw sensor estimates in multi-agent networks cause dangerous overconfidence (the "Rumor Propagation" problem)?
- What is Covariance Intersection (CI), and how does it fuse two estimates when cross-correlations are unknown?
- What is the geometric interpretation of Covariance Intersection (the intersection of covariance hyper-ellipsoids)?
- How does a swarm track an evasive moving target collectively when each drone has only intermittent camera glimpses?
- How does peer-to-peer relative localization (UWB ranging + optical flow) maintain swarm geometry without GPS?

### Key Insight
When Drone A shares an estimate with Drone B, and Drone B shares it back to Drone A, a standard Kalman filter treats it as new information and shrinks uncertainty incorrectly; Covariance Intersection provides a mathematically proven upper bound that guarantees consistency under unknown correlations.

---

### 1. The Rumor Propagation / Double-Counting Problem

In cyclic mesh networks ($A \leftrightarrow B \leftrightarrow C \leftrightarrow A$):
- Drone A shares target position with Drone B.
- Drone B incorporates it and shares with Drone C.
- Drone C shares it back to Drone A.
- Standard Kalman filtering treats this as a brand new independent observation, falsely inflating confidence until the estimator diverges!

---

### 2. Covariance Intersection (CI) Formulation

Given two state estimates $(\hat{\mathbf{x}}_a, P_a)$ and $(\hat{\mathbf{x}}_b, P_b)$ with unknown cross-covariance $P_{ab}$:

$$P_{\text{fused}}^{-1} = \omega P_a^{-1} + (1 - \omega) P_b^{-1}$$
$$\hat{\mathbf{x}}_{\text{fused}} = P_{\text{fused}} \left( \omega P_a^{-1} \hat{\mathbf{x}}_a + (1 - \omega) P_b^{-1} \hat{\mathbf{x}}_b \right)$$

where $\omega \in [0, 1]$ is optimized to minimize the determinant or trace:
$$\omega^* = \arg\min_\omega \det(P_{\text{fused}}(\omega))$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COVARIANCE INTERSECTION GEOMETRY                         │
│                                                                             │
│                           Covariance Ellipse P_a                            │
│                         .-------------------------.                         │
│                        /      [P_fused CI]         \                        │
│                       |      .------------.         |                       │
│                       |     /  Fused Area  \        |                       │
│                        \   (   (Consistent) )      /                        │
│                         '---\--------------/------'                         │
│                              \            /                                 │
│                               '----------' Covariance Ellipse P_b           │
│                                                                             │
│   • CI ellipse bounds the intersection of both individual ellipses!         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Hands-On Lab & Practical Code References

#### 1. Testing Sensor Degradation & GPS Drift Breakers:
```bash
# Test GPS drift rejection in swarm
ros2 run swarm_demos break_gps_drift
```
