# Article CPS-03: Microsecond Clock Synchronization (Chrony NTP) & Federated TF Trees

**Pedagogical Layer:** Distributed State Estimation & Coordinate Geometry  
**Focus Area:** Clock Drift Compensation, PTP/NTP Stratum Hierarchies, Multi-Robot TF Prefixes, and Frame Aggregation  
**Associated Package:** `setup_network.sh`, `cps_bringup`

---

## 1. The Clock Drift Catastrophe in Multi-Robot Systems

In ROS 2, transform lookup queries rely on timestamps:
$${}^{A}T_{B}(t) = \text{lookup\_transform}(A, B, t)$$

If Robot 1's clock leads Robot 2's clock by just $\Delta t = 50\,\text{ms}$, the transform buffer will reject lookups with:
$$\text{ExtrapolationException: Lookup would require extrapolation into the future/past.}$$

Unsynchronized clocks break Nav2 global path planning, LiDAR point-cloud accumulation, and shared map alignment.

---

## 2. Chrony NTP Architecture for Multi-Robot Subnets

We configure the Base Station as a local **Stratum 10 NTP Master Server**, and all edge robots as **high-precision NTP Clients**:

```text
┌──────────────────────────────────────────────────────────┐
│ BASE STATION (192.168.1.100) — Chrony Stratum 10 Server  │
└────────────────────────────┬─────────────────────────────┘
                             │ Local Subnet Broadcast (minpoll 2, maxpoll 4)
         ┌───────────────────┴───────────────────┐
         ▼                                       ▼
┌─────────────────────────────────┐   ┌─────────────────────────────────┐
│ Robot 1 (192.168.1.101)         │   │ Robot 2 (192.168.1.102)         │
│ Chrony Client (Jitter < 0.5 ms) │   │ Chrony Client (Jitter < 0.5 ms) │
└─────────────────────────────────┘   └─────────────────────────────────┘
```

### Client Configuration (`/etc/chrony/chrony.conf`):
```text
server 192.168.1.100 iburst minpoll 2 maxpoll 4
makestep 0.1 3
```

---

## 3. Federated TF Tree Architecture

Every robot maintains its own isolated kinematic chain rooted in a shared global `map` frame:

```text
                                 ┌───────────────┐
                                 │      map      │
                                 └───────┬───────┘
                     ┌───────────────────┴───────────────────┐
                     │                                       │
                     ▼                                       ▼
           ┌───────────────────┐                   ┌───────────────────┐
           │   robot1/odom     │                   │   robot2/odom     │
           └─────────┬─────────┘                   └─────────┬─────────┘
                     │                                       │
                     ▼                                       ▼
           ┌───────────────────┐                   ┌───────────────────┐
           │ robot1/base_link  │                   │ robot2/base_link  │
           └─────────┬─────────┘                   └─────────┬─────────┘
          ┌──────────┴──────────┐                 ┌──────────┴──────────┐
          ▼                     ▼                 ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ robot1/laser     │  │ robot1/imu       │  │ robot2/arm_base  │  │ robot2/camera    │
└──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 4. Implementation in ROS 2 Launch Files

Ensure all `robot_state_publisher` and `slam_toolbox` instances set the `frame_prefix` parameter:

```python
Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    namespace='robot1',
    parameters=[{
        'robot_description': urdf_content,
        'frame_prefix': 'robot1/'
    }]
)
```

---

## 5. Summary & Key Takeaways

- Chrony NTP guarantees $<1\,\text{ms}$ clock alignment across the Wi-Fi subnet.
- Prefixed TF trees eliminate frame collisions while maintaining a unified global reference frame.
- In [Article CPS-04](article_cps_04_heterogeneous_robot_roles_and_state_machines.md), we develop the heterogeneous role allocation state machines.
