## ARM 10: CONFIGURATION SPACE (C-SPACE) & OBSTACLE TOPOLOGY

*Purpose: Master the fundamental concept that makes high-dimensional motion planning possible. Learn why planning in Cartesian workspace fails, how 3D obstacles transform into complex non-convex shapes in Configuration Space (C-Space), and understand the topology of robotic joints.*

### Must Answer
- What is Configuration Space (C-Space / $\mathcal{C}$), and why does a point in C-space represent the entire state of the robot?
- What is the difference between Task Space $\mathcal{X} \subset \mathbb{R}^3 \times SO(3)$ and Configuration Space $\mathcal{Q} \subset \mathbb{R}^n$?
- How does a simple 3D bounding box obstacle in the workspace become a twisted, complex, non-convex obstacle in C-space ($\mathcal{C}_{\text{obs}}$)?
- What is the topological structure of revolute joint space ($T^n = S^1 \times S^1 \times \dots$), and why is Euclidean distance misleading?
- Why is explicitly calculating $\mathcal{C}_{\text{obs}}$ computationally intractable ($NP$-hard), and how does sampling bypass this barrier?

### Key Insight
In the Cartesian workspace, the robot is a complex geometric body that can collide along any link; in Configuration Space, the robot shrinks to an infinitesimal point $\mathbf{q} \in \mathcal{C}$, while the obstacles grow into $\mathcal{C}_{\text{obs}}$.

---

### 1. The Configuration Space Concept

A **Configuration** $\mathbf{q}$ is a complete specification of the position of every point on the robot.
The **Configuration Space $\mathcal{C}$** is the $n$-dimensional manifold of all possible configurations $\mathbf{q} \in \mathcal{C}$.

For an $n$-revolute joint arm:
$$\mathcal{C} = [q_{1,\min}, q_{1,\max}] \times [q_{2,\min}, q_{2,\max}] \times \dots \times [q_{n,\min}, q_{n,\max}] \subset \mathbb{T}^n$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WORKSPACE VS. CONFIGURATION SPACE                        │
│                                                                             │
│         WORKSPACE W \subset \mathbb{R}^3               CONFIGURATION SPACE \mathcal{C}      │
│                                                                             │
│            Link 2                                                           │
│             /‾‾‾\         [Obstacle]              q_2                       │
│    Link 1  /     \                                 ▲   \mathcal{C}_{free}           │
│     /‾‾‾\ /       \                                │   /‾‾‾‾‾‾‾\            │
│    o     o         ▼ TCP                           │  / \mathcal{C}_{obs} \           │
│    │                                               │  \       /             │
│   === (Base)                                       │   \_____/   • q_{goal} │
│                                                    │  • q_{start}            │
│   (Robot is a complex 3D shape                     └────────────────────►   │
│    colliding with 3D obstacles)                    (Robot is a 0D POINT) q_1│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Free Space ($\mathcal{C}_{\text{free}}$) and Obstacle Space ($\mathcal{C}_{\text{obs}}$)

Let $\mathcal{W}$ be the 3D physical workspace, $\mathcal{A}(\mathbf{q}) \subset \mathcal{W}$ be the volume occupied by the robot links at configuration $\mathbf{q}$, and $\mathcal{O}_i \subset \mathcal{W}$ be workspace obstacles.

The **Obstacle Space $\mathcal{C}_{\text{obs}}$** is the set of all configurations where the robot collides with an obstacle or with itself:
$$\mathcal{C}_{\text{obs}} = \{ \mathbf{q} \in \mathcal{C} \ | \ (\mathcal{A}(\mathbf{q}) \cap \mathcal{O} \ne \emptyset) \ \lor \ (\mathcal{A}_i(\mathbf{q}) \cap \mathcal{A}_j(\mathbf{q}) \ne \emptyset, \ i \ne j) \}$$

The **Free Space $\mathcal{C}_{\text{free}}$** is the valid region for motion:
$$\mathcal{C}_{\text{free}} = \mathcal{C} \setminus \mathcal{C}_{\text{obs}}$$

#### The Core Problem of Motion Planning:
Find a continuous curve $\tau: [0, 1] \to \mathcal{C}_{\text{free}}$ such that $\tau(0) = \mathbf{q}_{\text{start}}$ and $\tau(1) = \mathbf{q}_{\text{goal}}$.

---

### 3. Why Explicit Geometry Computation Fails

Attempting to compute the exact analytical algebraic boundaries of $\mathcal{C}_{\text{obs}}$ for a 6-DOF arm requires solving complex systems of high-degree polynomial inequalities (Minkowski sums in 6D).
- John Canny (1987) proved that exact algebraic C-space path planning is **PSPACE-complete** ($O(n^d)$).
- **The Breakthrough**: Instead of computing $\mathcal{C}_{\text{obs}}$ explicitly, modern planners use **Collision Detection Oracles** (e.g. FCL): Given a single candidate state $\mathbf{q}$, return `True` (collision) or `False` (free) in microseconds.

---

### 4. Hands-On Lab & Practical Code References

#### 1. Visualizing Collision Objects in MoveIt2:
```bash
# Launch MoveIt2 planning scene
ros2 launch arm_bringup arm_sim.launch.py
```
In RViz, add a collision cylinder into the Planning Scene and observe how MoveIt2 plans around it in C-space.


