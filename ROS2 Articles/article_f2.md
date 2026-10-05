## F2: TIME IN ROS2: REAL TIME VS. SIMULATED TIME

*Purpose: Teach the /clock topic. Avoid subtle timing bugs in deterministic systems.*

### Must Answer
- Why does ROS2 care about time?
- What is simulated time vs. real time?
- How does /clock control simulation?
- How do nodes stay synchronized?

### Key Insight
Time is a shared resource in ROS2. Simulation controls /clock to enable deterministic testing. Nodes that respect /clock work seamlessly in sim and reality.

---

### The Problem: Timing Dependency

Imagine your node does:

```cpp
start_time = current_time()
while (current_time() - start_time < 5.0 seconds) {
  // do something for 5 seconds
}
```

In real world: waits 5 actual seconds. Works.

In simulation: should wait 5 simulated seconds. But how does the node know?

---

### The Solution: /clock Topic

ROS2 publishes time on `/clock` topic. Nodes read it.

**Real robot:**
- `/clock` publishes actual time continuously
- Nodes read actual time
- Everything runs in real time

**Simulation:**
- Simulator publishes `/clock` at a different rate
- Same node reads `/clock` and gets simulated time
- Simulation can run slow, fast, or even backwards (for replay)

Same code. Different time source. Magic.

---

### Real Example: Navigation Timeout

Your planner times out if planning takes >5 seconds:

```cpp
start_time = get_clock()->now()
plan_trajectory(...)
if (get_clock()->now() - start_time > 5.0 seconds) {
  timeout!
}
```

**In real world:**
- Timer uses wall clock
- If planning takes 6 seconds, timeout triggers
- Correct behavior

**In simulation:**
- Timer uses `/clock`
- Simulator might run 10x faster than real time
- Simulated 6 seconds = 0.6 real seconds
- Timer works correctly in sim

---

### Deterministic Testing

Simulation can replay exact same scenario:

```
Scenario: Robot navigates obstacle field
Run 1: Robot follows path X, crashes at time T
Fix code
Run 2: Simulation replays same scenario at same time
Robot follows path Y, succeeds
Guaranteed reproducibility
```

Real world: Can't replay (world changes, uncertainties).

Simulation: Can replay (deterministic `/clock`).

---

### Hands-On Lab & Practical Code References

To observe the `/clock` topic and test the behavior of `use_sim_time`:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_simulation/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_simulation/README.md)
- **Source Code to Inspect:** `learning_simulation/sim_time_node.py` — Demonstrates node clock source selection (`rclpy.time.Time`) based on the `use_sim_time` parameter

#### 1. Run Node with Simulation Time Enabled
```bash
cd ROS2_kits_ws
source install/setup.bash

# Run node configured to consume simulated clock ticks
ros2 run learning_simulation sim_time_node --ros-args -p use_sim_time:=true
```

#### 2. Publish Simulated Clock Ticks
In a second terminal:

```bash
# 1. Observe that node timers pause when /clock is not publishing
ros2 topic list

# 2. Publish discrete simulated clock timestamps manually
ros2 topic pub /clock rosgraph_msgs/msg/Clock "{clock: {sec: 100, nanosec: 0}}" --rate 10
```

Notice how node timers, timeouts, and callbacks advance strictly according to `/clock` ticks rather than system wall time.

---

### How This Connects Forward

Next: In Article G1 ("How to Debug Without Guessing"), you'll learn debugging tools. Time awareness is key to effective debugging. ROS2 provides tools to inspect and replay time-dependent behavior.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Explain** why `/clock` is essential
2. **Predict** timing behavior in sim vs. real
3. **Design** time-aware algorithms that work in both
4. **Debug** timing issues (identify simulation vs. real time problems)
5. **Use** time for deterministic testing

---

*Word Count: 700*
*Reading Time: 5 minutes*
*Prerequisites: F1*
*Next: G1*