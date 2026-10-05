## LEG 03: SUPPORT POLYGONS & STATIC STABILITY CRITERIA

*Purpose: Understand static equilibrium in multi-legged systems. Formulate the Support Polygon, compute Center of Mass (CoM) projections, evaluate static stability margins, and contrast 4-legged crawl with 6-legged tripod gaits.*

### Must Answer
- What is a Support Polygon, and how is its convex hull defined by grounded feet?
- What is the Static Stability Criterion ($P_{\text{CoM}} \in \text{Support Polygon}$)?
- What is the Static Stability Margin ($d_{\text{margin}}$), and how does it quantify tipping resistance?
- Why can a 4-legged robot only achieve static stability by lifting one leg at a time (Crawl gait)?
- How do 6-legged hexapods achieve perpetual static stability during high-speed tripod locomotion?

### Key Insight
Static stability requires the vertical projection of the Center of Mass to reside strictly inside the convex hull of grounded support feet; as soon as a quadruped transitions to a 2-foot trot, static stability vanishes and dynamic balance takes over.

---

### 1. The Support Polygon Convex Hull

Let $\mathcal{S} = \{ \mathbf{p}_1, \mathbf{p}_2, \dots, \mathbf{p}_k \}$ be the 2D ground contact points $(x_i, y_i)$ of all stance legs.
The **Support Polygon** is the 2D convex hull:

$$\mathcal{H} = \text{ConvexHull}(\mathcal{S}) \subset \mathbb{R}^2$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SUPPORT POLYGON GEOMETRY                           │
│                                                                             │
│      Front-Left (p_FL) ────────────────── Front-Right (p_FR)                │
│             │                                    │                          │
│             │        Center of Mass (CoM)        │                          │
│             │                 o                  │                          │
│             │           ◄─ d_margin ─►           │                          │
│             │                                    │                          │
│      Rear-Left (p_RL) ─────────────────── Rear-Right (p_RR)                 │
│                                                                             │
│   • 4-Leg Stance: Quadrilateral support area (High stability margin).       │
│   • 3-Leg Stance (Crawl): Triangular support area (Stable if CoM inside).   │
│   • 2-Leg Stance (Trot): Line segment (Zero static area; statically unstable│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Static Stability Margin ($d_{\text{margin}}$)

The **Stability Margin** $S_{\text{margin}}$ is the minimum signed Euclidean distance from the CoM projection $(x_{\text{com}}, y_{\text{com}})$ to any bounding edge of the support polygon:

$$S_{\text{margin}} = \min_{e_i \in \partial \mathcal{H}} \text{dist}(\mathbf{p}_{\text{CoM}}, e_i)$$

- If $S_{\text{margin}} > 0$: The robot is statically stable.
- If $S_{\text{margin}} = 0$: The robot is on the tipping edge.
- If $S_{\text{margin}} < 0$: Gravity produces an overturning torque; the robot falls.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Running Static Stand & Crawl Demos:
```bash
# Launch quadruped simulation
ros2 launch quadruped_bringup quadruped_sim.launch.py

# In another terminal, run static crawl gait demo
ros2 run quadruped_demos demo_02_kinematics
```

