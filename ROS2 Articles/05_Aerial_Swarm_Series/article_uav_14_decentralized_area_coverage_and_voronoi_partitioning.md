## UAV 14: DECENTRALIZED AREA COVERAGE & VORONOI PARTITIONING

*Purpose: Optimize multi-agent spatial coverage. Formulate Voronoi Partitions in 2D and 3D Euclidean space, implement Lloyd's Algorithm for Centroidal Voronoi Tessellation (CVT), and achieve optimal sensor coverage over irregular search zones.*

### Must Answer
- How do multiple search-and-rescue drones partition a $1\text{ km}^2$ disaster zone to search it in minimum time?
- What is a Voronoi Partition $V_i = \{ \mathbf{q} \in \mathcal{Q} \mid \|\mathbf{q} - \mathbf{p}_i\| \le \|\mathbf{q} - \mathbf{p}_j\|, \forall j \ne i \}$?
- What is a Centroidal Voronoi Tessellation (CVT), and why does moving each drone toward the geometric centroid of its cell minimize coverage cost?
- What is Lloyd's Algorithm, and how does it drive decentralized spatial dispersion using only local neighbor boundary exchanges?
- How do non-uniform density distributions ($\phi(\mathbf{q})$) concentrate drones over high-priority search zones?

### Key Insight
By simply driving toward the mass centroid of its own Voronoi polygon ($\mathbf{\dot{p}}_i = -k (\mathbf{p}_i - \mathbf{C}_{V_i})$), the swarm automatically distributes itself across any irregular search domain without central coordination.

---

### 1. Voronoi Partitioning & Lloyd's Descent

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VORONOI CELL DECENTRALIZATION                      │
│                                                                             │
│             ┌──────────────────────┬──────────────────────┐                 │
│             │                      │                      │                 │
│             │     Voronoi Cell V_1 │     Voronoi Cell V_2 │                 │
│             │            o (Drone) │            o         │                 │
│             │            │         │            │         │                 │
│             │            ▼ (Moves) │            ▼         │                 │
│             │            * Centroid│            * Centroid│                 │
│             │                      │                      │                 │
│             ├──────────────────────┼──────────────────────┤                 │
│             │                      │                      │                 │
│             │     Voronoi Cell V_3 │     Voronoi Cell V_4 │                 │
│             │            o ──▶ *   │            o ──▶ *   │                 │
│             │                      │                      │                 │
│             └──────────────────────┴──────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### The Centroid Formulation:
$$\mathbf{C}_{V_i} = \frac{\int_{V_i} \mathbf{q} \phi(\mathbf{q}) d\mathbf{q}}{\int_{V_i} \phi(\mathbf{q}) d\mathbf{q}}$$

#### Distributed Control Law:
$$\mathbf{v}_i = K_{\text{cover}} (\mathbf{C}_{V_i} - \mathbf{p}_i)$$

By LaSalle's Invariance Principle, the swarm provably converges to the critical points of the global coverage cost function $\mathcal{H}(\mathbf{P}) = \sum \int_{V_i} \|\mathbf{q} - \mathbf{p}_i\|^2 d\mathbf{q}$.

---

### 2. Hands-On Lab & Practical Code References

#### 1. Running Area Coverage Demo:
- Source: [`ros2_drone_swarm_kit/src/swarm_demos/swarm_demos/demo_06_swarm_area_coverage.py`](../../Ros2%20learning%20kits/ros2_drone_swarm_kit/src/swarm_demos/swarm_demos/demo_06_swarm_area_coverage.py)
