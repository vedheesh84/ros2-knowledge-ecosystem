## LEG 02: 3-DOF LEG KINEMATICS, WORKSPACE & ANALYTICAL SOLVERS

*Purpose: Master the analytical geometry and differential kinematics of robotic legs. Derive the Forward Kinematics (FK), Inverse Kinematics (IK), and Leg Jacobian for standard 3-DOF legs (Coxa, Thigh, Shin), and compute the reachable foot workspace envelope.*

### Must Answer
- What is the canonical 3-DOF serial leg topology (Hip Abduction/Adduction, Hip Pitch, Knee Pitch)?
- How do we derive closed-form algebraic Forward Kinematics from hip origin to foot tip?
- How do we derive closed-form analytical Inverse Kinematics for any 3D foot position $[x, y, z]^T$?
- What is the Leg Jacobian matrix $J_{\text{leg}}(\mathbf{q})$, and how does it map joint velocities to Cartesian foot velocities?
- How does the Leg Jacobian transpose ($J^T$) map Cartesian ground reaction forces directly to motor torques ($\boldsymbol{\tau} = J^T \mathbf{f}$)?

### Key Insight
Because each leg is a 3-DOF serial chain, closed-form analytical IK executes in $< 2\text{ microseconds}$ without numerical iterations, enabling hard real-time $1000\text{ Hz}$ joint trajectory tracking.

---

### 1. Canonical 3-DOF Leg Geometry

Every mammalian/insectoid quadruped leg comprises 3 revolute joints:
1. **$q_1$ (Hip Abduction / Adduction - Roll)**: Rotates in the coronal plane ($\pm x$).
2. **$q_2$ (Hip Pitch / Thigh)**: Rotates in the sagittal plane ($\pm y$).
3. **$q_3$ (Knee Pitch / Shin)**: Rotates in the sagittal plane ($\pm y$).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            3-DOF LEG TOPOLOGY                               │
│                                                                             │
│     [Hip Base / Shoulder]                                                   │
│            o ◄── joint_1 (Hip Roll / Abduction: q_1)                        │
│            │ ◄── Link: Coxa Length l_1                                      │
│            o ◄── joint_2 (Hip Pitch / Thigh: q_2)                           │
│             \                                                               │
│              \  ◄── Link: Thigh Length l_2                                  │
│               \                                                             │
│                o ◄── joint_3 (Knee Pitch / Shin: q_3)                       │
│               /                                                             │
│              /  ◄── Link: Shin Length l_3                                   │
│             /                                                               │
│            o ◄── [Foot Tip / Contact Sphere] (x, y, z)                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Analytical Inverse Kinematics Derivation

Given a desired foot coordinate $[x_f, y_f, z_f]^T$ relative to the hip base frame:

#### Step 1: Solve Hip Abduction Angle ($q_1$):
In the $Y-Z$ coronal plane:
$$q_1 = \text{atan2}(y_f, -z_f) - \text{atan2}(l_1, \sqrt{y_f^2 + z_f^2 - l_1^2})$$

#### Step 2: Project into the Leg Pitch Plane ($X-Z'$):
$$r_x = x_f, \quad r_z = \sqrt{y_f^2 + z_f^2 - l_1^2}$$
$$D = \frac{r_x^2 + r_z^2 - l_2^2 - l_3^2}{2 l_2 l_3}$$

#### Step 3: Solve Knee Pitch Angle ($q_3$):
$$q_3 = \text{atan2}(-\sqrt{1 - D^2}, D) \quad (\text{Knee-Backward / Mammalian})$$

#### Step 4: Solve Hip Pitch Angle ($q_2$):
$$q_2 = \text{atan2}(-r_x, r_z) - \text{atan2}(l_3 \sin q_3, l_2 + l_3 \cos q_3)$$

---

### 3. The Leg Jacobian & Virtual Work Principle

The Leg Jacobian $J \in \mathbb{R}^{3 \times 3}$ relates joint velocities to foot tip velocity:
$$\mathbf{v}_{\text{foot}} = J(\mathbf{q}) \mathbf{\dot{q}}$$

By the **Principle of Virtual Work** ($\boldsymbol{\tau}^T \mathbf{\dot{q}} = \mathbf{f}^T \mathbf{v}_{\text{foot}}$):
$$\boldsymbol{\tau}_{\text{joint}} = J^T(\mathbf{q}) \cdot \mathbf{f}_{\text{contact}}$$

This equation allows whole-body controllers to instantly map desired 3D ground reaction forces $\mathbf{f}_{\text{grf}} = [f_x, f_y, f_z]^T$ into feedforward motor torques!

---

### 4. Hands-On Lab & Practical Code References

#### 1. Kinematics Node Source Code:
- Leg Solver Node: [`ros2_quadruped_kit/src/quadruped_locomotion/quadruped_locomotion/gait_scheduler.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_locomotion/quadruped_locomotion/gait_scheduler.py)
- Run Demo 01: `ros2 run quadruped_demos demo_01_joint_control`

