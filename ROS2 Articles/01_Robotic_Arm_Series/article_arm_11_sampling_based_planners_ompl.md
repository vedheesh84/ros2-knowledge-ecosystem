## ARM 11: SAMPLING-BASED MOTION PLANNERS: OMPL, RRT, RRT* & RRTCONNECT

*Purpose: Master sampling-based motion planning algorithms. Learn why grid search suffers from the curse of dimensionality, how random sampling explores non-convex C-space, and analyze PRM, RRT, RRTConnect, and asymptotically optimal RRT*.*

### Must Answer
- Why do classical search algorithms ($A^*$, Dijkstra) fail in 5-DOF and 6-DOF robotic arms?
- What is the Open Motion Planning Library (OMPL), and how is it integrated into ROS2 / MoveIt2?
- How does the Rapidly-exploring Random Tree (RRT) algorithm explore high-dimensional C-space?
- Why is Bidirectional RRTConnect the industry default for industrial and tabletop manipulation?
- What is Asymptotic Optimality in RRT*, and how does path rewiring minimize trajectory length?

### Key Insight
Sampling-based planners trade completeness for speed: they do not guarantee finding a path in fixed time, but they are **Probabilistically Complete**—if a collision-free path exists, the probability of finding it approaches 1.0 as iterations increase.

---

### 1. The Curse of Dimensionality in Grid Search

Consider a grid-based search ($A^*$) over an arm configuration space.
If each joint range is discretized into 100 intervals:
- 2-DOF planar arm: $100^2 = 10,000$ grid cells (Trivial to search).
- 6-DOF industrial arm: $100^6 = 1,000,000,000,000$ (1 Trillion cells). Memory exhaustion and exponential search time.

**Sampling-based planners** do not discretize space into a grid. They sample random points in continuous C-space $\mathbf{q}_{\text{rand}} \sim \mathcal{C}$ and connect them using a local planner.

---

### 2. The Basic RRT Algorithm (LaValle, 1998)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             THE RRT ALGORITHM                               │
│                                                                             │
│             1. Sample random configuration: q_{rand} \sim \mathcal{C}               │
│             2. Find nearest tree vertex:   q_{near} = \arg\min ||v - q_{rand}||     │
│             3. Step along direction:       q_{new} = q_{near} + \epsilon \frac{q_{rand}-q_{near}}{||...||} │
│             4. Collision check edge:       if CollisionFree(q_{near}, q_{new})      │
│                                                AddVertex(q_{new})                   │
│                                                AddEdge(q_{near}, q_{new})           │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Why RRT Works: The Voronoi Bias
RRT has an inherent mathematical bias toward the largest unvisited regions of C-space. The probability that a node $v$ is selected for expansion is directly proportional to the volume of its **Voronoi cell**. This drives rapid exploration away from obstacles.

---

### 3. Bidirectional RRTConnect: The Industry Gold Standard

In manipulation, standard RRT is slow because growing a single tree toward a narrow goal configuration in high dimensions is difficult.

**RRTConnect (Kuffner & LaValle, 2000)** grows **TWO trees simultaneously**:
- Tree $A$ rooted at $\mathbf{q}_{\text{start}}$
- Tree $B$ rooted at $\mathbf{q}_{\text{goal}}$

At each iteration, Tree $A$ expands toward $\mathbf{q}_{\text{rand}}$, and Tree $B$ immediately attempts to extend toward the newly created vertex $\mathbf{q}_{\text{new}, A}$. When the two trees meet, a complete path is found.

#### Why RRTConnect dominates MoveIt2:
- Finds solutions in **$5 - 50\text{ ms}$** for 6-DOF arms.
- Bypasses narrow geometric bottlenecks in cluttered environments.

---

### 4. OMPL Configuration in `ros2_arm_kit`

In `ros2_arm_kit/src/arm_moveit/config/ompl_planning.yaml`:
```yaml
planning_plugins:
  - ompl_interface/OMPLPlanner
request_adapters:
  - default_planning_request_adapters/AddTimeOptimalParameterization
  - default_planning_request_adapters/ResolveConstraintFrames
  - default_planning_request_adapters/FixWorkspaceBounds

arm:
  default_planner_config: RRTConnectkConfigDefault
  planner_configs:
    RRTConnectkConfigDefault:
      type: geometric::RRTConnect
      range: 0.05       # Max step size (\epsilon) in radians
```

---

### 5. Hands-On Lab & Practical Code References

#### 1. Executing OMPL Planning:
```bash
# Launch MoveIt simulation
ros2 launch arm_bringup arm_sim.launch.py

# Run MoveIt trajectory demo
ros2 run arm_demos demo_05_moveit_planning
```


