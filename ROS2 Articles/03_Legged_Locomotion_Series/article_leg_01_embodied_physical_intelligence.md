## LEG 01: EMBODIED PHYSICAL INTELLIGENCE & FLOATING-BASE DYNAMICS

*Purpose: Master the core philosophy of legged locomotion. Understand why legged robots represent the ultimate manifestation of embodied intelligence, contrast fixed-base and wheeled systems with underactuated floating-base dynamics, and explore the tight physics-control loop.*

### Must Answer
- What is Embodied Physical Intelligence, and why is action inseparable from dynamic morphology in legged robots?
- How does a floating-base legged system differ from a fixed-base manipulator or a planar wheeled robot?
- What is Underactuation, and why are the 6 spatial degrees of freedom of the robot chassis not directly driven by motors?
- How does every stepping action alter the support geometry, ground reaction forces, and body stability?
- What is the multi-tier temporal control hierarchy (Behavior $10\text{ Hz} \to$ Locomotion/MPC $100\text{ Hz} \to$ WBC $500\text{ Hz} \to$ Joint PD $1000\text{ Hz}$)?

### Key Insight
Wheeled robots move through space with continuous static contact; a quadruped floats in 3D space, generating acceleration entirely by intermittent, unilateral, non-linear impact contacts with the terrain.

---

### 1. The Embodied Locomotion Paradigm

In classical robotics, software and hardware are cleanly decoupled: an algorithm computes a collision-free path, and motor controllers execute it.
In **Legged Locomotion**, intelligence is fundamentally **Embodied**:

$$\text{Action} \iff \text{Contact Forces} \iff \text{Floating-Base Dynamics} \iff \text{Morphology}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EMBODIED LOCOMOTION FEEDBACK LOOP                        │
│                                                                             │
│               [Floating Body (Chassis)] ──▶ (Underactuated 6-DOF)           │
│                           │                                                 │
│                           ▼ (Joint Torques \tau)                            │
│                 [4x 3-DOF Articulated Legs]                                 │
│                           │                                                 │
│                           ▼ (Intermittent Foot Contacts)                    │
│             [Ground Contact Dynamics & Friction Cones]                      │
│                           │                                                 │
│                           ▼ (Ground Reaction Forces F_grf)                  │
│               [Body Acceleration \ddot{x}, \dot{\omega}]                    │
│                           │                                                 │
│                           ▼                                                 │
│             [IMU & Kinematic State Estimation] ──▶ [Locomotion MPC / WBC]   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Fixed-Base vs. Wheeled vs. Floating-Base Systems

| System Type | Base Actuation | Support Geometry | Odometry Source | Failure Mode |
|---|---|---|---|---|
| **Industrial Arm** | Fixed to World ($0\text{ DOF}$) | Infinite (bolted) | Joint encoders directly | Over-torque / Collision |
| **Wheeled AMR** | Planar Non-holonomic ($3\text{ DOF}$) | Continuous polygon | Wheel ticks + IMU | Wheel slip / High center of mass |
| **Legged Quadruped** | **Floating Base ($6\text{ DOF}$ unactuated)** | **Dynamic intermittent polygon** | **EKF contact fusion** | **Catastrophic fall / Tip-over** |

---

### 3. The Multi-Tier Temporal Control Hierarchy

Legged locomotion spans 4 distinct temporal bandwidths:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TEMPORAL CONTROL BANDWIDTHS                            │
│                                                                             │
│   1. BEHAVIOR LAYER (10 Hz / 100 ms)                                        │
│   • Mission planning, waypoint navigation, elevation terrain scanning.      │
│                                                                             │
│   2. LOCOMOTION / MPC LAYER (100 Hz / 10 ms)                                │
│   • Single Rigid Body Dynamics (SRBD), Convex MPC, optimal ground reaction  │
│     forces \mathbf{f}_i for horizon N = 10 (next 0.3 seconds).              │
│                                                                             │
│   3. WHOLE-BODY CONTROL LAYER (500 Hz / 2 ms)                               │
│   • Operational space QP: projects ground reaction forces and swing foot    │
│     Bézier accelerations into instantaneous joint torques \tau.             │
│                                                                             │
│   4. LOW-LEVEL JOINT CONTROL (1000 Hz / 1 ms)                               │
│   • Hard real-time motor driver PD loops: \tau_cmd = K_p (q* - q) + K_d ... │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 4. Hands-On Lab & Practical Code References

#### 1. Inspecting the Quadruped Kit Bringup:
- Master Bringup: [`ros2_quadruped_kit/src/quadruped_bringup/launch/simulation.launch.py`](../../Ros2%20learning%20kits/ros2_quadruped_kit/src/quadruped_bringup/launch/simulation.launch.py)
- Kit Overview: [`ros2_quadruped_kit/README.md`](../../Ros2%20learning%20kits/ros2_quadruped_kit/README.md)

