## ARM 06: DIFFERENTIAL KINEMATICS, JACOBIANS & SINGULARITY ANALYSIS

*Purpose: Master differential kinematics in robotics. Derive the geometric Jacobian matrix, map joint velocities to Cartesian end-effector velocities, quantify manipulability using the Yoshikawa index, analyze singular configurations, and implement singularity-robust inverses (Damped Least Squares).*

### Must Answer
- What is the Manipulator Jacobian matrix $J(\mathbf{q})$, and how does it relate joint velocities $\mathbf{\dot{q}}$ to Cartesian linear and angular velocities $\mathbf{v}, \boldsymbol{\omega}$?
- What is a kinematic singularity ($\det(J) = 0$), and what happens to joint torques and velocities when a robot approaches one?
- What are boundary singularities (full extension) vs. interior singularities (wrist alignment)?
- What is the Yoshikawa Manipulability Index $w(\mathbf{q}) = \sqrt{\det(J J^T)}$, and how does it define the manipulability ellipsoid?
- How does the Damped Least Squares (DLS) pseudo-inverse prevent infinite velocity command spikes near singularities?

### Key Insight
The Jacobian is the local linear derivative of the forward kinematics; when the Jacobian loses full rank, the robot loses the ability to move in one or more Cartesian directions, regardless of how fast the motors spin.

---

### 1. The Manipulator Jacobian Matrix

Let $\mathbf{x} = f(\mathbf{q})$ be the forward kinematics mapping. Differentiating with respect to time using the multivariable chain rule:

$$\mathbf{\dot{x}} = \frac{\partial f(\mathbf{q})}{\partial \mathbf{q}} \mathbf{\dot{q}} = J(\mathbf{q}) \mathbf{\dot{q}}$$

The Jacobian $J(\mathbf{q}) \in \mathbb{R}^{6 \times n}$ decomposes into linear velocity ($J_v$) and angular velocity ($J_\omega$) submatrices:

$$\begin{bmatrix} \mathbf{v} \\ \boldsymbol{\omega} \end{bmatrix} = \begin{bmatrix} J_v(\mathbf{q}) \\ J_\omega(\mathbf{q}) \end{bmatrix} \begin{bmatrix} \dot{q}_1 \\ \dot{q}_2 \\ \vdots \\ \dot{q}_n \end{bmatrix}$$

For a revolute joint $i$ with joint axis unit vector $\mathbf{z}_{i-1}$ and position vector $\mathbf{p}_{i-1}$:
$$J_{v,i} = \mathbf{z}_{i-1} \times (\mathbf{p}_{\text{tcp}} - \mathbf{p}_{i-1})$$
$$J_{\omega,i} = \mathbf{z}_{i-1}$$

---

### 2. Planar Jacobian for the 5-DOF Articulated Arm

In the vertical arm plane ($r, z$), the linear velocity is controlled by joints $q_2, q_3, q_4$:

$$\begin{bmatrix} \dot{r} \\ \dot{z} \end{bmatrix} = J_{\text{planar}}(\mathbf{q}) \begin{bmatrix} \dot{q}_2 \\ \dot{q}_3 \\ \dot{q}_4 \end{bmatrix}$$

Differentiating the forward kinematics equations:
$$J_{11} = \frac{\partial r}{\partial q_2} = -a_2 \sin(q_2) - a_3 \sin(q_2+q_3) - d_5 \sin(q_2+q_3+q_4)$$
$$J_{12} = \frac{\partial r}{\partial q_3} = -a_3 \sin(q_2+q_3) - d_5 \sin(q_2+q_3+q_4)$$
$$J_{13} = \frac{\partial r}{\partial q_4} = -d_5 \sin(q_2+q_3+q_4)$$

$$J_{21} = \frac{\partial z}{\partial q_2} = a_2 \cos(q_2) + a_3 \cos(q_2+q_3) + d_5 \cos(q_2+q_3+q_4)$$
$$J_{22} = \frac{\partial z}{\partial q_3} = a_3 \cos(q_2+q_3) + d_5 \cos(q_2+q_3+q_4)$$
$$J_{23} = \frac{\partial z}{\partial q_4} = d_5 \cos(q_2+q_3+q_4)$$

---

### 3. Kinematic Singularities & Physical Manifestations

A singularity occurs when the Jacobian matrix loses full row rank:
$$\det(J(\mathbf{q}) J^T(\mathbf{q})) = 0$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TYPES OF SINGULARITIES                            │
│                                                                             │
│   1. BOUNDARY SINGULARITY (Full Arm Extension):                             │
│      Occurs when q_3 = 0. The arm is stretched straight out.                │
│      Loss of DOF: Cannot move radially outward (\dot{r} > 0 is impossible). │
│                                                                             │
│   2. INTERIOR SINGULARITY (Wrist-Shoulder Alignment):                       │
│      Occurs when wrist center aligns directly with the shoulder axis.       │
│      Loss of DOF: Infinite base yaw velocity required for lateral motion.   │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### What happens near a singularity?
Under standard Cartesian velocity control ($\mathbf{\dot{q}} = J^{-1} \mathbf{v}_{\text{cmd}}$), as $\det(J) \to 0$, $J^{-1} \to \infty$. A modest commanded TCP velocity of $0.05\text{ m/s}$ will command joints to rotate at hundreds of radians per second, causing:
1. Extreme motor current draw and power supply brownout.
2. Violent mechanical oscillation and gearbox tooth stripping.
3. Controller trajectory tracking error aborts.

---

### 4. Quantitative Manipulability: The Yoshikawa Ellipsoid

Tsuneo Yoshikawa (1985) introduced the **Manipulability Index** $w(\mathbf{q})$ to measure how easily an arm can move in arbitrary directions:

$$w(\mathbf{q}) = \sqrt{\det(J(\mathbf{q}) J^T(\mathbf{q}))} = \sigma_1 \sigma_2 \dots \sigma_m$$

where $\sigma_i$ are the singular values of $J$.
- $w(\mathbf{q}) > 0$: High manipulability (isotropic velocity generation).
- $w(\mathbf{q}) \to 0$: Near singularity (severely restricted motion).

---

### 5. Damped Least Squares (DLS / Levenberg-Marquardt Damping)

To prevent velocity blow-up near singularities, production controllers use the **Damped Least Squares pseudo-inverse**:

$$J^* = J^T (J J^T + \lambda^2 I)^{-1}$$

where $\lambda > 0$ is a damping parameter.
- **Far from singularity**: $\lambda^2 \approx 0 \implies J^* \approx J^\dagger$ (exact tracking).
- **Near singularity**: $\lambda^2$ bounds the inversion, sacrificing exact Cartesian tracking to ensure joint velocities remain smooth and bounded.

---

### 6. Hands-On Lab & Practical Code References

#### 1. Inspecting the Jacobian Node:
- Source: [`ros2_arm_kit/src/arm_kinematics/arm_kinematics/jacobian.py`](../../Ros2%20learning%20kits/ros2_arm_kit/src/arm_kinematics/arm_kinematics/jacobian.py)
```python
# Compute manipulability and check for singularities
jac = ArmJacobian()
w = jac.manipulability(q2=0.5, q3=-0.4, q4=0.2)
print(f"Yoshikawa Manipulability: {w:.4f}")
```


