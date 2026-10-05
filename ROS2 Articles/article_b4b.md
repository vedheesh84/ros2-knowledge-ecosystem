## B4b: CHOOSING BETWEEN TOPIC, SERVICE, AND ACTION (A Decision Framework with Real Trade-Offs)

*Purpose: Compare all three patterns side-by-side. Show trade-offs, edge cases, and real-world decisions. Teach learners to reason about constraints.*

### Must Answer
- What are the concrete trade-offs between the three patterns?
- When do professionals choose each one?
- What breaks when you choose wrong?
- How do you decide in edge cases?

### Key Insight
There's rarely a "perfect" choice. Each pattern trades off reliability for speed, coupling for simplicity, synchronicity for parallelism. Professionals choose based on the specific constraints of their problem.

---

### The Trade-Offs Matrix

| Dimension | Topic | Service | Action |
|-----------|-------|---------|--------|
| **Frequency** | Best for frequent (10+ Hz) | Best for infrequent (<1 Hz) | Best for on-demand |
| **Reliability** | Best-effort (msg may be lost) | Guaranteed (must receive response or timeout) | Acknowledged (goal must be accepted) |
| **Latency** | Lowest (fire-and-forget) | Medium (wait for response) | Medium-high (task time varies) |
| **Coupling** | Loosest (publisher doesn't know subscribers) | Tighter (request/response pair) | Tightest (task coordination) |
| **Complexity** | Lowest (just publish) | Medium (synchronization required) | Highest (goal/feedback/cancel logic) |
| **Throughput** | Highest (no blocking) | Lower (must wait for response) | Lowest (task-dependent) |
| **Use If** | Streaming data | One-time queries | Long-running tasks |

---

### Side-by-Side Comparison: A Real Example

**Problem:** A robot with a temperature sensor needs to:
1. Stream temperature readings continuously
2. Respond to temperature queries
3. Execute temperature-based adjustments (e.g., "cool down to 20°C")

**Option A: Everything as Topics**

```
Temperature sensor publishes to /temperature_reading every 100ms

Subscriber 1: reads /temperature_reading, logs to file
Subscriber 2: reads /temperature_reading, displays on dashboard
Subscriber 3: reads /temperature_reading, checks if too hot
```

Pros:
- Simple. One topic. No coordination.
- Scalable. Add as many subscribers as you want.
- High throughput. No blocking.

Cons:
- Query "/temperature_reading once" is awkward. You get a stale reading (last published value).
- No guarantee subscribers heard you.
- Hard to distinguish between "no one cares" and "someone's listening."

**Option B: Everything as Services**

```
Temperature service: when called, returns current temperature

Client 1 at startup: call temperature service → get reading
Client 2 every 10 seconds: call temperature service → get reading
Client 3 every 5 seconds: call temperature service → get reading
```

Pros:
- Guaranteed answer. You know the response is current.
- Synchronous. Simple request-response pattern.

Cons:
- Latency. Clients wait for answers. If sensor reading takes 10ms, clients are blocked.
- Client 2 and Client 3 are calling the service simultaneously → contention.
- Continuous reading (e.g., log every 100ms) becomes 10 requests/second to a single service. Bottleneck.

**Option C: Mixed Approach (Real-World Solution)**

```
Temperature sensor publishes to /temperature_reading every 100ms

For continuous use: subscribe to /temperature_reading
For one-time query: call temperature service
For autonomous control: send temperature_control action ("cool to 20°C")
```

Pros:
- Best of both worlds. Stream for efficiency. Query for certainty. Actions for complex tasks.
- Subscribers are decoupled. Services are for occasional queries. Actions handle complex logic.

Cons:
- Slightly more infrastructure. But not much.

**This is how professionals build systems.** Not dogmatically one pattern, but pragmatically mixed.

---

### Edge Cases and Real-World Decisions

**Edge Case 1: High-Frequency Queries**

Problem: You need battery level at 20 Hz (unusual, but possible).

Option A: Create a service. Call it 20 times per second.
- Works, but not ideal. Services are designed for occasional calls.

Option B: Create a topic. Subscribe to battery level.
- Better. Battery publishes at 20 Hz. You read it asynchronously.

Decision: Switch to topic if frequency is high.

**Edge Case 2: Critical One-Time Query**

Problem: Before navigation starts, you must know the battery level. If you can't get it, abort.

Option A: Topic subscription. Read latest value.
- Risky. What if battery level was never published? You read undefined data.

Option B: Service call with timeout.
- Better. Service call waits for response. If no response in 1 second, fail safely.

Option C: Topic + service hybrid.
- Best. Topic for continuous monitoring. Service for critical one-time query.

Decision: Use service for critical queries. Use topic for monitoring.

**Edge Case 3: Task that Might Take 10 Seconds or 2 Hours**

Problem: "Process this video file." Could be 10 seconds for a short clip or 2 hours for a long one.

Option A: Service call.
- Client waits for 2 hours. Network drops? Client fails. Bad.

Option B: Topic broadcast.
- No feedback. Client doesn't know if task succeeded. Bad.

Option C: Action.
- Client sends goal. Server accepts (immediately). Server works on it asynchronously. Sends progress: "20% done... 50% done..." Client can cancel.

Decision: Use action for long-running, unpredictable tasks.

---

### Common Mistakes (Analyzed)

**Mistake 1: Using Topic for Critical Configuration**

Wrong:
```
publish "max_speed = 0.5 m/s" to configuration topic
hope the motor controller subscribes to it
```

Problem: Motor might start before configuration is set. Or configuration might be missed. No guarantee.

Right:
```
call configuration service ("set max_speed to 0.5 m/s")
wait for confirmation
now you know it's set
```

**Mistake 2: Using Service for Streaming**

Wrong:
```
Main loop:
  image = call camera_image service
  process image
```

Problem: Service call blocks. If processing takes 100ms and camera runs at 30 FPS, you process only 3 images per second (not 30).

Right:
```
Subscribe to camera_image topic
When new image arrives, process it
30 images per second, no blocking
```

**Mistake 3: Using Action for Simple Queries**

Wrong:
```
send "get_battery_percentage" action goal
wait for action feedback
receive result: 85%
```

Problem: Massive overkill. Action machinery is for complex tasks. Battery query is trivial.

Right:
```
call get_battery service
receive response: 85%
```

---

### Decision Matrix for Common Robotics Tasks

| Task | Pattern | Why |
|------|---------|-----|
| Camera frames | Topic | Streaming, loss acceptable, high frequency |
| Motor commands | Topic | Streaming, fire-and-forget, high frequency |
| Battery level check | Service | One-time query, must guarantee answer |
| Arm joint angles | Topic | Streaming feedback, high frequency |
| Navigation goal | Action | Long-running, feedback desired, cancellable |
| Configuration change | Service | One-time, must guarantee acceptance |
| Sensor reading (temperature) | Topic (+ optional service) | Streaming + occasional query |
| Shutdown command | Service | Must guarantee execution, one-time |
| Gripper open/close | Action (or service for simple) | Quick task, might need feedback |

---

### The Zone of Confusion: Which Pattern for "Almost There" Cases?

**Case 1: Occasional Sensor Query (Once Per Second)**

Could be service (one-time query) or topic (subscribe to infrequent updates).

Decision heuristic: If you **need the answer right now and must know if it failed**, use service. If you can **live with slightly stale data and don't care if no one publishes**, use topic.

Example: Battery level → service (must know). Robot health status → topic (occasional broadcast).

**Case 2: Control Command That Happens Once Per 5 Seconds**

Could be topic (occasional message) or service (occasional query).

Decision heuristic: If it's **"set this value and make sure it's received,"** use service. If it's **"broadcast this command and move on,"** use topic.

Example: "Rotate turret 90 degrees" → service (need confirmation). "Publish status" → topic (fire and forget).

---

### Real Robotics Example: Mobile Robot with Dock

This robot needs to:
1. Stream lidar/camera data continuously
2. Query battery periodically
3. Execute "go to dock" task on command
4. Respond to emergency stop immediately

Pattern choices:
- **Lidar/Camera:** Topics (streaming)
- **Battery query:** Service (periodic checking with guaranteed response)
- **Dock navigation:** Action (long-running task with feedback)
- **Emergency stop:** Topic (broadcast, must be fast, okay if one subscriber misses it)

Why emergency stop as topic (not service)? Because you want it to propagate to *all* subscribers immediately. If you use service, you'd have to call *every* node individually (slow). Topic broadcasts to all (fast).

---

### How to Reason About Your Own Problem

1. **Sketch the data flow.** What needs to talk to what?
2. **For each edge,** ask: frequency, reliability, latency needs?
3. **Apply the decision matrix.**
4. **Check for anti-patterns.** Did you choose topic for a critical query? Service for streaming?
5. **Sketch the alternative.** If you chose service, would topic work? Why/why not?

If you can explain your choice, you're good.

---

### Hands-On Lab & Practical Code References

To benchmark the trade-offs between asynchronous topic throughput and synchronous service latency:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_comms/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_comms/README.md)
- **Demos to Compare:**
  - `launch/pubsub_demo.launch.py` — High-frequency streaming throughput
  - `launch/service_demo.launch.py` — Synchronous round-trip request/response latency

