## UAV 05: DECENTRALIZED CONSENSUS PROTOCOLS & DISTRIBUTED AGREEMENT

*Purpose: Achieve collective agreement without a master computer. Master continuous and discrete consensus protocols ($\dot{x}_i = -\sum a_{ij}(x_i - x_j)$), prove asymptotic convergence, and evaluate communication delay margins.*

### Must Answer
- What is the Distributed Consensus Problem (reaching agreement on position, heading, or target state)?
- What is the First-Order Continuous Consensus Protocol, and how does its state vector evolve as $\mathbf{\dot{x}} = -L \mathbf{x}$?
- Why does the state converge exponentially to the average of initial states: $\lim_{t \to \infty} x_i(t) = \frac{1}{N} \sum x_k(0)$?
- What is the Second-Order Consensus Protocol for coordinating both position and velocity simultaneously?
- What is the maximum allowable communication delay ($\tau_{\max} < \frac{\pi}{2 \lambda_N}$) before consensus destabilizes into violent oscillations?

### Key Insight
Decentralized consensus allows 50 autonomous drones to agree on a common flight heading or shared mission objective purely through local neighbor differences without any leader or central server.

---

### 1. First-Order Continuous Consensus

Let each drone $i$ maintain a local continuous state $x_i(t) \in \mathbb{R}$ (such as desired flight altitude or heading angle).
The local decentralized control law is:

$$\dot{x}_i(t) = -\sum_{j \in \mathcal{N}_i} a_{ij} (x_i(t) - x_j(t))$$

Stacking all states into vector $\mathbf{x} = [x_1, \dots, x_N]^T$:
$$\mathbf{\dot{x}}(t) = -L \mathbf{x}(t)$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CONSENSUS CONVERGENCE FLOW                         │
│                                                                             │
│   Initial Dispersed States:                                                 │
│   x_1(0) = 10.0m,  x_2(0) = 4.0m,  x_3(0) = 1.0m                           │
│                           │                                                 │
│                           ▼ (\dot{x} = -L x)                                │
│   Exponential Convergence: x_i(t) = e^{-L t} x(0)                           │
│                           │                                                 │
│                           ▼ (Rate governed by \lambda_2)                    │
│   Final Shared Consensus: x_1 = x_2 = x_3 = 5.0m (Exact Average!)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Second-Order Flocking Consensus (Position + Velocity)

For physical quadrotors moving with inertia, each drone must synchronize both position and velocity:

$$\mathbf{\ddot{p}}_i = -\sum_{j \in \mathcal{N}_i} a_{ij} \left[ (\mathbf{p}_i - \mathbf{p}_j) + \gamma (\mathbf{v}_i - \mathbf{v}_j) \right]$$

where $\gamma > 0$ is the velocity alignment damping gain.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Running Leader-Follower Consensus Demo:
```bash
# Run Demo 03: Leader-follower consensus tracking
ros2 run swarm_demos demo_03_leader_follower
```
- Source: [`ros2_drone_swarm_kit/src/swarm_formation/swarm_formation/leader_follower_node.py`](../../Ros2%20learning%20kits/ros2_drone_swarm_kit/src/swarm_formation/swarm_formation/leader_follower_node.py)
