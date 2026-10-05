## UAV 15: COOPERATIVE TARGET TRACKING & DYNAMIC ENCIRCLEMENT

*Purpose: Track dynamic ground targets with multi-UAV teams. Master dynamic encirclement geometry, balance angular spacing around moving targets, and optimize visual sensor baselines for 3D multi-view triangulation.*

### Must Answer
- How do multiple UAVs cooperatively track, surround, and monitor an evasive moving target?
- What is Dynamic Encirclement, and how do drones maintain a constant radius $r_{\text{orbit}}$ while orbiting at speed $v_{\text{orbit}}$?
- How do consensus angular spacing controllers ($\dot{\theta}_i = \omega_0 + \sum a_{ij} \sin(\theta_j - \theta_i - \Delta\theta_{\text{des}})$) distribute drones uniformly around the circle ($360^\circ / N$)?
- How does multi-view visual baseline separation maximize 3D target triangulation precision?
- How does the swarm adapt its orbit center when the target accelerates unexpectedly?

### Key Insight
A single drone tracking a target from above can lose visual contact due to occlusions; three drones orbiting in a balanced $120^\circ$ ring maintain continuous 3D multi-view line-of-sight regardless of building shadows.

---

### 1. Dynamic Encirclement Geometry

Let the target be at $\mathbf{p}_{\text{target}}(t)$.
Each drone $i$ tracks a desired circular orbit of radius $R$:

$$\mathbf{p}_{i, \text{des}}(t) = \mathbf{p}_{\text{target}}(t) + \begin{bmatrix} R \cos\theta_i(t) \\ R \sin\theta_i(t) \\ h_{\text{orbit}} \end{bmatrix}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          COOPERATIVE ENCIRCLEMENT                           │
│                                                                             │
│                                 [Drone 1] (\theta = 0 deg)                  │
│                                     o                                       │
│                                    / \                                      │
│                                   /   \ Radius R                            │
│                                  /     \                                    │
│             (\theta = 240 deg)  /   o   \  (\theta = 120 deg)               │
│                    [Drone 3] o  [Target] o [Drone 2]                        │
│                                                                             │
│   • Dynamic phase consensus maintains exact 120 degree visual separation!   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Hands-On Lab & Practical Code References

#### 1. Testing Encirclement Formations:
- Formation Node: [`ros2_drone_swarm_kit/src/swarm_formation/swarm_formation/formation_manager_node.py`](../../Ros2%20learning%20kits/ros2_drone_swarm_kit/src/swarm_formation/swarm_formation/formation_manager_node.py)
