## UAV 11: DYNAMIC FORMATION SWITCHING & THE HUNGARIAN MATCHING ALGORITHM

*Purpose: Seamlessly morph swarm geometry in mid-air. Master dynamic formation switching (V-Shape $\leftrightarrow$ Line $\leftrightarrow$ Circle $\leftrightarrow$ Grid), formulate the Linear Assignment Problem (LAP), and eliminate trajectory intersections using the Hungarian Algorithm.*

### Must Answer
- Why does transitioning between different formations cause mid-air collisions if drones choose targets arbitrarily?
- What is the Linear Assignment Problem (LAP), and how does the Cost Matrix $C_{ij} = \|\mathbf{p}_{i, \text{current}} - \mathbf{p}_{j, \text{target}}\|^2$ minimize total swarm flight distance?
- How does the Hungarian Algorithm ($O(N^3)$) find the globally optimal, collision-free slot assignment?
- How do parameterized Bézier transition trajectories ensure smooth velocity and acceleration during formation morphing?
- How does the ROS2 Formation Manager service orchestrate synchronized formation switches across the swarm?

### Key Insight
When switching from a V-Shape to a Line, assigning drones to target slots arbitrarily causes their flight paths to cross in mid-air; the Hungarian algorithm guarantees a collision-free optimal assignment that minimizes energy and transit time.

---

### 1. The Dynamic Formation Transition Problem

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FORMATION MORPHING & ASSIGNMENT                        │
│                                                                             │
│   FORMATION 1: V-SHAPE (Aerodynamic Cruise)                                 │
│                   [Drone 1]                                                 │
│                  /         \                                                │
│         [Drone 2]           [Drone 3]                                       │
│                                                                             │
│                          │                                                  │
│                          ▼ (Hungarian Matching Min \sum ||p_i - g_j||^2)    │
│                                                                             │
│   FORMATION 2: HORIZONTAL LINE (Sensor Sweep Search)                        │
│         [Slot 1] ──────── [Slot 2] ──────── [Slot 3]                        │
│            o                 o                 o                            │
│                                                                             │
│   • Optimal target slot assignment eliminates trajectory crossing!          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Hungarian Assignment Algorithm

Let cost matrix $C \in \mathbb{R}^{N \times N}$ be defined by:
$$C_{ij} = \|\mathbf{p}_i(t_{\text{switch}}) - \mathbf{g}_j\|^2$$

Find permutation matrix $X \in \{0, 1\}^{N \times N}$:
$$\min_X \sum_{i=1}^{N} \sum_{j=1}^{N} C_{ij} X_{ij} \quad \text{subject to: } \sum_{i=1}^N X_{ij} = 1, \quad \sum_{j=1}^N X_{ij} = 1$$

---

### 3. Hands-On Lab & Practical Code References

#### 1. Formation Manager Source Code:
- Formation Manager: [`ros2_drone_swarm_kit/src/swarm_formation/swarm_formation/formation_manager_node.py`](../../Ros2%20learning%20kits/ros2_drone_swarm_kit/src/swarm_formation/swarm_formation/formation_manager_node.py)
- Run Demo 04: `ros2 run swarm_demos demo_04_dynamic_formation`
