# ros2_drone_swarm_kit

**Aerial Swarm Robotics & Distributed Multi-Agent Learning Kit**

A systems learning platform for multi-robot namespacing, leader-follower formation flight, distributed consensus, and swarm coordination in ROS2.

---

## 1. Overview & Identity

`ros2_drone_swarm_kit` represents **Vertical 5: Collective & Swarm Intelligence** in the Intelligent Ecosystem. It explores how intelligent collective behavior emerges when multiple autonomous aerial agents communicate, synchronize, and navigate concurrently.

---

## 2. Package Architecture

```text
ros2_drone_swarm_kit/
├── resources/
│   └── swarm_coordination_principles.md # Mathematical foundations of swarm consensus & potential fields
├── src/
│   ├── drone_description/               # Micro-quadcopter URDF/Xacro models & visual meshes
│   ├── drone_hardware/                  # Mock flight dynamics & PX4/micro-ROS bridge
│   ├── swarm_control/                   # Position PID controllers & flight dynamics
│   ├── swarm_formation/                 # Leader-follower & dynamic formation flight engines
│   ├── swarm_coordination/              # Distributed area coverage & swarm dispatch
│   ├── drone_bringup/                   # Multi-agent namespaced spawn launch orchestration
│   └── swarm_demos/                     # 6 progressive educational demos + 4 failure breakers
└── README.md                            # Primary workspace documentation
```

---

## 3. Quick Start

```bash
# 1. Build workspace
cd "02 — Domains/ROS2/Ros2 learning kits/ros2_drone_swarm_kit"
colcon build --symlink-install
source install/setup.bash

# 2. Launch 3-Drone Namespaced Swarm Simulation
ros2 launch drone_bringup swarm_3drones.launch.py

# 3. Dynamic Formation Switching
ros2 run swarm_demos demo_04_dynamic_formation
```

---

## 4. Progressive Demo Progression

| Demo | Focus | What You Learn |
|---|---|---|
| **Demo 01** | `demo_01_single_drone_flight` | 3D waypoint navigation, altitude control, and landing. |
| **Demo 02** | `demo_02_multi_drone_namespacing` | Multi-robot launch composition and namespace isolation. |
| **Demo 03** | `demo_03_leader_follower` | Leader tracking with geometric coordinate offsets. |
| **Demo 04** | `demo_04_dynamic_formation` | Online switching between V-Shape, Line, and Circle formations. |
| **Demo 05** | `demo_05_collision_avoidance` | Decentralized artificial potential field deflection. |
| **Demo 06** | `demo_06_swarm_area_coverage` | Coordinated multi-agent grid sweep and search-and-rescue. |

---

## 5. Intentional Failure Breakers

| Breaker | Injected Fault | Architectural Lesson Learned |
|---|---|---|
| `break_communication_drop` | Follower packet loss | Heartbeat watchdog and autonomous hover hold. |
| `break_leader_failure` | Leader crash | Dynamic leader re-election in decentralized networks. |
| `break_gps_drift` | Spatial position drift | Relative range/bearing sensor fallback. |
| `break_swarm_collision` | Converging trajectories | Potential field saturation limits. |

---

## 6. Aerial Swarm Robotics & Distributed Intelligence Curriculum (18 Articles)

This kit is accompanied by the comprehensive 18-article **[Aerial Swarm Robotics Series](../../ROS2%20Articles/COMPLETE_INDEX.md#vertical-5-aerial-swarm-robotics--distributed-intelligence-series-18-articles)**:

- **Module 1 (Single Node & $SE(3)$ Flight)**: [Distributed Swarm Intelligence (UAV 01)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_01_distributed_swarm_intelligence.md) | [Quadrotor Dynamics & Differential Flatness (UAV 02)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_02_quadrotor_dynamics_and_se3_geometry.md) | [Cascaded Flight Control on $SE(3)$ (UAV 03)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_03_cascaded_flight_control_and_geometric_tracking.md)
- **Module 2 (Graph Theory & State Fusion)**: [Graph Theory & Topologies (UAV 04)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_04_graph_theory_and_network_topologies.md) | [Decentralized Consensus Protocols (UAV 05)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_05_decentralized_consensus_protocols.md) | [Distributed State Estimation & CI (UAV 06)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_06_distributed_state_estimation_and_fusion.md)
- **Module 3 (Emergent Flocking & Collisions)**: [Reynolds' Boids & Flocking (UAV 07)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_07_reynolds_boids_and_flocking_rules.md) | [Virtual Spring-Damper Meshes (UAV 08)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_08_virtual_spring_damper_mesh_dynamics.md) | [Decentralized 3D ORCA (UAV 09)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_09_decentralized_collision_avoidance_orca.md)
- **Module 4 (Dynamic Formations & Morphing)**: [Formation Control & Virtual Leaders (UAV 10)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_10_formation_control_leader_follower_vs_virtual_leader.md) | [Dynamic Switching & Hungarian (UAV 11)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_11_dynamic_formation_switching_and_hungarian_matching.md) | [Time-Varying Squeeze Contraction (UAV 12)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_12_time_varying_formations_and_obstacle_squeeze.md)
- **Module 5 (Task Allocation & Collective Missions)**: [Distributed Task Allocation / CBBA (UAV 13)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_13_distributed_task_allocation_cbba_and_auctions.md) | [Decentralized Area Coverage / Voronoi (UAV 14)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_14_decentralized_area_coverage_and_voronoi_partitioning.md) | [Target Tracking & Encirclement (UAV 15)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_15_cooperative_target_tracking_and_encirclement.md)
- **Module 6 (Resilience, DDS Tuning & DECA Bridge)**: [Network Loss & Leader Re-Election (UAV 16)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_16_network_degradation_packet_loss_and_leader_failure.md) | [ROS2 DDS Tuning & Discovery Server (UAV 17)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_17_ros2_dds_tuning_for_multi_robot_swarms.md) | [The DECA Bridge: Collective Mind (UAV 18)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_18_the_deca_bridge_collective_embodied_consciousness.md)

---

## 7. Related Resources

- [resources/swarm_coordination_principles.md](resources/swarm_coordination_principles.md)
- [UAV Research Workspace](../../UAV_ws/README.md)
- [Kits & Products Strategy](../../KITS_AND_PRODUCTS_STRATEGY.md)

