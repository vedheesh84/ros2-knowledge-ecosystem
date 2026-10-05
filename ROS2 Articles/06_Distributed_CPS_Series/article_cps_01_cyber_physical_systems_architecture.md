# Article CPS-01: Cyber-Physical Systems (CPS) Architecture for Multi-Robot Systems

**Pedagogical Layer:** Foundational Systems Architecture  
**Focus Area:** Industrial Distributed Control Systems (DCS), Edge-Fog-Cloud Hierarchy, and Cyber-Physical Feedback Loops  
**Associated Package:** `cps_coordination`, `cps_bringup`

---

## 1. Introduction: From Isolated Robots to Cyber-Physical Fleets

Traditional robotics treats the robot as an **isolated, monolithic computation node**: sensors feed onboard algorithms, which command local actuators. In a **Cyber-Physical System (CPS)**, physical entities (heterogeneous ground rovers, robotic arms, aerial scouts) are tightly integrated with computation, networking, fixed infrastructure anchors, and cloud/edge intelligence.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               TIER 3: SUPERVISORY & MANAGEMENT LAYER                             │
│  • Global Mission Optimization              • Global Occupancy Grid Fusion                       │
│  • Digital Twin Mirror (Gazebo / Web)       • Long-Term Fleet Telemetry (Prometheus / Grafana)   │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ DDS FastRTPS Unicast / Zenoh Router
         ┌───────────────────────────────────────┴───────────────────────────────────────┐
         ▼                                                                               ▼
┌───────────────────────────────────────────────┐               ┌───────────────────────────────────────────────┐
│     TIER 1: ROBOT 1 — EXPLORER (AMR)          │               │ TIER 2: ROBOT 2 — TRANSPORTER / MANIPULATOR   │
│  • Role: Frontier SLAM & Landmark Detection   │               │  • Role: Nav2 Path Execution + MoveIt2 Pick   │
│  • Edge Compute: Raspberry Pi 5 / Orin Nano   │               │  • Edge Compute: Raspberry Pi 5 + Micro-ROS   │
│  • Local Namespace: /robot1/*                 │               │  • Local Namespace: /robot2/*                 │
│  • TF: map -> robot1/odom -> robot1/base_link │               │  • TF: map -> robot2/odom -> robot2/base_link │
└───────────────────────────────────────────────┘               └───────────────────────────────────────────────┘
```

---

## 2. Industrial DCS Principles Applied to Multi-Robot Robotics

Industrial Distributed Control Systems (DCS) partition automation across strictly separated layers:

1. **Level 0 (Physical Layer / Actuators & Sensors)**:
   - DC brushless hub motors, quadrature encoders, 2D LiDARs, RealSense depth cameras, 6-DOF servo arms.
2. **Level 1 (Direct Control Layer / Embedded Real-Time)**:
   - Micro-ROS microcontrollers (ESP32, STM32, Arduino) running 100 Hz PID velocity and current loops.
3. **Level 2 (Coordinated Node Layer / Single-Robot SBC)**:
   - Linux SBC (Ubuntu 22.04 with ROS 2 Humble) executing local SLAM, local costmaps, and MoveIt 2 trajectory generators.
4. **Level 3 (Supervisory Coordination Layer / Base Station)**:
   - High-performance workstation managing fleet dispatch, consensus auctioning, and global map stitching.

---

## 3. Communication Topologies: Peer-to-Peer vs Broker-Assisted

| Architecture | Discovery Mechanism | Scalability ($N$ nodes) | Wi-Fi Resilience | Single Point of Failure |
|---|---|:---:|:---:|:---:|
| **Standard ROS 2 (Multicast)** | Simple Participant Discovery (SPDP) | $O(N^2)$ packets | Poor (Multicast dropouts) | None |
| **FastDDS Discovery Server** | Unicast TCP/UDP to Central Locator | $O(N)$ packets | High | Low (Redundant servers supported) |
| **Zenoh Router (`rmw_zenoh`)** | Compact Broker Protocol | $O(1)$ client traffic | Excellent (Lossy links) | Low |

---

## 4. Architectural Implementation Recipe

To build a clean CPS node hierarchy in ROS 2:
1. **Never use unqualified global topic names** (e.g. `/cmd_vel`). Always push a unique robot namespace (e.g. `/robot1/cmd_vel`).
2. **Isolate TF trees**: Every transform must belong to an explicit frame prefix (`robot1/base_link`, `robot2/base_link`).
3. **Establish a common spatial origin**: Both robots must tie their local odometry to a unified `map` frame via global localization (AMCL or Multi-Robot SLAM).

---

## 5. Summary & Key Takeaways

- A Multi-Robot CPS decomposes high-level mission goals into distributed, local real-time actions.
- True scalability requires replacing unconstrained multicast discovery with structured, unicast DDS architectures.
- In [Article CPS-02](article_cps_02_dds_discovery_server_and_qos_tuning.md), we explore the wire mechanics of FastDDS Discovery Servers and Quality of Service (QoS) tuning.
