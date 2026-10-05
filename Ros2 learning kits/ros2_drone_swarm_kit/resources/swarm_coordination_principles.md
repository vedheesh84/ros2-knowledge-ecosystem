# Swarm Coordination Principles

**Mathematical Foundations of Multi-Agent Aerial Swarms**

---

## 1. Multi-Agent Namespacing & State Architecture

In a swarm with $N$ aerial nodes, each agent executes its own isolated stack under dynamic namespace $\text{/drone\_}i$:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SWARM MESH ARCHITECTURE                            │
│                                                                             │
│      [Central Dispatch / Leader] ──/swarm/formation_mode (Broadcast)        │
│                    │                                                        │
│         ┌──────────┼──────────┐                                             │
│         ▼          ▼          ▼                                             │
│    [/drone_0]  [/drone_1] [/drone_2] ...                                    │
│    (Leader)    (Follower) (Follower)                                        │
│         │          │          │                                             │
│         └──────────┼──────────┘                                             │
│                    ▼                                                        │
│      [Inter-Agent Collision Repulsion Fields]                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Leader-Follower Geometric Offsets

Let $\mathbf{p}_0(t) = [x_0(t), y_0(t), z_0(t)]^T$ be the leader position and $\mathbf{d}_i = [\Delta x_i, \Delta y_i, \Delta z_i]^T$ be the follower offset:

$$\mathbf{p}_i^{\text{des}}(t) = \mathbf{p}_0(t) + R(\psi_0) \mathbf{d}_i$$

where $R(\psi_0)$ is the 3D yaw rotation matrix aligning the formation with the leader's heading.

---

## 3. Artificial Potential Fields for Collision Avoidance

To prevent inter-agent collisions, each agent $i$ computes a repulsive force $\mathbf{F}_{i,j}^{\text{rep}}$ against every neighboring agent $j$:

$$\mathbf{F}_{i,j}^{\text{rep}} = \begin{cases} k_{\text{rep}} \left( \frac{1}{\|\mathbf{p}_i - \mathbf{p}_j\|} - \frac{1}{d_{\text{safe}}} \right) \frac{\mathbf{p}_i - \mathbf{p}_j}{\|\mathbf{p}_i - \mathbf{p}_j\|^3}, & \text{if } \|\mathbf{p}_i - \mathbf{p}_j\| \le d_{\text{safe}} \\ \mathbf{0}, & \text{if } \|\mathbf{p}_i - \mathbf{p}_j\| > d_{\text{safe}} \end{cases}$$

The total commanded velocity vector is:
$$\mathbf{v}_i^{\text{cmd}} = \mathbf{v}_i^{\text{formation}} + \sum_{j \ne i} \mathbf{F}_{i,j}^{\text{rep}}$$
