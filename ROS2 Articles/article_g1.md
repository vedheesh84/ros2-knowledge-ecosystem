## G1: HOW TO DEBUG A ROBOT WITHOUT GUESSING

*Purpose: Build engineering confidence. Teach systematic debugging methodology.*

### Must Answer
- How do you debug without random guessing?
- What tools does ROS2 provide?
- How do you observe system state?
- Why is logging a design concern, not an afterthought?

### Key Insight
Debugging is systematic investigation, not guessing. ROS2 provides introspection tools. Use them before modifying code.

---

### The Debugging Methodology

**Step 1: Observe**
- What is happening? (not why yet)
- Use ROS2 tools to inspect state
- Don't assume

**Step 2: Hypothesize**
- What could cause this behavior?
- Think systematically about possibilities

**Step 3: Test**
- Prove or disprove hypothesis
- Change one thing at a time
- Record results

**Step 4: Fix**
- Only after understanding root cause
- Don't band-aid symptoms

---

### Tool 1: ros2 topic echo

See what data is flowing:

```bash
$ ros2 topic echo /camera/image
header:
  seq: 1234
  timestamp: 1.234567
data: [...]
```

Is the camera publishing? At what rate? Valid data?

---

### Tool 2: ros2 topic hz

Measure frequency:

```bash
$ ros2 topic hz /camera/image
average rate: 29.8 Hz
```

Expected 30 Hz? Good. Expected 100 Hz but getting 15? Bottleneck.

---

### Tool 3: rqt_graph

Visualize connections:

```bash
$ rqt_graph
```

Opens GUI showing all nodes and topics. Missing connection? Immediate diagnosis.

---

### Tool 4: Logging

Print strategic debug information:

```cpp
RCLCPP_INFO(logger, "Obstacle detected at %.2f m", distance);
RCLCPP_WARN(logger, "Timeout waiting for response");
RCLCPP_ERROR(logger, "Critical failure: sensor offline");
```

Don't use printf. Use structured logging. Searchable. Timestamped.

---

### Real Debugging Example

**Problem:** Robot doesn't navigate to goal.

**Without methodology:** "Maybe the planner is broken?" → rewrite planner. Still doesn't work.

**With methodology:**
1. **Observe:** ros2 topic echo /navigation/goal → nothing? Topic remapped? Check launch file.
2. **Observe:** rqt_graph → is planner node connected? Missing nodes?
3. **Observe:** ros2 topic hz /navigation/goal → being published? At what rate?
4. **Hypothesis:** Planner never receives goal because topic is misspelled
5. **Test:** Launch file has `/navigation/goal` but code subscribes to `/nav/goal`
6. **Fix:** Correct the topic name in launch file
7. **Verify:** ros2 topic echo confirms data flowing. Robot navigates. Success.

Total time: 2 minutes. Without methodology: 2 hours.

---

### Hands-On Lab & Practical Code References

To practice the systematic 4-step inspection protocol on real faulty and noisy nodes:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_debugging/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_debugging/README.md)
- **Source Code to Inspect:**
  - `learning_debugging/faulty_node.py` — Implements intermittent failures and silent exceptions
  - `learning_debugging/noisy_node.py` — Injects payload corruption and rate fluctuations
- **Launch Orchestration:** `launch/debug_demo.launch.py`

#### 1. Launch the Faulty Environment
```bash
cd ROS2_kits_ws
source install/setup.bash
ros2 launch learning_debugging debug_demo.launch.py
```

#### 2. Execute the Systematic Introspection Protocol
In a second terminal, trace the issue without reading source code:

```bash
# Step 1: Discover who is alive
ros2 node list

# Step 2: Inspect node connectivity and endpoints
ros2 node info /faulty_node

# Step 3: Check topic publishing rate and inspect discovered topic
ros2 topic list
# Inspect the active topic (notice the intentional typo: /data_outptu)
ros2 topic echo /data_outptu
ros2 topic hz /data_outptu

# Step 4: Run system diagnostic auditor
ros2 doctor --report
```

---

### How This Connects Forward

Next: In Article G2 ("Reading the ROS2 Graph"), you'll learn advanced graph analysis. Finding bottlenecks. Identifying failure modes. System-level debugging.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Diagnose** problems systematically (observe, hypothesize, test)
2. **Use** ROS2 tools to inspect system state
3. **Avoid** guessing and random code changes
4. **Identify** root causes vs. symptoms
5. **Log** strategically (what to log, when, at what level)

---

*Word Count: 900*
*Reading Time: 6 minutes*
*Prerequisites: A0, A1, A2, C1*
*Next: G2*