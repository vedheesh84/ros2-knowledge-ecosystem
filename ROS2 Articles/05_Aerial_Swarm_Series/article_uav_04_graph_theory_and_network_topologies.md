## UAV 04: GRAPH THEORY & DYNAMIC NETWORK TOPOLOGIES FOR SWARMS

*Purpose: Master the mathematics of multi-agent connectivity. Formulate graph representations of robot swarms, derive the Adjacency Matrix $A$, Degree Matrix $D$, and Graph Laplacian $L = D - A$, and analyze Algebraic Connectivity ($\lambda_2$).*

### Must Answer
- How is a multi-UAV swarm modeled as a dynamic communication graph $\mathcal{G}(t) = (\mathcal{V}, \mathcal{E}(t))$?
- What is the difference between Directed Graphs (Digraphs) and Undirected Graphs in communication?
- What is the Graph Laplacian Matrix $L = D - A$, and what are its fundamental mathematical properties?
- What is the Fiedler Value / Algebraic Connectivity ($\lambda_2(L)$), and why does $\lambda_2 > 0$ guarantee network connectivity?
- How do dynamic communication range limits ($d_{ij} \le r_{\text{comm}}$) alter graph edges during flight?

### Key Insight
The second-smallest eigenvalue of the Graph Laplacian ($\lambda_2$) measures the speed and robustness of information diffusion across the swarm; if $\lambda_2 = 0$, the network has fractured into isolated sub-swarms.

---

### 1. Graph Theoretical Representation of Swarms

Let a swarm of $N$ drones be vertices $\mathcal{V} = \{1, 2, \dots, N\}$.
An edge $(i, j) \in \mathcal{E}(t)$ exists if Drone $i$ can transmit packets to Drone $j$ (e.g. distance $\|\mathbf{p}_i - \mathbf{p}_j\| \le R_{\text{comm}}$).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SWARM COMMUNICATION GRAPH                          │
│                                                                             │
│                       [Drone 1] ═══════════ [Drone 2]                       │
│                           ║                      ║                          │
│                           ║  Dynamic Edge (r)    ║                          │
│                           ║                      ║                          │
│                       [Drone 4] ═══════════ [Drone 3]                       │
│                                                                             │
│   • Adjacency Matrix A: a_ij = 1 if connected, 0 otherwise.                 │
│   • Degree Matrix D: d_ii = \sum_j a_ij (number of active neighbors).       │
│   • Laplacian Matrix L = D - A.                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Graph Laplacian $L = D - A$

For an undirected connected graph:
$$L = \begin{bmatrix} d_1 & -a_{12} & \dots & -a_{1N} \\ -a_{21} & d_2 & \dots & -a_{2N} \\ \vdots & \vdots & \ddots & \vdots \\ -a_{N1} & -a_{N2} & \dots & d_N \end{bmatrix}$$

#### Key Properties of $L$:
1. $L$ is symmetric and positive semi-definite ($L \ge 0$).
2. The row sums of $L$ are always zero: $L \mathbf{1} = \mathbf{0}$.
3. The eigenvalues satisfy: $0 = \lambda_1 \le \lambda_2 \le \lambda_3 \le \dots \le \lambda_N$.
4. **Spectral Theorem**: $\lambda_2(L) > 0$ **if and only if the communication graph is connected**.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Inspecting Multi-Drone Namespacing:
- Launch File: [`ros2_drone_swarm_kit/src/drone_bringup/launch/swarm_3drones.launch.py`](../../Ros2%20learning%20kits/ros2_drone_swarm_kit/src/drone_bringup/launch/swarm_3drones.launch.py)
- Run Demo 02: `ros2 run swarm_demos demo_02_multi_drone_namespacing`
