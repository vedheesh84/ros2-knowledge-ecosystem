# ros2_drone_swarm_kit

**Aerial Swarm Robotics & Distributed Multi-Agent Learning Kit**

A comprehensive systems learning platform for multi-robot namespacing, leader-follower formation flight, distributed consensus, artificial potential fields, and swarm coordination in ROS 2.

---

## 1. Overview & Identity

`ros2_drone_swarm_kit` represents **Vertical 5: Collective & Swarm Intelligence** in the Intelligent Ecosystem. It explores how intelligent collective behavior emerges when multiple autonomous aerial agents communicate, synchronize, and navigate concurrently.

---

## 2. Package Architecture

```text
ros2_drone_swarm_kit/
├── arduino/
│   └── drone_flight_controller/
│       └── drone_flight_controller.ino  # 50 Hz physical ESC & IMU/Baro firmware
├── scripts/
│   ├── pseudo_drone_emulator.py         # Virtual PTY serial emulator for offline testing
│   └── test_drone_swarm_kit.py          # 8-part comprehensive automated verification suite
├── resources/
│   └── swarm_coordination_principles.md # Mathematical foundations of swarm consensus & potential fields
├── src/
│   ├── drone_description/               # Micro-quadcopter URDF/Xacro models & RViz visualization
│   ├── drone_hardware/                  # Serial telemetry & control bridge connecting flight controllers
│   ├── swarm_control/                   # Position PID controllers & flight dynamics simulator
│   ├── swarm_formation/                 # Leader-follower & dynamic formation flight engines
│   ├── swarm_coordination/              # Distributed area coverage & swarm mission dispatch
│   ├── drone_bringup/                   # Multi-agent namespaced spawn launch orchestration
│   └── swarm_demos/                     # 6 progressive educational demos + 4 failure breakers
└── README.md                            # Primary kit documentation
```

---

## 3. Quick Start

### 1. Build Workspace
```bash
cd "02 — Domains/ROS2/Ros2 learning kits/ros2_drone_swarm_kit"
colcon build --symlink-install
source install/setup.bash
```

### 2. Launch 3-Drone Namespaced Swarm Simulation
```bash
ros2 launch drone_bringup swarm_3drones.launch.py use_rviz:=true
```

### 3. Dynamic Formation Switching
```bash
ros2 run swarm_demos demo_04_dynamic_formation
```

### 4. Run Automated Test Suite
```bash
python3 scripts/test_drone_swarm_kit.py
```

---

## 4. Hardware Integration & Virtual Telemetry Bridge

The kit supports both physical microcontroller flight controllers and desktop virtual serial emulation:

- **Physical Arduino Firmware (`arduino/drone_flight_controller/drone_flight_controller.ino`)**:
  - Implements a 50 Hz real-time flight control loop with 4-motor Quad X mixer (Pins 3, 5, 6, 9).
  - Handles `ARM`, `DISARM`, and `CMD,roll,pitch,yaw_rate,thrust` ASCII serial commands.
  - Streams 50 Hz telemetry frames (`TELEM,roll,pitch,yaw,alt,vx,vy,vz,armed,battery`).
  - Includes failsafe watchdog timer (auto-land on 1000ms comm loss).

- **Desktop Pseudo-Hardware Emulator (`scripts/pseudo_drone_emulator.py`)**:
  - Creates a POSIX virtual pseudo-terminal (`/tmp/ttyVIRT_DRONE`) implementing the flight controller protocol.
  - Allows running tests and simulations completely offline without requiring physical hardware connected.

- **Hardware Bridge Node (`drone_hardware/flight_controller_bridge.py`)**:
  - Bridges physical or virtual serial streams into ROS 2 topics: `/{drone_id}/imu`, `/{drone_id}/odom`, `/{drone_id}/battery`, and `/{drone_id}/armed`.
  - Translates `/{drone_id}/cmd_vel` into flight controller motor mixing setpoints.

```bash
# Launch virtual emulator
python3 scripts/pseudo_drone_emulator.py --port /tmp/ttyVIRT_DRONE

# Launch ROS 2 hardware bridge
ros2 run drone_hardware flight_controller_bridge --ros-args -p serial_port:=/tmp/ttyVIRT_DRONE -p drone_id:=drone_0
```

---

## 5. Progressive Demo Progression

