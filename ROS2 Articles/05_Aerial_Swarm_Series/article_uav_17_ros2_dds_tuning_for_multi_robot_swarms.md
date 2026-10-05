## UAV 17: ROS2 DDS TUNING & DISCOVERY SERVER FOR MULTI-ROBOT SWARMS

*Purpose: Scale ROS2 to multi-robot swarms without network collapse. Master ROS2 DDS discovery, contrast Multicast Discovery with FastDDS Discovery Server, configure namespaces, and tune Quality of Service (QoS) for lossy wireless ad-hoc networks.*

### Must Answer
- Why does default ROS2 Simple Discovery Protocol (multicast broadcast) overwhelm Wi-Fi networks when $> 5$ robots connect?
- What is the FastDDS / CycloneDDS Discovery Server architecture, and how does it reduce discovery network traffic by $90\%$?
- How do we configure clean multi-robot namespacing (`/drone1/cmd_vel`, `/drone2/odom`) without topic collisions?
- What is the optimal QoS profile for swarm state telemetry over lossy Wi-Fi (Best Effort, Transient Local, Volatile)?
- How do ROS2 domain IDs (`ROS_DOMAIN_ID`) isolate different swarm sub-teams in shared radio environments?

### Key Insight
Default ROS2 discovery uses multicast flooding ($O(N^2)$ traffic), which brings Wi-Fi routers to their knees with a 10-drone swarm; configuring a centralized or decentralized Discovery Server reduces discovery traffic to $O(N)$, enabling reliable large-scale swarm communication.

---

### 1. Multicast Discovery Storms vs. Discovery Server

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DDS DISCOVERY ARCHITECTURES                        │
│                                                                             │
│   DEFAULT MULTICAST DISCOVERY (O(N^2) Storm):                               │
│   Every node broadcasts discovery packets to every other node continuously. │
│   • 10 drones \times 20 nodes = 200 nodes \implies 40,000 discovery links!  │
│   • Wi-Fi router packet queue overflows; high jitter and lost telemetry.   │
│                                                                             │
│   FAST-DDS DISCOVERY SERVER (O(N) Point-to-Point):                          │
│   Nodes connect directly to a lightweight Discovery Server daemon.          │
│   • Zero multicast network flooding.                                        │
│   • Instant, deterministic node discovery even over lossy wireless mesh.    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. XML FastDDS Discovery Server Configuration

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<dds xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
    <profiles>
        <participant profile_name="discovery_server_client">
            <rtps>
                <builtin>
                    <discovery_config>
                        <discoveryProtocol>CLIENT</discoveryProtocol>
                        <discoveryServersList>
                            <RemoteServer prefix="44.53.01.5f.45.50.52.4f.53.49.4d.41">
                                <metatrafficUnicastLocatorList>
                                    <locator>
                                        <udpv4>
                                            <address>192.168.1.100</address>
                                            <port>11811</port>
                                        </udpv4>
                                    </locator>
                                </metatrafficUnicastLocatorList>
                            </RemoteServer>
                        </discoveryServersList>
                    </discovery_config>
                </builtin>
            </rtps>
        </participant>
    </profiles>
</dds>
```

---

### 3. Hands-On Lab & Practical Code References

#### 1. Inspecting Multi-Drone Namespacing Architecture:
- Bringup Orchestration: [`ros2_drone_swarm_kit/src/drone_bringup/launch/swarm_3drones.launch.py`](../../Ros2%20learning%20kits/ros2_drone_swarm_kit/src/drone_bringup/launch/swarm_3drones.launch.py)
