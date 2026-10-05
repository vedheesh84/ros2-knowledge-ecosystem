## LEG 14: CONVEX MODEL PREDICTIVE CONTROL (MPC) & QP FORCE OPTIMIZATION

*Purpose: Master the state-of-the-art control technique for dynamic legged locomotion: Convex Model Predictive Control (MPC). Formulate the discrete Quadratic Program (QP), enforce friction pyramids and unilateral contact constraints, and optimize ground reaction forces across a receding horizon ($N=10$).*

### Must Answer
- What is Model Predictive Control (MPC), and why is it superior to classical PID controllers for legged balance?
- How is the continuous SRBD state-space discretized across a future horizon $N = 10$ ($0.3\text{ seconds}$)?
- What is the Cost Function $J(\mathbf{x}, \mathbf{u}) = \sum (\mathbf{x}_k - \mathbf{x}_k^{\text{ref}})^T Q (\mathbf{x}_k - \mathbf{x}_k^{\text{ref}}) + \mathbf{u}_k^T R \mathbf{u}_k$?
- How is Coulomb's friction cone linearized into a 4-sided Friction Pyramid constraint?
- How do Quadratic Programming (QP) solvers (OSQP, qpOASES) solve the optimal forces in $< 2\text{ ms}$?

### Key Insight
Instead of reacting *after* an error occurs, MPC simulates the robot physics $0.3\text{ seconds}$ into the future at every $10\text{ ms}$ control loop, choosing ground forces that proactively stabilize the body across all upcoming footholds.

---

### 1. The Receding Horizon Optimization

At every control cycle ($t = k \cdot \Delta t$, e.g. at $100\text{ Hz}$):
1. Measure the current estimated robot state $\mathbf{x}_0 = \mathbf{x}(t)$.
2. Solve a constrained Quadratic Program (QP) over $N=10$ discrete steps:
   $$\min_{\mathbf{u}_0, \dots, \mathbf{u}_{N-1}} \sum_{k=0}^{N-1} \left( \|\mathbf{x}_{k+1} - \mathbf{x}_{k+1}^{\text{ref}}\|_Q^2 + \|\mathbf{u}_k\|_R^2 \right)$$
3. **Execute ONLY the first control action $\mathbf{u}_0^*$** on the robot.
4. Shift the horizon forward by one time step and repeat!

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CONVEX MPC RECEDING HORIZON (N = 10)                     │
│                                                                             │
│   t=0 (Now)       t=1 (30ms)      t=2 (60ms)        ...        t=N (300ms)  │
│      o ──────────────▶ o ──────────────▶ o ──────────────▶ ... ──────▶ o    │
│      │                 │                 │                             │    │
│      ▼                 ▼                 ▼                             ▼    │
│   [Forces u_0*]     [Forces u_1]      [Forces u_2]                  [Forces]│
│      │                                                                      │
│   (EXECUTED NOW!)                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Linear Friction Pyramid Constraints

To prevent foot slippage and guarantee push-only (unilateral) ground contact:
1. **Unilateral Normal Force**: $f_{z, \min} \le f_{z, i} \le f_{z, \max}$ ($5\text{ N} \le f_{z} \le 180\text{ N}$).
2. **Friction Pyramid (Linearized Cone)**:
   $$|f_{x, i}| \le \mu f_{z, i} \iff -\mu f_{z, i} \le f_{x, i} \le \mu f_{z, i}$$
   $$|f_{y, i}| \le \mu f_{z, i} \iff -\mu f_{z, i} \le f_{y, i} \le \mu f_{z, i}$$
3. **Contact Schedule Constraint**: If leg $i$ is in **SWING**, force its ground reaction force strictly to zero: $\mathbf{f}_i = \mathbf{0}$.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Running Convex MPC Locomotion Demo:
```bash
# Launch quadruped simulation
ros2 launch quadruped_bringup quadruped_sim.launch.py

# In another terminal, run Convex MPC locomotion demo
ros2 run quadruped_demos demo_05_locomotion
```
- Source: [`ros2_quadruped_kit/src/quadruped_locomotion/quadruped_locomotion/mpc_controller/mpc_node.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_locomotion/quadruped_locomotion/mpc_controller/mpc_node.py)

