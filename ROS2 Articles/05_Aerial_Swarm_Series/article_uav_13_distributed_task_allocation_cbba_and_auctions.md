## UAV 13: DISTRIBUTED TASK ALLOCATION: CBBA & MARKET AUCTIONS

*Purpose: Allocate complex multi-drone missions autonomously without centralized servers. Master the Consensus-Based Bundle Algorithm (CBBA), decentralized market-based auction bidding, bundle construction, and consensus conflict resolution.*

### Must Answer
- How does a swarm of 10 drones assign 30 inspection targets or search tasks amongst themselves autonomously?
- Why do simple greedy task assignments cause redundant duplicate assignments and wasted energy?
- What is the Consensus-Based Bundle Algorithm (CBBA, Choi, Brunet & How, 2009)?
- What are the two alternating phases of CBBA (Phase 1: Bundle Construction $\to$ Phase 2: Consensus Conflict Resolution)?
- How does CBBA guarantee $50\%$ polynomial-time optimality with zero central communication bottleneck?

### Key Insight
CBBA combines local greedy score optimization (where each drone builds a bundle of desired tasks) with decentralized consensus (where drones compare winning bids over peer-to-peer radio), resolving assignment conflicts in polynomial time.

---

### 1. The Decentralized Task Allocation Problem

Let $M$ tasks $\mathcal{T} = \{1, 2, \dots, M\}$ be distributed in 3D space, and let $N$ drones $\mathcal{V} = \{1, \dots, N\}$ bid on them.
- Each drone $i$ maintains a **task bundle** $\mathbf{b}_i$ (ordered sequence of tasks).
- Each drone maintains a **winning bids list** $\mathbf{y}_i \in \mathbb{R}^M$ and **winning agents list** $\mathbf{z}_i \in \mathbb{Z}^M$.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CBBA ALGORITHM TWO-PHASE LOOP                      │
│                                                                             │
│   PHASE 1: BUNDLE CONSTRUCTION (Local Optimization)                         │
│   • Drone i greedily evaluates marginal reward for all available tasks.     │
│   • Inserts highest-scoring task into bundle b_i; updates local bid y_i.    │
│                                                                             │
│                                │                                            │
│                                ▼ (Broadcast winning bids over ROS2 DDS)     │
│                                                                             │
│   PHASE 2: CONSENSUS CONFLICT RESOLUTION (Decentralized Agreement)          │
│   • Drone i receives bid lists from neighbors j \in N_i.                    │
│   • Compares bids: If neighbor j has a higher bid for task k:               │
│     ==> Drone i outbid! Yields task k and drops all subsequent tasks in b_i.│
│                                                                             │
│   • Loop repeats until all bids achieve global consensus!                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Hands-On Lab & Practical Code References

#### 1. Testing Swarm Task Allocation:
```bash
# Run Demo 06: Swarm decentralized area coverage & task execution
ros2 run swarm_demos demo_06_swarm_area_coverage
```
