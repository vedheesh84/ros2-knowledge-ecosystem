## LEG 18: REINFORCEMENT LEARNING & SIM-TO-REAL POLICY TRANSFER

*Purpose: The frontier of physical intelligence in legged robotics. Understand deep reinforcement learning (RL) for locomotion, master Proximal Policy Optimization (PPO), massive parallel simulation (Isaac Gym / MuJoCo), Domain Randomization, and Sim-to-Real policy deployment on physical hardware.*

### Must Answer
- Why has Reinforcement Learning (RL) emerged as a dominant paradigm alongside Model Predictive Control (MPC)?
- How is locomotion framed as a Markov Decision Process (MDP): State $\mathbf{s}_t$, Action $\mathbf{a}_t$, Reward $r_t$?
- What is Proximal Policy Optimization (PPO), and how do thousands of simulated quadrupeds learn in parallel on GPUs?
- What is the Sim-to-Real Reality Gap, and how does Domain Randomization (varying mass, friction, latency) guarantee real-world transfer?
- What is Teacher-Student Policy Distillation for handling privileged terrain information?

### Key Insight
While classical MPC relies on human mathematical simplifications (like SRBD), Reinforcement Learning discovers complex whole-body dynamic reflexes, dynamic jumps, and fall recoveries by experiencing millions of simulated physical interactions across randomized environments.

---

### 1. The RL Locomotion Formulation (MDP)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       REINFORCEMENT LEARNING PIPELINE                       │
│                                                                             │
│   STATE s_t \in \mathbb{R}^{48}:                                            │
│   • Trunk orientation (\mathbf{R}_b), angular velocity (\boldsymbol{\omega})│
│   • Linear velocity (\mathbf{v}_b), joint positions (q), joint velocities (\dot{q})
│   • Previous action (a_{t-1}), velocity command (v_x, v_y, \omega_z)        │
│                                                                             │
│   ACTION a_t \in \mathbb{R}^{12}:                                           │
│   • Desired target joint angles q_{i, \text{target}} \implies \tau_i = K_p (q^* - q) ...
│                                                                             │
│   REWARD r_t:                                                               │
│   • + Tracking command: \exp(-\|v - v_{\text{cmd}}\|^2)                     │
│   • - Energy penalty: \|\tau \dot{q}\|^2                                    │
│   • - Body jerk penalty: \|\mathbf{\ddot{p}}\|^2                            │
│   • - Foot slip penalty: \|v_{\text{contact}}\|^2                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Overcoming the Sim-to-Real Gap: Domain Randomization

A policy trained in a perfect simulator will violently shake and collapse on real hardware.
**Domain Randomization** trains the neural network to be robust across a wide probability distribution of physics parameters:

| Parameter | Nominal Value | Training Randomization Range |
|---|---|---|
| **Base Trunk Mass** | $10.0\text{ kg}$ | $[8.5\text{ kg}, 12.5\text{ kg}]$ |
| **Ground Friction $\mu$** | $0.7$ | $[0.2\text{ (ice)}, 1.2\text{ (rubber)}]$ |
| **Motor Latency** | $0.0\text{ ms}$ | $[2\text{ ms}, 25\text{ ms}]$ |
| **Motor Torque Gain ($K_p, K_d$)** | Nominal | $\pm 20\%$ gain error |
| **External Push Impulse** | $0\text{ N}$ | Random $[0\text{ N}, 80\text{ N}]$ pushes every 3 sec |

---

### 3. Comparing Model-Based MPC vs. Reinforcement Learning

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONVEX MPC VS. NEURAL RL POLICIES                   │
│                                                                             │
│   CONVEX MPC (Model-Based):                                                 │
│   • Pros: Mathematically transparent, guarantees stability constraints,     │
│     requires zero training data, explicit friction cone enforcement.        │
│   • Cons: Assumes rigid ground; fails on non-rigid dynamic terrains.        │
│                                                                             │
│   NEURAL RL POLICIES (Data-Driven / PPO):                                   │
│   • Pros: Discovers extreme agility (backflips, parkour, stair running);    │
│     runs inference in < 0.2 ms on embedded microcomputers.                  │
│   • Cons: Black-box behavior; unpredictable responses to out-of-distribution │
│     sensory corruptions.                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 4. Hands-On Lab & Practical Code References

#### 1. Running Policy Inference in ROS2:
```bash
# Launch quadruped simulation with neural locomotion policy
ros2 launch quadruped_bringup quadruped_sim.launch.py
ros2 run quadruped_locomotion mpc_controller.py
```
- Breaker Test: `ros2 run quadruped_demos break_gait.py`