| Demo | Focus | What You Learn |
|---|---|---|
| **Demo 01** | `demo_01_single_drone_flight` | 3D waypoint navigation, altitude control, and landing for `drone_0`. |
| **Demo 02** | `demo_02_multi_drone_namespacing` | Simultaneous multi-agent dispatch and topic isolation across `/drone_0`, `/drone_1`, `/drone_2`. |
| **Demo 03** | `demo_03_leader_follower` | Closed-loop leader tracking with SE(3) heading-aligned geometric coordinate offsets. |
| **Demo 04** | `demo_04_dynamic_formation` | Online switching between V-Shape, Line, and Circle geometric formations with centroid tracking. |
| **Demo 05** | `demo_05_collision_avoidance` | Decentralized artificial potential field (APF) repulsive deflection on crossing paths. |
| **Demo 06** | `demo_06_swarm_area_coverage` | Coordinated multi-agent search-and-rescue grid sweep partitioned into parallel non-overlapping lanes. |

---

## 6. Intentional Failure Breakers

| Breaker | Injected Fault | Architectural Lesson Learned |
|---|---|---|
| `break_communication_drop` | Follower packet loss / RF jamming | Heartbeat watchdog timeout ($>1.0\text{s}$) triggering autonomous hover hold fallback. |
| `break_leader_failure` | Leader crash / dropout | Decentralized consensus election promoting `drone_1` to new leader and reforming swarm mesh. |
| `break_gps_drift` | Progressive spatial position drift | State estimation innovation residual detection triggering optical-flow / rangefinder fallback. |
| `break_swarm_collision` | Converging collision course | Proximity radar breach triggering emergency vertical altitude deconfliction ($\Delta z = \pm 0.7\text{m}$). |

---

## 7. Aerial Swarm Robotics & Distributed Intelligence Curriculum (18 Articles)

This kit is accompanied by the comprehensive 18-article **[Aerial Swarm Robotics Series](../../ROS2%20Articles/COMPLETE_INDEX.md#vertical-5-aerial-swarm-robotics--distributed-intelligence-series-18-articles)**:

- **Module 1 (Single Node & $SE(3)$ Flight)**: [Distributed Swarm Intelligence (UAV 01)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_01_distributed_swarm_intelligence.md) | [Quadrotor Dynamics & Differential Flatness (UAV 02)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_02_quadrotor_dynamics_and_se3_geometry.md) | [Cascaded Flight Control on $SE(3)$ (UAV 03)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_03_cascaded_flight_control_and_geometric_tracking.md)
- **Module 2 (Graph Theory & State Fusion)**: [Graph Theory & Topologies (UAV 04)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_04_graph_theory_and_network_topologies.md) | [Decentralized Consensus Protocols (UAV 05)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_05_decentralized_consensus_protocols.md) | [Distributed State Estimation & CI (UAV 06)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_06_distributed_state_estimation_and_fusion.md)
- **Module 3 (Emergent Flocking & Collisions)**: [Reynolds' Boids & Flocking (UAV 07)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_07_reynolds_boids_and_flocking_rules.md) | [Virtual Spring-Damper Meshes (UAV 08)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_08_virtual_spring_damper_mesh_dynamics.md) | [Decentralized 3D ORCA (UAV 09)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_09_decentralized_collision_avoidance_orca.md)
- **Module 4 (Dynamic Formations & Morphing)**: [Formation Control & Virtual Leaders (UAV 10)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_10_formation_control_leader_follower_vs_virtual_leader.md) | [Dynamic Switching & Hungarian (UAV 11)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_11_dynamic_formation_switching_and_hungarian_matching.md) | [Time-Varying Squeeze Contraction (UAV 12)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_12_time_varying_formations_and_obstacle_squeeze.md)
- **Module 5 (Task Allocation & Collective Missions)**: [Distributed Task Allocation / CBBA (UAV 13)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_13_distributed_task_allocation_cbba_and_auctions.md) | [Decentralized Area Coverage / Voronoi (UAV 14)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_14_decentralized_area_coverage_and_voronoi_partitioning.md) | [Target Tracking & Encirclement (UAV 15)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_15_cooperative_target_tracking_and_encirclement.md)
- **Module 6 (Resilience, DDS Tuning & DECA Bridge)**: [Network Loss & Leader Re-Election (UAV 16)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_16_network_degradation_packet_loss_and_leader_failure.md) | [ROS2 DDS Tuning & Discovery Server (UAV 17)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_17_ros2_dds_tuning_for_multi_robot_swarms.md) | [The DECA Bridge: Collective Mind (UAV 18)](../../ROS2%20Articles/05_Aerial_Swarm_Series/article_uav_18_the_deca_bridge_collective_embodied_consciousness.md)

---

## 8. Verification Results

All packages and nodes have been systematically verified with automated unit and integration tests:
- **Test Suite**: `python3 scripts/test_drone_swarm_kit.py`
- **Results**: 8 / 8 tests passed (100% success rate, exit code 0).
- **Tested Nodes**: `drone_description`, `drone_bringup`, `swarm_control`, `swarm_formation`, `swarm_coordination`, `drone_hardware`, and all 10 `swarm_demos` binaries.
