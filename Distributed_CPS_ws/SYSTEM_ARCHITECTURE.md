# Distributed Multi-Robot Cyber-Physical System (CPS): System Architecture

**Document Version:** 2.0.0  
**Status:** 100% Verified & Tested  
**Associated Curriculum:** `06_Distributed_CPS_Series` (Articles CPS-01 through CPS-09)  
**Target Environment:** ROS 2 Humble Hawksbill / FastDDS Discovery Server / Linux Embedded (RPi 4/5, Jetson Orin)

---

## 1. Executive System Overview

The **Distributed Multi-Robot Cyber-Physical System (CPS)** workspace provides an end-to-end distributed robotics platform. It coordinates heterogeneous ground rovers, articulated manipulation units, fixed IoT perimeter sensor anchors, and high-performance base station supervisors over a wireless DDS network bus.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TIER 3: MANAGEMENT & CLOUD/BASE LAYER                            │
│  • Global Task Dispatcher & State Machine   • Digital Twin Mirror (Gazebo / Web)                 │
│  • FastDDS Discovery Server (TCP/UDP:11811) • Observability (Foxglove + Prometheus + Grafana)   │
│  • Multi-Robot 2D Map Merging & Fusion      • Chrony Master NTP Server (Precision <1ms)          │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ Wi-Fi Subnet / Unicast DDS / Zenoh Router
         ┌───────────────────────────────────────┴───────────────────────────────────────┐
         ▼                                                                               ▼
