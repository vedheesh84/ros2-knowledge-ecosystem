## ARM 16: CONTACT MECHANICS, GRASP SYNTHESIS & TACTILE SENSING

*Purpose: Master the physics of physical interaction. Understand what happens when the gripper contacts an object, analyze friction cones, contrast Form Closure with Force Closure, evaluate grasp stability, and implement current-based stall detection and tactile feedback.*

### Must Answer
- What is the difference between Kinematic Planning (free space) and Manipulation (constrained contact dynamics)?
- What is Coulomb's Friction Cone model, and how does it define whether a grasped object will slip or hold?
- What is the difference between Form Closure (geometric trapping) and Force Closure (friction balance)?
- How do back-EMF current spikes and motor effort feedback detect physical contact without expensive force-torque sensors?
- What are tactile sensor arrays, and how do they estimate contact normals and slip velocity?

### Key Insight
Motion planning avoids contact with the environment; manipulation intentionally establishes and maintains contact to exert controlled wrenches without crushing the object or dropping it.

---

### 1. Contact Mechanics & Coulomb Friction Cones

When a parallel gripper finger contacts an object surface with normal force $f_n$, the maximum tangential friction force $f_t$ before slippage is governed by Coulomb's law:

$$|f_t| \le \mu f_n$$

where $\mu$ is the static coefficient of friction.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FRICTION CONE GEOMETRY                           │
│                                                                             │
│                        Contact Normal f_n                                   │
│                                ▲                                            │
│                                │   /                                        │
│                        \       │  /  Friction Cone                          │
│                         \      │ /   Half-angle \alpha = \arctan(\mu)        │
│                          \     │/                                           │
│                 ───────────o───┴────────── Contact Surface                  │
│                             \                                               │
│                              ▼ Total Contact Force F                        │
│                                                                             │
│   • Inside Cone: No slip (Static equilibrium holds).                        │
│   • Outside Cone: Object slips out of grasp.                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

The contact force vector $\mathbf{f}$ must lie strictly inside the friction cone:
$$\|\mathbf{f}_t\| \le \mu (\mathbf{f} \cdot \mathbf{n})$$

---

### 2. Form Closure vs. Force Closure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FORM CLOSURE VS. FORCE CLOSURE                        │
│                                                                             │
│   FORM CLOSURE (Geometric Immobility):                                      │
│   The geometric shape of the fingers completely locks the object in place.  │
│   It resists ANY external wrench \mathbf{w} \in \mathbb{R}^6 purely through │
│   rigid body contact normals, even if \mu = 0 (zero friction).              │
│                                                                             │
│   FORCE CLOSURE (Friction-Dependent Balance):                               │
│   The fingers squeeze the object such that the internal contact forces and  │
│   friction cones can balance ANY external wrench \mathbf{w} \in \mathbb{R}^6│
│   subject to positive normal forces (f_n > 0).                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Current-Based Stall Detection & Grasp Validation

In low-cost articulated manipulators without multi-axis force-torque load cells, we estimate contact force using **motor current (effort feedback)**:

$$\tau_{\text{motor}} = K_t \cdot I_{\text{armature}}$$

where $K_t$ is the motor torque constant ($\text{N}\cdot\text{m}/\text{A}$).

#### The Grasp Verification Algorithm:
1. Command parallel gripper to close toward position $0.0$ (fully closed).
2. Monitor motor current / effort $I(t)$ at $50\text{ Hz}$.
3. **If position stops changing ($\dot{q} \approx 0$) AND current rises above threshold ($I > I_{\text{contact}}$)**:
   $\implies$ **Object Contact Confirmed** (Successful Grasp).
4. **If position reaches $0.0$ WITHOUT current spike**:
   $\implies$ **Missed Grasp** (Fingers closed empty).

---

### 4. Hands-On Lab & Practical Code References

#### 1. Inspecting Gripper Action Protocol:
- Action Server: [`ros2_arm_kit/src/arm_manipulation/arm_manipulation/gripper_action_server.py`](../../Ros2%20learning%20kits/ros2_arm_kit/src/arm_manipulation/arm_manipulation/gripper_action_server.py)
- Run Gripper Demo: `ros2 run arm_demos demo_04_gripper_action`
- Breaker Test: `ros2 run arm_demos break_gripper_stall`


