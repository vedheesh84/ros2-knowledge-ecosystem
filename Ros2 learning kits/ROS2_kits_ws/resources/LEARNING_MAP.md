# ROS2 Learning Map

> **Purpose**: When you're stuck, start here. This map connects *symptoms* to *packages*.

---

## How to Use This Document

1. **Find your symptom** in the sections below
2. **Go to the linked package** and study the relevant node
3. **Run the demo** to see correct behavior
4. **Compare** with your broken code

This is NOT a tutorial. This is a **diagnostic tool**.

---

## Quick Reference: Package Purpose

| Package | One-Line Purpose |
|---------|------------------|
| learning_core | What IS a node? How does the graph work? |
| learning_comms | How do nodes talk? (topics, services, actions) |
| learning_execution | Who starts whom? How do launch files compose? |
| learning_lifecycle | How do nodes manage state and readiness? |
| learning_tf | Where am I? How do frames relate? |
| learning_simulation | Why does time behave differently in Gazebo? |
| learning_debugging | What tools exist to see inside the system? |
| learning_integration | How do all pieces fail together? |

---

## Symptom-Based Navigation

### "My node doesn't appear in `ros2 node list`"

**Likely cause**: Node not spinning, crashed on init, or not registered

**Go to**: `learning_core`
- Study: `hello_node.py` - minimal working node
- Check: Is `rclpy.init()` called before node creation?
- Check: Is `rclpy.spin()` keeping the node alive?
- Check: Does `super().__init__('node_name')` have a valid name?

**Debug command**:
```bash
ros2 run learning_core hello_node &
ros2 node list  # Should show /hello_node
```

---

### "My topic is not publishing / subscriber receives nothing"

**Likely cause**: QoS mismatch, wrong topic name, no spin

**Go to**: `learning_comms`
- Study: `talker_node.py` and `listener_node.py`
- Run: `ros2 launch learning_comms pubsub_demo.launch.py`

**Debug commands**:
```bash
ros2 topic list                    # Is topic visible?
ros2 topic info /topic_name        # Publisher/subscriber count?
ros2 topic hz /topic_name          # Is data flowing?
ros2 topic echo /topic_name        # What data?
```

**Common mistakes**:
- Topic name typo (`/chatter` vs `/Chatter`)
- QoS incompatibility (reliable vs best_effort)
- Timer not created (nothing triggers publish)

---

### "My service call hangs forever"

**Likely cause**: Server not running, server not spinning, client not waiting

**Go to**: `learning_comms`
- Study: `service_server_node.py` and `service_client_node.py`
- Run: `ros2 launch learning_comms service_demo.launch.py`

**Debug commands**:
```bash
ros2 service list                  # Is service visible?
ros2 service type /service_name    # Correct interface?
ros2 service call /service_name std_srvs/srv/Trigger  # Manual test
```

**Common mistakes**:
- Server node not spinning (blocked or crashed)
- Client calling before server exists (race condition)
- Wrong service type in client

---

### "My action never completes / no feedback"

**Likely cause**: Server execute_callback issue, goal rejection, cancellation

**Go to**: `learning_comms`
- Study: `action_server_node.py` (lines 143-186: goal/cancel callbacks)
- Study: `action_client_node.py`
- Run: `ros2 launch learning_comms action_demo.launch.py`

**Debug commands**:
```bash
ros2 action list                   # Is action visible?
ros2 action info /action_name      # Server/client count?
ros2 action send_goal /count_to_number learning_comms/action/CountToNumber \
    "{target_number: 5, delay_between_counts: 0.5}" --feedback
```

**Common mistakes**:
- Goal rejected (check `goal_callback` logic)
- `execute_callback` blocking without feedback
- Missing `goal_handle.succeed()` at end
- Not using `MultiThreadedExecutor` for concurrent handling

---

### "My launch file does nothing / nodes don't start"

**Likely cause**: Syntax error, wrong executable name, missing source

**Go to**: `learning_execution`
- Study: `separate_processes.launch.py` (minimal launch)
- Study: `conditional.launch.py` (with arguments)
- Run: `ros2 launch learning_execution separate_processes.launch.py`

**Debug commands**:
```bash
ros2 launch learning_execution separate_processes.launch.py --show-args
ros2 launch <pkg> <file> --debug   # Verbose output
```

**Common mistakes**:
- Forgot `source install/setup.bash` after build
- Executable name doesn't match `setup.py` entry_points
- `generate_launch_description()` doesn't return `LaunchDescription`
- Missing `from launch_ros.actions import Node`

---

### "Nodes start but can't find each other"

**Likely cause**: Namespace issue, remapping error, topic mismatch

**Go to**: `learning_execution`
- Study: `remapped.launch.py`
- Understand: How `remappings=[('/old', '/new')]` works

**Debug commands**:
```bash
ros2 node info /node_name          # See actual topic names
rqt_graph                          # Visual connection map
```

---

### "My robot state is wrong after restart"

**Likely cause**: No lifecycle management, state not reset

**Go to**: `learning_lifecycle`
- Study: `lifecycle_sensor_node.py`
- Understand: configure → activate → deactivate → cleanup cycle

