## MM 16: REAL-WORLD PHYSICAL CHALLENGES, CALIBRATION & DEBUGGING

*Purpose: Master real-world debugging in physical mobile manipulation. Analyze mechanical backlash, wheel slip on warehouse floors, battery discharge curves, ambient lighting variations, and systematic diagnostic methodologies.*

### Must Answer
- What are the biggest physical differences between Gazebo simulation and real hardware deployment?
- What is Gearbox Backlash, and how does mechanical play in cheap servo gears ruin end-effector precision?
- How do battery discharge curves affect motor RPM, servo holding torque, and LiDAR spin rates?
- How do we debug multi-node communication bottlenecks, dropped frames, and memory leaks on SBCs?
- What is a systematic pre-flight hardware diagnostic checklist before running autonomous missions?

### Key Insight
In simulation, physics is deterministic and parameters are exact; on physical hardware, batteries discharge, gears have mechanical backlash, ambient sun glares wash out cameras, and floor dust causes wheel slip.

---

### 1. Simulation vs. Physical Reality Discrepancies

| Phenomenon | Gazebo Physics Simulation | Real Physical Hardware | Engineering Mitigation |
|---|---|---|---|
| **Joint Backlash** | $0.0^\circ$ (Zero gear play) | $\pm 1.5^\circ - 3.0^\circ$ mechanical slop | Visual servoing / Closed-loop eye-in-hand tracking |
| **Wheel Friction** | Uniform Coulomb friction | Dust, floor seams, uneven wheel slip | IMU + Wheel Odometry EKF sensor fusion |
| **Battery Power** | Infinite, constant voltage | Voltage sags from $12.6\text{ V} \to 10.5\text{ V}$ | Regulated UBEC power supplies + Voltage monitoring |
| **Lighting / Vision**| Constant directional light | Glare, shadows, fluorescent flicker | HSV color thresholding + Adaptive histogram equalization |
| **Latency / Jitter** | Synthetic lock-step clock | Asynchronous OS scheduling ($5 - 20\text{ ms}$) | Low-latency QoS + Multi-threaded ROS2 executors |

---

### 2. The 10-Point Pre-Flight Hardware Checklist

Before launching an autonomous mobile manipulation mission:
1. **Battery Check**: Measure logic and motor batteries ($V > 11.4\text{ V}$ for 3S LiPo).
2. **E-Stop Readiness**: Verify physical emergency stop switch cuts motor power instantly.
3. **TF Sanity**: Run `ros2 run tf2_tools view_frames` to verify zero broken branches.
4. **Camera Focus & White Balance**: Ensure optical lens is focused at $0.25\text{ m}$ reach distance.
5. **LiDAR Spin Rate**: Verify `/scan` publishes at steady $10\text{ Hz}$ without packet drops.
6. **Joint Homing**: Confirm all arm servos center cleanly at $0.0\text{ rad}$ home pose.
7. **Gripper Effort**: Verify stall current threshold triggers without overheating servo.
8. **Footprint Inflation**: Check RViz local costmap displays expanded robot footprint.
9. **SBC CPU Load**: Verify `htop` shows CPU usage $< 75\%$ across all cores.
10. **Clear Floor Path**: Ensure workspace has no stray cables or high-pile rugs.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Generating TF Diagnostic Graphs:
```bash
# Generate PDF diagram of the complete live transform tree
ros2 run tf2_tools view_frames
```

#### 2. Running Diagnostic Monitoring:
```bash
# Monitor ROS2 diagnostic messages
ros2 topic echo /diagnostics
```
