## LEG 15: WHOLE-BODY CONTROL (WBC) & OPERATIONAL SPACE QP

*Purpose: Bridge high-level forces with low-level joint actuators. Master Whole-Body Control (WBC), operational space formulation, hierarchical task prioritization (Nullspace Projection), and instantaneous torque generation at $500\text{ Hz}$.*

### Must Answer
- What is the Whole-Body Control (WBC) layer, and why is MPC alone insufficient for joint-level tracking?
- How does WBC reconcile optimal ground reaction forces ($\mathbf{f}_{\text{MPC}}^*$) with high-speed swing foot tracking ($\mathbf{\ddot{p}}_{\text{swing}}$)?
- What is Hierarchical Quadratic Programming (HQP), and how do strict task priorities prevent lower tasks from violating balance?
- What are the standard 3 task priorities in quadruped WBC (Task 1: Contact/Friction, Task 2: Trunk 6-DOF pose, Task 3: Swing foot)?
- How does the WBC output feedforward torques $\boldsymbol{\tau}_{\text{ff}}$ and joint PD setpoints ($q^*, \dot{q}^*$) at $500\text{ Hz}$?

### Key Insight
Convex MPC plans low-frequency ($100\text{ Hz}$) optimal ground forces assuming rigid bodies; Whole-Body Control runs at $500\text{ Hz}$ to track those forces while simultaneously driving swing feet through air and managing joint limit nullspaces.

---

### 1. The Hierarchical Task Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HIERARCHICAL TASK PRIORITY                         │
│                                                                             │
│   TASK 1 (HIGHEST PRIORITY - HARD CONSTRAINTS):                             │
│   • Contact non-slip condition: J_c \ddot{q} + \dot{J}_c \dot{q} = 0        │
│   • Friction pyramid bounds: |f_x,y| \le \mu f_z, f_z > 0                   │
│   • Motor torque limits: |\tau_i| \le \tau_max                              │
│                                                                             │
│   TASK 2 (MEDIUM PRIORITY - TRUNK DYNAMICS):                                │
│   • Track desired body linear and angular acceleration (\ddot{p}_b, \dot{\omega}_b)
│   • Match optimal MPC contact forces: \lambda \approx \mathbf{f}_MPC^*       │
│                                                                             │
│   TASK 3 (LOWER PRIORITY - SWING FOOT TRACKING):                            │
│   • Track Bézier swing trajectory: \ddot{p}_foot = K_p (p* - p) + K_d ...   │
│                                                                             │
│   TASK 4 (NULLSPACE POSTURE):                                               │
│   • Stay near nominal joint centers (q \approx q_nom).                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Operational Space Formulation

The WBC solves an instantaneous Quadratic Program at $500\text{ Hz}$ for generalized accelerations $\mathbf{\ddot{q}}$ and contact forces $\boldsymbol{\lambda}$:

$$\min_{\mathbf{\ddot{q}}, \boldsymbol{\lambda}} \left( \|\mathbf{\ddot{x}}_{\text{trunk}} - \mathbf{\ddot{x}}_{\text{trunk}}^{\text{des}}\|_{W_1}^2 + \|\boldsymbol{\lambda} - \mathbf{f}_{\text{MPC}}^*\|_{W_2}^2 + \|\mathbf{\ddot{p}}_{\text{swing}} - \mathbf{\ddot{p}}_{\text{swing}}^{\text{des}}\|_{W_3}^2 \right)$$
$$\text{subject to: } \quad M(\mathbf{q}) \mathbf{\ddot{q}} + \mathbf{h} = B \boldsymbol{\tau} + J_c^T \boldsymbol{\lambda}$$
$$\text{and: } \quad J_c \mathbf{\ddot{q}} + \dot{J}_c \mathbf{\dot{q}} = \mathbf{0}, \quad \boldsymbol{\lambda} \in \mathcal{F}_{\text{friction}}$$

Once $\mathbf{\ddot{q}}^*$ and $\boldsymbol{\lambda}^*$ are computed, joint motor torques are calculated directly from the bottom rows of the dynamic equation:
$$\boldsymbol{\tau}_{\text{cmd}} = M_{jb} \mathbf{\ddot{q}}_b^* + M_{jj} \mathbf{\ddot{q}}_j^* + \mathbf{h}_j - J_{c, j}^T \boldsymbol{\lambda}^*$$

---

### 3. Hands-On Lab & Practical Code References

#### 1. Whole-Body Controller Source:
- Controller Source: [`ros2_quadruped_kit/src/quadruped_control/quadruped_control/whole_body_controller.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_control/quadruped_control/whole_body_controller.py)
- Physical Microcontroller Firmware: [`ros2_quadruped_kit/arduino/quadruped_controller/quadruped_controller.ino`](../../Ros2%20learning%20kits/ros2_quadruped_kit/arduino/quadruped_controller/quadruped_controller.ino)
- Desktop Pseudo-Hardware Emulator: [`ros2_quadruped_kit/scripts/pseudo_quadruped_emulator.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/scripts/pseudo_quadruped_emulator.py)
- Automated Verification Suite: [`ros2_quadruped_kit/scripts/test_quadruped_kit.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/scripts/test_quadruped_kit.py)

