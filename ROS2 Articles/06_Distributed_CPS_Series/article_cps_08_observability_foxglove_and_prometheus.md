# Article CPS-08: Observability, Foxglove Studio & Prometheus Fleet Telemetry

**Pedagogical Layer:** DevOps, Site Reliability & System Observability  
**Focus Area:** Real-Time Distributed Telemetry, 3D Foxglove Dashboards, Prometheus Metrics Exporter, and DDS Packet Sniffing  
**Associated Package:** `cps_telemetry`

---

## 1. Why Observability is Essential for CPS

In a multi-robot CPS, debugging by reading terminal logs on individual robots is impossible. Observability requires:
1. **Real-time 3D spatial visualization** of all robot poses, point clouds, and plans simultaneously.
2. **Time-series performance metrics** (CPU, RAM, battery voltage, Wi-Fi RSSI, DDS drop count).
3. **Automated health watchdogs** with millisecond alert routing.

---

## 2. The Complete CPS Observability Stack

```text
┌────────────────────────────────────────────────────────────────────────┐
│ FOXGLOVE STUDIO / RVIZ 2 (Spatial 3D Visualization)                    │
│ • Live Multi-Robot TF Trees       • Merged 2D Occupancy Grid (/map)    │
│ • LiDAR Scan Streams (/robot*/scan)• Camera Feeds & Target Markers      │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
┌──────────────────────────────────┴─────────────────────────────────────┐
│ PROMETHEUS & GRAFANA DASHBOARD (Time-Series Metrics)                   │
│ • Battery Voltage Curves          • CPU & Thermal Throttling Monitor   │
│ • Wi-Fi RSSI Signal Maps          • DDS Round-Trip Latency (ms)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. High-Precision DDS Network Latency Measurement

Message latency $\Delta t$ is calculated using hardware-synchronized timestamps:
$$\Delta t = t_{\text{arrival}} - (\text{header.stamp.sec} \times 10^9 + \text{header.stamp.nanosec})$$

If $\Delta t > 50\,\text{ms}$, the system automatically logs network degradation and throttles high-bandwidth image topics.

---

## 4. Summary & Key Takeaways

- Unified telemetry enables rapid diagnostic pinpointing across multi-machine fleets.
- In [Article CPS-09](article_cps_09_digital_twins_and_hardware_in_the_loop.md), we cover Digital Twins and physical hardware deployment.
