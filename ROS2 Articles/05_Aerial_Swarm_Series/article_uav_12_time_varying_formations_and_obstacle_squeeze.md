## UAV 12: TIME-VARYING FORMATIONS & OBSTACLE SQUEEZE CONTRACTION

*Purpose: Navigate complex geometric environments. Master time-varying formation scaling, apply Contraction Theory to squeeze through narrow apertures, and maintain network connectivity in cluttered obstacle fields.*

### Must Answer
- How does a wide swarm formation navigate through a narrow doorway, tunnel, or dense forest?
- What is Formation Contraction / Dilation ($\boldsymbol{\delta}_i(t) = s(t) \cdot \boldsymbol{\delta}_i^0$), and how does scaling factor $s(t) \in [0.2, 1.0]$ compress the swarm?
- What are Contraction Metrics, and how do they prove that a compressed swarm remains dynamically stable without collisions?
- How does the swarm maintain peer-to-peer radio connectivity during spatial deformation?
- How do downwash aerodynamic interactions change as inter-drone spacing shrinks below $0.4\text{ m}$?

### Key Insight
Rather than breaking formation into chaotic individual navigation, the swarm dynamically scales its geometry via a continuous scaling parameter $s(t)$, squeezing through obstacles as an organized coherent unit.

---

### 1. Formation Scaling & Contraction Formulation

Let $\boldsymbol{\delta}_i^0$ be the nominal formation offset of Drone $i$. When approaching an obstacle constriction of width $W_{\text{gap}}$:

$$\boldsymbol{\delta}_i(t) = s(t) \cdot \boldsymbol{\delta}_i^0$$

where scaling factor $s(t)$ satisfies:
$$s(t) = \min\left( 1.0, \frac{W_{\text{gap}} - 2 r_{\text{safety}}}{\text{Span}(\boldsymbol{\delta}^0)} \right)$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OBSTACLE SQUEEZE CONTRACTION                       │
│                                                                             │
│     Wide V-Formation (s = 1.0)           Narrow Aperture (s = 0.3)          │
│                                                ║         ║                  │
│            o                                   ║    o    ║                  │
│           / \                                  ║   / \   ║                  │
│          o   o                                 ║  o   o  ║                  │
│         /     \                                ║         ║                  │
│        o       o                               ║         ║                  │
│                                                ║         ║                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Hands-On Lab & Practical Code References

#### 1. Testing Swarm Formation Squeeze:
```bash
# Launch swarm simulation and command formation squeeze
ros2 run swarm_demos demo_04_dynamic_formation
```
