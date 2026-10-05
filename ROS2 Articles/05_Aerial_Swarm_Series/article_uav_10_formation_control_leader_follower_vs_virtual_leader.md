## UAV 10: FORMATION CONTROL: LEADER-FOLLOWER VS. VIRTUAL LEADER

*Purpose: Compare fundamental formation architectures. Formulate Leader-Follower tracking, Virtual Leader consensus, and Distributed Rigid Formations, and analyze error propagation across long chains.*

### Must Answer
- What are the two dominant formation control paradigms (Physical Leader-Follower vs. Virtual Leader Consensus)?
- What is Error Propagation / String Instability in long leader-follower chains (where small leader perturbations amplify down the line)?
- How does Virtual Leader Consensus eliminate the single-point-of-failure of a physical leader drone?
- How do relative offset vectors $\boldsymbol{\delta}_{ij}$ define arbitrary geometric patterns (V-Shape, Circle, Line, Wedge)?
- How does the formation manager track global group velocity while maintaining millimeter inter-drone relative geometry?

### Key Insight
In Leader-Follower, if the leader crashes, the entire swarm is paralyzed; in Virtual Leader Consensus, all drones track a decentralized mathematical reference point, allowing any drone to drop out without affecting formation integrity.

---

### 1. Leader-Follower vs. Virtual Leader Topologies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FORMATION TOPOLOGY COMPARISON                          │
│                                                                             │
│   PHYSICAL LEADER-FOLLOWER:               VIRTUAL LEADER CONSENSUS:         │
│                                                                             │
│           [Physical Leader]                      [Virtual Reference Trajectory]
│              /        \                               /      |      \       │
│             ▼          ▼                             ▼       ▼       ▼      │
│        [Follower 1]  [Follower 2]               [Drone 1] [Drone 2] [Drone 3]
│             │          │                            ▲        ▲       ▲      │
│             ▼          ▼                            └────────┴───────┘      │
│        [Follower 3]  [Follower 4]                   (Peer-to-Peer Consensus) │
│                                                                             │
│   • Cons: Leader is SPOF; string error.   • Pros: Robust, no physical SPOF. │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Relative Formation Control Law

For each drone $i$ with desired offset $\boldsymbol{\delta}_i$ from the group center:

$$\mathbf{\ddot{p}}_i = \mathbf{\ddot{p}}_{\text{ref}} - K_p [(\mathbf{p}_i - \boldsymbol{\delta}_i) - \mathbf{p}_{\text{ref}}] - K_v [(\mathbf{v}_i) - \mathbf{v}_{\text{ref}}] - \sum_{j \in \mathcal{N}_i} a_{ij} [(\mathbf{p}_i - \mathbf{p}_j) - (\boldsymbol{\delta}_i - \boldsymbol{\delta}_j)]$$

---

### 3. Hands-On Lab & Practical Code References

#### 1. Leader-Follower Formation Node:
- Source: [`ros2_drone_swarm_kit/src/swarm_formation/swarm_formation/leader_follower_node.py`](../../Ros2%20learning%20kits/ros2_drone_swarm_kit/src/swarm_formation/swarm_formation/leader_follower_node.py)
