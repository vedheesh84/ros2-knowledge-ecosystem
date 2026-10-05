# Distributed Multi-Robot Cyber-Physical System (CPS) Workspace

**Multi-Tier Autonomous Cyber-Physical System with Physical Edge Robots, Base Station Coordinators, and Real-Time Observability**

This workspace implements an end-to-end multi-robot CPS platform spanning physical mobile robots, embedded edge controllers, fixed sensor anchors, and high-performance base station coordinators using ROS 2 Humble, FastDDS Discovery Server, and telemetry monitoring.

---

## 1. System Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TIER 3: MANAGEMENT & CLOUD/BASE LAYER                            │
│  • Global Task Planner (CBBA Auctions)      • Digital Twin Mirror (Gazebo/Web)                   │
│  • FastDDS Discovery Server (TCP:11811)     • Observability (Foxglove + Prometheus + Grafana)   │
│  • Multi-Robot Map Merging & TF Aggregator  • Chrony Master Server (NTP Precision <1ms)         │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ Wi-Fi Subnet / Unicast DDS / Zenoh
         ┌───────────────────────────────────────┴───────────────────────────────────────┐
         ▼                                                                               ▼
┌───────────────────────────────────────────────┐               ┌───────────────────────────────────────────────┐
│     TIER 1: ROBOT 1 — EXPLORER (AMR)          │               │ TIER 2: ROBOT 2 — TRANSPORTER/MANIPULATOR     │
│  • Hardware: Differential Drive + 2D LiDAR    │               │  • Hardware: 4WD Rover + 5/6-DOF Arm + Camera │
│  • Compute: RPi 4/5 or Jetson (Ubuntu 22.04)  │               │  • Compute: RPi 4/5 + PCA9685/STM32 Bridge    │
│  • Role: Frontier Exploration & SLAM Mapping  │               │  • Role: Nav2 Path Execution + MoveIt2 Pick   │
│  • Namespacing: /robot1/*                     │               │  • Namespacing: /robot2/*                     │
│  • TF: map -> robot1/odom -> robot1/base_link │               │  • TF: map -> robot2/odom -> robot2/base_link │
└───────────────────────────────────────────────┘               └───────────────────────────────────────────────┘
```

---

## 2. Package Summary

| Package | Role | Core Nodes & Capabilities |
|---|---|---|
| **`cps_msgs`** | Custom Interfaces | `TaskAssignment.msg`, `RobotHeartbeat.msg`, `PeerState.msg`, `RequestTask.srv`, `ExecuteCoordinatedMission.action` |
| **`cps_coordination`** | Decision & Planning | `base_coordinator_node.py`, `map_merger_node.py`, `cbba_auction_node.py`, `peer_collision_avoidance.py`, `health_watchdog_node.py` |
| **`cps_telemetry`** | Observability | `topic_delay_monitor.py`, `prometheus_ros_exporter.py`, Foxglove & Grafana dashboard configurations |
| **`cps_bringup`** | Orchestration | Discovery Server XML profile, QoS YAML, multi-robot Gazebo digital twin launch recipes |

---

## 3. Quick Start & Execution Recipes

### 1. Build the Workspace
```bash
cd "02 — Domains/ROS2/Distributed_CPS_ws"
colcon build --symlink-install
source install/setup.bash
```

### 2. Network Time Sync & Discovery Server
```bash
# On Base Station (Master):
chmod +x setup_network.sh
./setup_network.sh server 192.168.1.100

# On Edge Robots (Clients):
./setup_network.sh client 192.168.1.100
```

### 3. Launching Full Multi-Robot Digital Twin Simulation
```bash
ros2 launch cps_bringup full_cps_simulation.launch.py
```

### 4. Launching Physical Base Station & Fleet Nodes
```bash
# On Base Station:
ros2 launch cps_bringup base_station.launch.py

# On Robot 1 (Explorer):
ros2 launch cps_bringup explorer_robot.launch.py

# On Robot 2 (Manipulator):
ros2 launch cps_bringup manipulator_robot.launch.py
```

---

## 4. Master Learning Series Curriculum

For in-depth mathematical formulations, DDS internals, and research-level distributed control proofs, refer to the [Distributed CPS Learning Series](../ROS2%20Articles/06_Distributed_CPS_Series/article_cps_01_cyber_physical_systems_architecture.md).