#### 1. Measure Streaming Topic Latency vs Frequency
```bash
cd ROS2_kits_ws
source install/setup.bash

# Run pub/sub streaming
ros2 launch learning_comms pubsub_demo.launch.py

# In another terminal, inspect delivery rate and latency jitter
ros2 topic hz /chatter
```

#### 2. Observe Synchronous Service Blocking
```bash
# Call service in a rapid loop to observe synchronous client blocking overhead
for i in {1..10}; do ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: $i, b: $i}"; done
```

Notice the round-trip latency overhead compared to the fire-and-forget streaming throughput of topics.

---

### How This Connects Forward

Next: In Article C1 ("Why Launch Files Are System Design"), you'll see how to coordinate all these patterns together in a real system. The launch file is where you wire up nodes, topics, services, and actions to create a functioning robot.

---

### Learning Outcome Test

After reading this article, you should be able to:

1. **Defend** your choice of communication pattern for any robotics task
2. **Identify** mistakes in system designs (e.g., "That should be a topic, not a service, because...")
3. **Explain** the trade-offs (e.g., "Topics are faster but less reliable than services because...")
4. **Reason** about edge cases (e.g., "For high-frequency queries, switch from service to topic because...")
5. **Design** a mixed-pattern system (using topics, services, and actions appropriately)

If you can do these, you understand not just how to use patterns, but *when and why* to use them.

---

*Word Count: 2,200*
*Reading Time: 14 minutes*
*Prerequisites: A0, A1, B1, B2, B3 (ideally), B4a (required)*
*Next: C1*