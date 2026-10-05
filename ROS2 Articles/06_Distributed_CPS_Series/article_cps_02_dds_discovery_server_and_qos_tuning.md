# Article CPS-02: DDS Discovery Server Architecture & Quality of Service (QoS) Tuning

**Pedagogical Layer:** Networking & Distributed Middleware  
**Focus Area:** DDS Wire Protocols, Multicast Storm Mitigation, FastDDS Discovery Server XML, and Deterministic QoS  
**Associated Package:** `cps_bringup/config/fastdds_discovery_server.xml`, `cps_bringup/config/qos_profiles.yaml`

---

## 1. The Wi-Fi Multicast Discovery Breakdown

By default, ROS 2 nodes discover each other using the **Simple Participant Discovery Protocol (SPDP)**. Each node periodically broadcasts its entity metadata over UDP multicast.

In a multi-robot system with $N$ robots and $M$ nodes per robot, the discovery traffic scales quadratically:
$$\text{Discovery Messages} \propto (N \times M)^2$$

Over standard 802.11 Wi-Fi, multicast frames are transmitted at the lowest mandatory base rate without hardware acknowledgement (ACK) or retransmission. Under heavy network traffic, discovery packets drop, causing robots to randomly fail to detect peer topics.

---

## 2. FastDDS Discovery Server Architecture

The **Discovery Server** converts $O(N^2)$ multicast discovery into $O(N)$ point-to-point unicast communication:

```text
┌──────────────┐                  ┌────────────────────────────────────────┐
│   Robot 1    │──Unicast (TCP)──▶│  Base Station: FastDDS Discovery Server│
│ (/robot1/*)  │◀─Entity List─────│            (192.168.1.100:11811)       │
└──────────────┘                  └────────────────────────────────────────┘
                                                       ▲
┌──────────────┐                                       │
│   Robot 2    │──────────────Unicast (TCP)────────────┘
│ (/robot2/*)  │
└──────────────┘
```

---

## 3. FastDDS Discovery Server XML Profile

Deploy the following XML profile (`fastdds_discovery_server.xml`) on all edge robots and the base station:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<dds xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
    <profiles>
        <participant profile_name="cps_discovery_server_profile" is_default_profile="true">
            <rtps>
                <builtin>
                    <discovery_config>
                        <discoveryProtocol>SERVER</discoveryProtocol>
                        <discoveryServersList>
                            <RemoteServer prefix="44.53.00.5f.45.50.52.4f.53.49.4d.41">
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

## 4. QoS Tuning Matrix for Heterogeneous Fleets

| Topic Stream | Reliability | Durability | History & Depth | Rationale |
|---|---|---|---|---|
| `/robot*/scan`, `/camera/image` | `BEST_EFFORT` | `VOLATILE` | `KEEP_LAST`, Depth=1 | Sensor data is ephemeral; dropping stale frames is better than queuing delay. |
| `/robot*/cmd_vel` | `RELIABLE` | `VOLATILE` | `KEEP_LAST`, Depth=5 | Motor velocity setpoints must not be lost during maneuvers. |
| `/map`, `/robot*/map` | `RELIABLE` | `TRANSIENT_LOCAL` | `KEEP_LAST`, Depth=1 | Static maps must be latched for late-joining robots. |
| `/cps/mission_state`, `/alerts` | `RELIABLE` | `TRANSIENT_LOCAL` | `KEEP_ALL` | Mission critical state changes must never be dropped. |

---

## 5. Summary & Key Takeaways

- Multicast discovery is the primary cause of multi-robot Wi-Fi unreliability.
- Unicast Discovery Servers eliminate discovery storms and reduce network overhead by over $80\%$.
- In [Article CPS-03](article_cps_03_time_sync_chrony_and_federated_tf.md), we solve clock drift and federated TF tree management.