┌───────────────────────────────────────────────┐               ┌───────────────────────────────────────────────┐
│     TIER 1: ROBOT 1 — EXPLORER (AMR)          │               │ TIER 2: ROBOT 2 — TRANSPORTER/MANIPULATOR     │
│  • Chassis: 2WD Differential Drive + 2D LiDAR │               │  • Chassis: 4WD Rover + 5/6-DOF Robotic Arm   │
│  • Compute: RPi 5 / Orin Nano (Ubuntu 22.04)  │               │  • Compute: RPi 5 + Microcontroller Bridge    │
│  • Role: Frontier Exploration & Mapping       │               │  • Role: Nav2 Path Navigation & MoveIt2 Pick  │
│  • Namespacing: /robot1/*                     │               │  • Namespacing: /robot2/*                     │
│  • TF: map -> robot1/odom -> robot1/base_link │               │  • TF: map -> robot2/odom -> robot2/base_link │
└───────────────────────┬───────────────────────┘               └───────────────────────┬───────────────────────┘
                        │                                                               │
                        └───────────────────────┬───────────────────────────────────────┘
                                                ▼
                        ┌───────────────────────────────────────────────┐
                        │     PHYSICAL EDGE SENSOR ANCHOR / GATEWAY     │
                        │  • Hardware: Arduino Uno / Nano / ESP32       │
                        │  • Sensors: Battery Divider, Temp, Sonar Ping │
                        │  • Safety: Hardware E-Stop Relay Interrupt    │
                        │  • Serial Link: 115200 Baud, NMEA $CPS Telemetry│
                        └───────────────────────────────────────────────┘
```

---

## 2. Package Summary & Structural Taxonomy

```text
Distributed_CPS_ws/
├── arduino/
│   └── cps_edge_node/
│       └── cps_edge_node.ino          # Edge microcontroller firmware (ADC, Sonar, E-Stop)
├── scripts/
│   ├── pseudo_cps_network_emulator.py # PTY serial bridge + multi-robot fault injector
│   └── test_distributed_cps.py        # 10-phase automated integration test suite
├── src/
│   ├── cps_msgs/                      # Custom interfaces (3 messages, 1 service, 1 action)
│   ├── cps_coordination/              # Decision engine, CBBA, map merger, collision avoidance
│   ├── cps_telemetry/                 # Topic delay probe, Prometheus HTTP exporter, dashboards
│   └── cps_bringup/                   # Discovery server XML, QoS YAML, multi-robot launch recipes
├── setup_network.sh                   # Automated Chrony NTP & FastDDS network configuration
├── SYSTEM_ARCHITECTURE.md             # This comprehensive architecture specification
├── ERROR_DIAGNOSIS_AND_SOLUTIONS.md   # Complete technical failure and solution registry
└── COHERENCE_AUDIT_REPORT.md          # Pedagogical audit cross-referencing Articles CPS-01 - 09
```

---

## 3. Mathematical & Algorithmic Foundations

### 3.1 Consensus-Based Bundle Algorithm (CBBA)
In decentralized multi-agent operations where a centralized coordinator represents a Single Point of Failure (SPOF), CBBA guarantees a polynomial-time conflict-free task assignment with a provable $50\%$ optimality bound ($1/2$-approximation to global ILP optimum).

1. **Phase 1: Bundle Building (Local Greedy Construction)**  
   For task $j$ located at coordinate $\mathbf{x}_j$, an agent located at $\mathbf{x}_i$ computes the marginal score discounted exponentially by Euclidean distance:
   $$c_{ij} = R_j \cdot e^{-\lambda \cdot \|\mathbf{x}_i - \mathbf{x}_j\|}$$
   Tasks are appended to the agent's bundle $b_i$ while $|b_i| < L_t$ and $c_{ij} > y_{ij}$ (where $y_{ij}$ is the highest recorded bid across the fleet).

2. **Phase 2: Consensus Resolution (Peer Communication)**  
   Robots periodically exchange winning bid lists $\mathbf{y}_i$ and winning agent assignments $\mathbf{z}_i$. When an agent is outbid by peer $k$ ($y_{kj} > y_{ij}$), it updates $y_{ij} \leftarrow y_{kj}$ and $z_{ij} \leftarrow z_{kj}$. If task $j$ was in its local bundle, it releases task $j$ and all downstream tasks appended to its bundle after task $j$.

### 3.2 2D Bayesian Log-Odds Occupancy Grid Fusion
Let $m_1(x, y)$ and $m_2(x, y)$ be 2D local occupancy grid probabilities generated by independent robot SLAM instances. The log-odds representation of occupancy is defined as:
$$L(m(x, y)) = \ln \left( \frac{P(m(x, y) = 1)}{1 - P(m(x, y) = 1)} \right)$$

When combining independent spatial observations:
$$L(m_{\text{fused}}(x, y)) = L(m_1(x, y)) + L(m_2(x, y)) - L_0$$
where $L_0 = 0$ is the prior log-odds for unknown space ($P=0.5$).
The fused probability is recovered via the sigmoid function:
$$P(m_{\text{fused}}(x, y) = 1) = \frac{1}{1 + e^{-L(m_{\text{fused}}(x, y))}}$$

### 3.3 Velocity Obstacle (VO) Reciprocal Collision Avoidance
To prevent reciprocal deadlock in narrow corridors, each agent computes the Velocity Obstacle cone $VO_{A|B}(\mathbf{v}_B)$:
$$VO_{A|B}(\mathbf{v}_B) = \left\{ \mathbf{v} \;\Big|\; \exists t \in [0, \tau], \; t(\mathbf{v} - \mathbf{v}_B) \in D(\mathbf{p}_B - \mathbf{p}_A, r_A + r_B) \right\}$$
Based on distance $d = \|\mathbf{p}_B - \mathbf{p}_A\|$, the node publishes dynamic RViz `Marker` bounding cylinders and costmap footprint inflation alerts:
- $d > 2.5 \cdot r_{\text{safe}}$: `SAFE` (Green marker)
- $1.5 \cdot r_{\text{safe}} < d \le 2.5 \cdot r_{\text{safe}}$: `WARNING` (Yellow marker)
- $d \le 1.5 \cdot r_{\text{safe}}$: `CRITICAL` (Red marker, Nav2 speed throttling triggered)

---

## 4. Hardware & Edge Integration

### 4.1 Physical Edge Sensor Anchor (`cps_edge_node.ino`)
The physical microcontroller sketch provides edge monitoring for stationary perimeter anchors or robot power distribution units:
- **Battery Divider (A0):** Reads analog voltage divider with $R_1 = 10\,\text{k}\Omega$ and $R_2 = 2.2\,\text{k}\Omega$:
  $$V_{\text{bat}} = \left(\frac{\text{ADC}}{1023}\right) \times 5.0\,\text{V} \times \left(\frac{10\,\text{k}\Omega + 2.2\,\text{k}\Omega}{2.2\,\text{k}\Omega}\right)$$
- **Emergency Stop Interrupt (D2):** Hardware interrupt `FALLING` triggering immediate de-energization of the safety relay (Pin 8).
- **Serial Telemetry Protocol (115200 Baud):** Streams NMEA-formatted frames at 2 Hz:
  ```text
  $CPS,id=edge_anchor_1,seq=42,v=12.24,pct=92.1,temp=26.4,dist=1.85,estop=0*4F
  ```
- **Command Dispatch:** Listens for `$CMD,ESTOP\n`, `$CMD,RESUME\n`, and `$CMD,PING\n`.

---

## 5. Standardized Testing Sandbox Layer

In accordance with user design directives, every main package and workspace incorporates an isolated testing sandbox layer:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      STANDARDIZED TESTING SANDBOX                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Physical Microcontroller Firmware:                                 │
│    arduino/cps_edge_node/cps_edge_node.ino (Tested on ATmega328P/ESP32) │
│                                                                        │
│ 2. Desktop Pseudo-Hardware & Network Emulator:                         │
│    scripts/pseudo_cps_network_emulator.py                              │
│    • Linux PTY virtual serial port (/tmp/ttyCPS_EDGE)                  │
│    • Multi-robot odometry, scans, and heartbeat synthesis              │
│    • Dynamic network jitter and packet loss fault injection            │
│                                                                        │
│ 3. Automated End-to-End Regression Test Suite:                         │
│    scripts/test_distributed_cps.py                                     │
│    • Validates all 9 articles and 4 packages with exit code 0          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Observability & Telemetry Infrastructure

1. **Prometheus ROS Exporter:** Embeds a zero-dependency standard library HTTP server (`http.server.HTTPServer`) running on port `9100`. Exposes `/metrics` conforming to the Prometheus text exposition standard:
   - `robot_battery_percentage`
   - `robot_cpu_utilization_percent`
   - `robot_wifi_rssi_dbm`
   - `robot_topic_latency_ms`
   - `robot_heartbeat_timestamp_seconds`
2. **Health Watchdog:** Monitors periodic heartbeats. Silence exceeding the timeout ($3.0\text{s}$) flags the robot as `UNRESPONSIVE` and dispatches task reassignment failover events to `/cps/system_alerts`.
3. **Foxglove Studio Dashboards:** Pre-configured 3D multi-robot spatial layouts provided in `cps_telemetry/dashboards/foxglove_layout.json`.

---

## 7. Build & Verification Procedures

### 7.1 Compiling the Workspace
```bash
cd Distributed_CPS_ws
colcon build --symlink-install
source install/setup.bash
```

### 7.2 Running the Automated Test Suite
```bash
python3 scripts/test_distributed_cps.py
```
Output:
```text
===========================================================================
  ALL 10 TESTS PASSED (100% SUCCESS)
===========================================================================
Distributed CPS Workspace & Curriculum Articles 01-09 Fully Verified!
```

### 7.3 Launching the Multi-Robot Digital Twin
```bash
ros2 launch cps_bringup full_cps_simulation.launch.py
```