**Debug commands**:
```bash
ros2 lifecycle list /node_name
ros2 lifecycle get /node_name
ros2 lifecycle set /node_name configure
ros2 lifecycle set /node_name activate
```

**Key insight**: Lifecycle nodes don't DO anything until activated. If your sensor "works sometimes", you might have a race condition that lifecycle management would fix.

---

### "My TF transform lookup fails / frame not found"

**Likely cause**: Frame not broadcast, timing issue, wrong frame name

**Go to**: `learning_tf`
- Study: `static_tf_node.py` (fixed transforms)
- Study: `dynamic_tf_node.py` (moving transforms)
- Study: `tf_listener_node.py` (lookup pattern)
- Run: `ros2 launch learning_tf full_tf_demo.launch.py`

**Debug commands**:
```bash
ros2 run tf2_tools view_frames     # Generate PDF of TF tree
ros2 run tf2_ros tf2_echo frame_a frame_b  # Live transform
rviz2                              # Add TF display
```

**Common mistakes**:
- Looking up transform before it's published (add timeout)
- Frame name typo (`base_link` vs `base_Link`)
- Missing static transform publisher in launch
- Child/parent order confusion in broadcaster

---

### "Simulation works but hardware doesn't"

**Likely cause**: Timing difference, sim_time mismatch, missing hardware driver

**Go to**: `learning_simulation`
- Study: `sim_time_node.py`
- Understand: `use_sim_time` parameter and `/clock` topic

**Key insight**:
```
Simulation: time comes from /clock topic (Gazebo controls it)
Hardware:   time comes from system clock (real wall time)
```

**Debug commands**:
```bash
ros2 param get /node_name use_sim_time
ros2 topic echo /clock             # Only exists in simulation
```

**Common mistakes**:
- Node uses `use_sim_time:=true` but Gazebo isn't running
- Timeouts calibrated for simulation (too fast for real hardware)
- Rate-based loops assume wall clock

---

### "I don't know what's happening inside my system"

**Go to**: `learning_debugging`
- Study: `noisy_node.py` (logging levels)
- Study: CLI introspection patterns

**Essential tools**:
```bash
# Graph inspection
ros2 node list
ros2 topic list
ros2 service list
ros2 action list
rqt_graph

# Data inspection
ros2 topic echo /topic
ros2 topic hz /topic
ros2 topic bw /topic

# Parameter inspection
ros2 param list /node
ros2 param get /node param_name
ros2 param dump /node

# Logging
ros2 run rqt_console rqt_console
```

---

### "Everything works alone but fails when combined"

**Go to**: `learning_integration`
- Study: `full_system.launch.py`
- Study: `robot_brain_node.py` (coordination)
- Study: `sensor_fusion_node.py` (data combination)

**Integration failure patterns**:

| Symptom | Likely Cause |
|---------|--------------|
| Works in isolation, fails together | Namespace collision |
| Random timing failures | Missing lifecycle coordination |
| Data arrives out of order | No synchronization policy |
| System hangs on startup | Circular dependency in launch |
| Memory grows over time | Subscriber queue overflow |

---

## Concept Dependencies

If you don't understand package X, you probably need package Y first:

```
learning_lifecycle  ← learning_execution ← learning_comms ← learning_core
learning_tf         ← learning_core
learning_simulation ← learning_tf, learning_execution
learning_debugging  ← learning_core (can be done anytime)
learning_integration← ALL OF THE ABOVE
```

---

## The Mental Model (Reference)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ROS2 SYSTEM LAYERS                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   APPLICATION        learning_integration                           │
│   (What robot does)  └── Coordinates everything                     │
│                                                                     │
│   ─────────────────────────────────────────────────────────────     │
│                                                                     │
│   BEHAVIOR           learning_lifecycle    learning_tf              │
│   (How robot thinks) └── State machine     └── Spatial reasoning    │
│                                                                     │
│   ─────────────────────────────────────────────────────────────     │
│                                                                     │
│   ORCHESTRATION      learning_execution                             │
│   (Who runs what)    └── Launch, compose, configure                 │
│                                                                     │
│   ─────────────────────────────────────────────────────────────     │
│                                                                     │
│   COMMUNICATION      learning_comms                                 │
│   (How nodes talk)   └── Topics, services, actions                  │
│                                                                     │
│   ─────────────────────────────────────────────────────────────     │
│                                                                     │
│   FOUNDATION         learning_core                                  │
│   (What is a node)   └── Graph, spin, callbacks                     │
│                                                                     │
│   ─────────────────────────────────────────────────────────────     │
│                                                                     │
│   CROSS-CUTTING      learning_debugging    learning_simulation      │
│   (Tools & context)  └── Introspection     └── Time & physics       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## When to Use This Map vs. Other Docs

| Situation | Use This |
|-----------|----------|
| Something is broken | LEARNING_MAP.md (you are here) |
| Learning a concept from scratch | Package README |
| Step-by-step tutorial | LEARNING_PATH.md |
| Terminology confusion | GLOSSARY.md |
| Understanding the architecture | Main README.md |

---

## Version

Map version: 1.0
Last updated: 2025-12-29
Workspace analyzed: ROS2_kits_ws (8 packages, 24 nodes)
