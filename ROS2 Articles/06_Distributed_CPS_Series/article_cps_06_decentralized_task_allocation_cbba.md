# Article CPS-06: Decentralized Task Allocation via Consensus-Based Bundle Algorithm (CBBA)

**Pedagogical Layer:** Distributed Optimization & Market Algorithms  
**Focus Area:** CBBA Two-Phase Auction Protocol, Marginal Score Discounting, Conflict Resolution, and Mathematical Convergence  
**Associated Package:** `cps_coordination/cps_coordination/cbba_auction_node.py`

---

## 1. Introduction: Why Market Auctions?

In distributed multi-robot systems, relying on a central coordinator introduces a **Single Point of Failure (SPOF)**. If the coordinator crashes or Wi-Fi connectivity partitions the fleet, the robots become paralyzed.

The **Consensus-Based Bundle Algorithm (CBBA)** is a polynomial-time, decentralized market auction protocol that converges to a conflict-free task allocation using only local peer-to-peer communication.

---

## 2. The Two-Phase CBBA Mechanics

```text
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: BUNDLE BUILDING (Local Greedy Construction)                   │
│ • Each robot builds an ordered bundle b_i of tasks up to capacity L_t. │
│ • Computes marginal score: c_ij = S(p_i ⊕ {j}) - S(p_i)               │
│ • Adds task with maximum marginal reward to local bundle.              │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: CONSENSUS RESOLUTION (Peer-to-Peer Communication)             │
│ • Robots exchange winning bid lists y_i and winning agent lists z_i.  │
│ • Rule-based conflict arbitration updates local bids.                  │
│ • Outbid robots release conflicting tasks and downstream assignments.  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Marginal Score Formulation

For a task $j$ located at position $\mathbf{x}_j$, the score awarded to agent $i$ at position $\mathbf{x}_i$ is discounted exponentially by Euclidean travel distance:
$$c_{ij} = R_j \cdot e^{-\lambda \cdot \|\mathbf{x}_i - \mathbf{x}_j\|}$$
where $R_j$ is the base task reward and $\lambda$ is the distance penalty factor.

---

## 4. Convergence & Optimality Guarantees

CBBA guarantees:
1. **Convergence**: The algorithm terminates in a finite number of communication rounds bounded by the network diameter $D$.
2. **Suboptimality Bound**: Achieves a guaranteed **$50\%$ optimality bound** ($1/2$-approximation) relative to the global integer linear programming (ILP) optimum:
   $$\sum_{i} S_i(p_i) \ge \frac{1}{2} S_{\text{optimal}}$$

---

## 5. Summary & Key Takeaways

- CBBA eliminates central dispatch bottlenecks, providing mathematical fault tolerance.
- In [Article CPS-07](article_cps_07_peer_collision_avoidance_and_costmaps.md), we address physical spatial collisions between peer robots.
