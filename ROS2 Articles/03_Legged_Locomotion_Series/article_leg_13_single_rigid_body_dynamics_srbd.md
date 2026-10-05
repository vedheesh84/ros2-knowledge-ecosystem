## LEG 13: SINGLE RIGID BODY DYNAMICS (SRBD) FOR LOCOMOTION

*Purpose: Master the state-of-the-art dynamic model for quadruped locomotion. Formulate Single Rigid Body Dynamics (SRBD), simplify multi-link inertia into a lumped trunk model, linearize 3D rotational dynamics, and establish net wrench balance.*

### Must Answer
- Why is full-body multi-rigid-body dynamics too non-linear and computationally slow for real-time MPC?
- What is the Single Rigid Body Dynamics (SRBD) assumption (mass of trunk $\gg$ mass of legs)?
- How do 3D translational dynamics ($\mathbf{\ddot{p}} = \frac{1}{m} \sum \mathbf{f}_i - \mathbf{g}$) describe body trajectory?
- How do 3D rotational dynamics ($I \mathbf{\dot{\omega}} = \sum (\mathbf{r}_i \times \mathbf{f}_i)$) describe body roll/pitch/yaw balance?
- How does small-angle linearization transform non-linear Euler equations into a linear state-space system $\mathbf{\dot{x}} = A \mathbf{x} + B \mathbf{u}$?

### Key Insight
Because a quadruped's body trunk comprises $\sim 85\%$ of its total mass, treating the body as a single rigid 3D box floating on massless force-generating vectors enables convex, microsecond-fast optimization.

---

### 1. The Single Rigid Body Assumption

In a $12\text{-kg}$ robotic dog (like MIT Cheetah or Unitree Go1/A1), the body trunk weighs $\sim 10\text{ kg}$, while all 4 legs combined weigh only $\sim 2\text{ kg}$.
Instead of modeling 13 separate rigid bodies (1 trunk + 12 leg links), **SRBD** assumes:
1. All mass $m$ and rotational inertia tensor $I \in \mathbb{R}^{3 \times 3}$ reside in the central trunk.
2. The legs are massless force actuators that apply ground reaction force vectors $\mathbf{f}_i \in \mathbb{R}^3$ at contact footholds $\mathbf{p}_i$.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SINGLE RIGID BODY MODEL TOPOLOGY                        │
│                                                                             │
│                        Mass m, Inertia Tensor I                             │
│                  ┌───────────────────────────────────┐                      │
│                  │            CHASSIS TRUNK          │                      │
│                  └───┬───────────┬───────────┬───┬───┘                      │
│                     /             \           \   \                         │
│                    /               \           \   \                        │
│             r_FL  /            r_FR \     r_RL  \   \ r_RR                  │
│                  ▼                   ▼           ▼   ▼                      │
│                f_FL                f_FR        f_RL f_RR                    │
│             (Foot FL)           (Foot FR)   (Foot RL) (Foot RR)             │
│            ═════════════════════════════════════════════════ Ground Plane   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Equations of Motion in State-Space Form

Let the state vector be $\mathbf{x} = [\boldsymbol{\Theta}^T, \mathbf{p}^T, \boldsymbol{\omega}^T, \mathbf{\dot{p}}^T, g]^T \in \mathbb{R}^{13}$ and control inputs be $\mathbf{u} = [\mathbf{f}_1^T, \mathbf{f}_2^T, \mathbf{f}_3^T, \mathbf{f}_4^T]^T \in \mathbb{R}^{12}$.

$$\mathbf{\dot{p}}(t) = \mathbf{v}(t)$$
$$m \mathbf{\ddot{p}}(t) = \sum_{i=1}^{4} \mathbf{f}_i(t) - m \mathbf{g}$$
$$\mathbf{\dot{\Theta}}(t) \approx \boldsymbol{\omega}(t) \quad (\text{under small Euler angles})$$
$$I_G \boldsymbol{\dot{\omega}}(t) = \sum_{i=1}^{4} (\mathbf{p}_i - \mathbf{p}_{\text{CoM}}) \times \mathbf{f}_i(t) = \sum_{i=1}^{4} [\mathbf{r}_i]_\times \mathbf{f}_i(t)$$

where $[\mathbf{r}_i]_\times$ is the $3 \times 3$ skew-symmetric cross-product matrix.

#### Continuous Linear State-Space Form:
$$\mathbf{\dot{x}}(t) = A_c \mathbf{x}(t) + B_c \mathbf{u}(t)$$

---

### 3. Hands-On Lab & Practical Code References

#### 1. Dynamic Model Formulation:
- Controller Source: [`ros2_quadruped_kit/src/quadruped_locomotion/quadruped_locomotion/mpc_controller/mpc_node.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_locomotion/quadruped_locomotion/mpc_controller/mpc_node.py)

