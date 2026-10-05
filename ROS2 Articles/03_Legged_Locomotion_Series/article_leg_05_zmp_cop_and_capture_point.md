## LEG 05: ZMP, CENTER OF PRESSURE (COP) & CAPTURE POINT DYNAMICS

*Purpose: Master dynamic stability metrics. Formulate the Zero Moment Point (ZMP), contrast it with the Center of Pressure (CoP), derive the Divergent Component of Motion (DCM) / Capture Point, and use Capture Steps for push recovery.*

### Must Answer
- What is the Zero Moment Point (ZMP), and why does dynamic equilibrium require the ZMP to stay inside the support polygon?
- What is the difference between Center of Mass (CoM), Center of Pressure (CoP), and Zero Moment Point (ZMP)?
- What is the Divergent Component of Motion (DCM) / Capture Point ($\boldsymbol{\xi} = \mathbf{x} + \frac{\mathbf{\dot{x}}}{\omega_0}$)?
- What is the Instantaneous Capture Point (ICP), and how does it determine where the robot MUST step to stop falling?
- How does the robot recover from aggressive external pushes using Capture Point stepping?

### Key Insight
The Center of Mass tells you where the robot *is*; the Capture Point tells you where the robot *is going to fall* unless it places a foot directly at that spot.

---

### 1. The Zero Moment Point (ZMP)

The **Zero Moment Point (ZMP)** is the point on the ground where the total horizontal tipping moment produced by inertial and gravitational forces equals zero:

$$x_{\text{zmp}} = x_{\text{CoM}} - \frac{\ddot{x}_{\text{CoM}}}{\ddot{z}_{\text{CoM}} + g} z_{\text{CoM}}$$
$$y_{\text{zmp}} = y_{\text{CoM}} - \frac{\ddot{y}_{\text{CoM}}}{\ddot{z}_{\text{CoM}} + g} z_{\text{CoM}}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ZMP DYNAMIC STABILITY                              │
│                                                                             │
│   • As long as ZMP \in Support Polygon: Ground reaction forces can          │
│     completely balance body inertia; robot will NOT tip over.               │
│   • When ZMP reaches Support Polygon boundary: Robot begins tipping over    │
│     the contact edge.                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Capture Point (Divergent Component of Motion)

Pratt et al. (2006) decomposed the 2nd-order unstable LIPM equation ($\ddot{x} = \omega_0^2 x$) into two decoupled 1st-order systems: a stable converging mode and an unstable diverging mode (**DCM / Capture Point** $\boldsymbol{\xi}$):

$$\boldsymbol{\xi} = \mathbf{x}_{\text{CoM}} + \frac{\mathbf{\dot{x}}_{\text{CoM}}}{\omega_0}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAPTURE POINT PUSH RECOVERY                         │
│                                                                             │
│                  Current CoM                                                │
│                       o ───▶ Velocity \dot{x}                               │
│                      /                                                      │
│                     /                                                       │
│                    /                                                        │
│                   o ─────────────────────────────▶ o                        │
│             Current Stance Foot              Capture Point \xi              │
│                                              (Place Foot HERE to Stop!)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Push Recovery Step Placement:
If an external disturbance pushes the robot with impulse $\Delta \mathbf{v}$, the Capture Point instantly shifts:
$$\Delta \boldsymbol{\xi} = \frac{\Delta \mathbf{v}}{\omega_0}$$
The swing leg controller immediately overrides its default foothold and targets $\mathbf{p}_{\text{foot}} = \boldsymbol{\xi}$, capturing the fall in a single step!

---

### 3. Hands-On Lab & Practical Code References

#### 1. Running Dynamic Balance Demo:
```bash
# Run Demo 03: Dynamic balance controller under external perturbations
ros2 run quadruped_demos demo_03_balance
```

