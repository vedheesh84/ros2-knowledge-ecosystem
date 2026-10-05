## LEG 04: INVERTED PENDULUM & LINEAR INVERTED PENDULUM (LIPM) DYNAMICS

*Purpose: Master the core reduced-order model of dynamic balance. Derive the 3D Inverted Pendulum equations of motion, formulate the Linear Inverted Pendulum Model (LIPM) under constant CoM height, and analyze orbital energy.*

### Must Answer
- Why do full multi-body dynamic equations fail to run in real-time on robot microcontrollers?
- What is Reduced-Order Modeling, and how does the Inverted Pendulum model represent legged balance?
- What assumption linearizes the non-linear inverted pendulum into the Linear Inverted Pendulum Model (LIPM)?
- What is the LIPM natural frequency ($\omega_0 = \sqrt{g / z_0}$), and what does it physically represent?
- What is Orbital Energy ($E_{\text{orbital}}$), and how does it determine whether a pendulum will come to rest or tip over?

### Key Insight
By constraining the Center of Mass to move on a constant horizontal plane ($z = z_0$), the non-linear vertical acceleration terms decouple, transforming chaotic multi-body dynamics into a simple, linear hyperbolic differential equation.

---

### 1. The 3D Inverted Pendulum Model

Let a point mass $m$ represent the total robot body at position $\mathbf{x} = [x, y, z]^T$, supported by a massless leg pivoting at foot stance point $\mathbf{p} = [p_x, p_y, 0]^T$.

$$\ddot{x} = \frac{g}{z} (x - p_x) + \frac{f_x}{m}$$
$$\ddot{y} = \frac{g}{z} (y - p_y) + \frac{f_y}{m}$$
$$\ddot{z} = -g + \frac{f_z}{m}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LINEAR INVERTED PENDULUM MODEL (LIPM)                    │
│                                                                             │
│                      Constant Height Plane z = z_0                          │
│        ═════════════════════════o════════════════════════════               │
│                                /| CoM Mass m                                │
│                               / |                                           │
│                              /  |                                           │
│                 Leg Length L/   | Height z_0                                │
│                            /    |                                           │
│                           /     |                                           │
│                          o──────┴──────────────────────────                 │
│                     Foot Pivot (p_x, 0)                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Linear Inverted Pendulum Equation

Under the constraint $\ddot{z} = 0 \implies z(t) = z_0 = \text{constant}$:

$$\ddot{x}(t) = \omega_0^2 (x(t) - p_x)$$
$$\ddot{y}(t) = \omega_0^2 (y(t) - p_y)$$

where $\omega_0 = \sqrt{\frac{g}{z_0}}$ is the **eigenfrequency** of the pendulum.

#### Analytical Solution (Hyperbolic Motion):
$$x(t) = (x_0 - p_x) \cosh(\omega_0 t) + \frac{\dot{x}_0}{\omega_0} \sinh(\omega_0 t) + p_x$$
$$\dot{x}(t) = \omega_0 (x_0 - p_x) \sinh(\omega_0 t) + \dot{x}_0 \cosh(\omega_0 t)$$

---

### 3. Orbital Energy & Phase-Plane Trajectories

Multiplying the differential equation by $\dot{x}$ and integrating yields the conserved **Orbital Energy**:

$$E_{\text{orbital}} = \frac{1}{2} \dot{x}^2 - \frac{1}{2} \omega_0^2 (x - p_x)^2$$

- **$E_{\text{orbital}} < 0$**: CoM lacks sufficient kinetic energy to cross the stance foot; it stops and reverses.
- **$E_{\text{orbital}} = 0$**: CoM reaches the apex directly above $p_x$ with zero velocity as $t \to \infty$.
- **$E_{\text{orbital}} > 0$**: CoM crosses the stance foot with positive velocity (sustained forward locomotion).

---

### 4. Hands-On Lab & Practical Code References

#### 1. Inspecting Balance Controller:
- Controller Source: [`ros2_quadruped_kit/src/quadruped_control/quadruped_control/joint_pd_controller.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_control/quadruped_control/joint_pd_controller.py)

