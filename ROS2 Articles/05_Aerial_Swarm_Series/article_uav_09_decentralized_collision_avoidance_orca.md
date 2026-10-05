## UAV 09: DECENTRALIZED 3D COLLISION AVOIDANCE & ORCA IN $SE(3)$

*Purpose: Guarantee reciprocal collision avoidance in dense airspace. Master the Velocity Obstacle (VO) concept, formulate Optimal Reciprocal Collision Avoidance (ORCA) in 3D Euclidean space, and solve collision-free velocities via Linear Programming.*

### Must Answer
- What is the Velocity Obstacle (VO) cone between two moving aerial vehicles?
- What causes reciprocal oscillations (the "Mirror Dance" deadlock) when two symmetric robots try to avoid each other?
- How does Optimal Reciprocal Collision Avoidance (ORCA) resolve deadlock by having each robot take exactly $50\%$ responsibility?
- How is 3D ORCA formulated as half-plane constraints solved via 3D Linear Programming in $< 0.1\text{ ms}$?
- How do downwash cones (aerodynamic propeller wake turbulence) create asymmetric vertical collision buffers?

### Key Insight
ORCA guarantees collision freedom between hundreds of independent agents without communication by assuming that other agents are also actively choosing velocities outside the reciprocal velocity obstacle.

---

### 1. The Velocity Obstacle (VO) Geometry

Let Drone $A$ have radius $r_A$ at $\mathbf{p}_A$ moving with velocity $\mathbf{v}_A$, and Drone $B$ have radius $r_B$ at $\mathbf{p}_B$ moving with $\mathbf{v}_B$.
The Velocity Obstacle $\text{VO}_{A|B}$ is the cone of relative velocities that will result in a collision within time window $\tau$:

$$\text{VO}_{A|B}^\tau = \{ \mathbf{v} \mid \exists t \in [0, \tau], \quad t \mathbf{v} \in D(\mathbf{p}_B - \mathbf{p}_A, r_A + r_B) \}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VELOCITY OBSTACLE IN 3D                            │
│                                                                             │
│                           Drone B (Obstacle)                                │
│                                  o                                          │
│                                 / \                                         │
│                                /   \                                        │
│                               /  VO \                                       │
│                              /  Cone \                                      │
│                             /         \                                     │
│                            /           \                                    │
│                           o─────────────o                                   │
│                        Drone A                                              │
│                                                                             │
│   • If relative velocity (v_A - v_B) lies INSIDE the cone: COLLISION!       │
│   • ORCA shifts v_A to the closest boundary point on the half-plane.        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Hands-On Lab & Practical Code References

#### 1. Running Collision Breaker Test:
```bash
# Test collision avoidance under head-on trajectories
ros2 run swarm_demos break_swarm_collision
```
