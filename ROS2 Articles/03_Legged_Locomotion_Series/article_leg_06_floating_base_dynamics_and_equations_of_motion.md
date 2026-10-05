## LEG 06: FLOATING-BASE DYNAMICS & MULTI-CONTACT EQUATIONS OF MOTION

*Purpose: Formulate the complete rigid-body equations of motion for floating-base systems. Master unactuated spatial coordinates, contact constraints, the operational space mass matrix, and torque mapping.*

### Must Answer
- How are floating-base equations of motion written in block-matrix form ($M(\mathbf{q}) \mathbf{\ddot{q}} + \mathbf{h} = B \boldsymbol{\tau} + J_c^T \boldsymbol{\lambda}$)?
- What is the difference between the 6 unactuated floating-base degrees of freedom and the $n$ actuated joint coordinates?
- What are contact holonomic constraints ($J_c \mathbf{\dot{q}} = \mathbf{0}$), and how do they eliminate unactuated DOF?
- What are Ground Reaction Force Lagrange Multipliers ($\boldsymbol{\lambda} \in \mathbb{R}^{3k}$)?
- How do Whole-Body Controllers invert the constrained dynamic equations in real time?

### Key Insight
Because the floating base has no motors connecting it to the world, all chassis motion must be generated indirectly through the contact Jacobian transpose $J_c^T \boldsymbol{\lambda}$ acting at the feet.

---

### 1. The Block Floating-Base Equations of Motion

Let generalized coordinates be $\mathbf{q} = [\mathbf{q}_b^T, \mathbf{q}_j^T]^T \in SE(3) \times \mathbb{R}^{12}$, where $\mathbf{q}_b$ represents the unactuated 6-DOF floating base and $\mathbf{q}_j$ represents the 12 leg joints.

$$\begin{bmatrix} M_{bb}(\mathbf{q}) & M_{bj}(\mathbf{q}) \\ M_{jb}(\mathbf{q}) & M_{jj}(\mathbf{q}) \end{bmatrix} \begin{bmatrix} \mathbf{\ddot{q}}_b \\ \mathbf{\ddot{q}}_j \end{bmatrix} + \begin{bmatrix} \mathbf{h}_b(\mathbf{q}, \mathbf{\dot{q}}) \\ \mathbf{h}_j(\mathbf{q}, \mathbf{\dot{q}}) \end{bmatrix} = \begin{bmatrix} \mathbf{0}_{6 \times 12} \\ I_{12 \times 12} \end{bmatrix} \boldsymbol{\tau} + \begin{bmatrix} J_{c, b}^T \\ J_{c, j}^T \end{bmatrix} \boldsymbol{\lambda}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FLOATING-BASE DYNAMICS BREAKDOWN                        │
│                                                                             │
│   Top Row (Base Dynamics - Unactuated):                                     │
│   M_bb \ddot{q}_b + M_bj \ddot{q}_j + h_b = J_c,b^T \lambda                 │
│   • Base accelerations are driven ENTIRELY by contact reaction forces \lambda! │
│                                                                             │
│   Bottom Row (Joint Dynamics - Actuated):                                   │
│   M_jb \ddot{q}_b + M_jj \ddot{q}_j + h_j = \tau + J_c,j^T \lambda          │
│   • Joint motors must balance inertia, gravity, AND contact reaction forces.│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Contact Constraints & Closed Kinematic Loops

When $k$ feet are firmly planted on the ground without slipping:
$$\mathbf{p}_{c, i}(\mathbf{q}) = \text{constant} \implies J_c(\mathbf{q}) \mathbf{\dot{q}} = \mathbf{0}$$

Differentiating with respect to time yields the contact acceleration constraint:
$$J_c(\mathbf{q}) \mathbf{\ddot{q}} + \dot{J}_c(\mathbf{q}) \mathbf{\dot{q}} = \mathbf{0}$$

This algebraic constraint binds the unactuated floating chassis to the ground, allowing optimization algorithms (such as Convex MPC and Whole-Body QP) to compute the exact motor torques $\boldsymbol{\tau}$ needed to achieve any desired chassis trajectory.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Hardware Interface & Joint Effort Pipeline:
- Hardware Interface: [`ros2_quadruped_kit/src/quadruped_hardware/src/leg_hardware.cpp`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_hardware/src/leg_hardware.cpp)
- Breaker Test: `ros2 run quadruped_demos break_contact.py`

