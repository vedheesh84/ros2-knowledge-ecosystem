## B2: SERVICES: WHEN ROBOTICS NEEDS CERTAINTY

*Purpose: Introduce request-response pattern. Teach synchronous communication and guaranteed delivery.*

### Must Answer
- How are services different from topics?
- Why are they synchronous?
- When do you need a service instead of a topic?
- What happens if a service doesn't respond?

### Key Insight
Services are how robots ask questions and get guaranteed answers. The caller waits. The service responds. Both parties know the transaction succeeded (or failed with timeout).

---

### The Mental Model: Telephone Call

A service is like a phone call:

- **You call** and wait for answer
- **Other person** hears phone, picks up
- **You ask** a question
- **Other person** responds
- **You** have confirmation (they heard you, they answered)

Synchronous. Both parties are engaged. The caller waits. The responder must answer (or call times out).

---

### Client-Server Pattern

A **client** calls a service:

```
Battery query client: "What's your battery level?"
Waits for response...
```

A **service server** handles the request:

```
Battery server receives: "What's your battery level?"
Responds: "85% charged"
Client receives response
```

Request and response are paired. The client doesn't continue until response arrives (or timeout).

---

### Real Example: Critical Queries

Robot system needs to verify state before executing dangerous tasks:

```
Motion planner calls get_battery_level service
  ↓
Battery manager responds: "85%"
  ↓
Planner: "Good, we have power. Proceeding with navigation."

vs.

Planner reads latest battery topic value (might be stale)
Planner: "Last reading was 85%, probably still true?"
  ↓
Actually battery is 5%, robot dies mid-navigation
```

Services provide certainty. Topics don't.

---

### Why Not Just Use Topics?

You could publish battery level continuously on a topic:

```
Battery node publishes: 85% (every 10 seconds)
Planner subscribes, reads latest value: 85%
Planner thinks: "battery is 85%"
```

Problem: What if the reading is stale?

- Battery reading published 9 seconds ago
- Battery was draining fast
- Actual battery is now 5%
- Planner thinks it's 85% (dangerous assumption)

With a service:

```
Planner calls battery service NOW
Service returns current value (fresh)
Planner knows it's not stale
```

---

### Blocking and Timeouts

Services are **blocking**. The client waits.

```
Planner calls battery service
Planner stops here ↓
    ↓
    Waiting for response...
    ↓
Server responds
Planner continues
```

If server is dead or slow, client waits. If it waits too long (timeout), the call fails.

Default timeout: 10 seconds.

**Risk:** If you call a slow service in a loop, you create latency. This is why topics are better for frequent updates.

---

### Common Misconceptions

**Myth: Services are always better because they guarantee delivery**

Truth: Services are better ONLY when you need synchronization. For streaming data, topics are more efficient.

**Myth: You should use services for everything that matters**

Truth: Critical one-time queries → services. Continuous monitoring → topics.

---

### Hands-On Lab & Practical Code References

To run synchronous request-response transactions and trigger services via CLI:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_comms/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_comms/README.md)
- **Source Code to Inspect:**
  - `learning_comms/service_server_node.py` — Implements service callback returning computed responses
  - `learning_comms/service_client_node.py` — Asynchronous future-based service invocation
- **Launch Orchestration:** `launch/service_demo.launch.py`

#### 1. Launch the Service Demo
```bash
cd ROS2_kits_ws
source install/setup.bash
ros2 launch learning_comms service_demo.launch.py
```

#### 2. Call Services Directly via CLI
In a second terminal:

```bash
# 1. Discover all active services
ros2 service list

# 2. Inspect the service request/response schema type
ros2 service type /add_two_ints

# 3. Call the service synchronously with typed JSON arguments
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 14, b: 28}"
# Output: response: example_interfaces.srv.AddTwoInts_Response(sum=42)
```

---

### How This Connects Forward

Next: In Article B3 ("Actions: Long-Running Decisions and Feedback"), you'll learn about tasks. Services work for quick queries. But what if the task takes 5 seconds? 5 minutes? That's where actions come in.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Explain** why battery query needs a service (not a topic)
2. **Identify** when blocking is acceptable vs. problematic
3. **Predict** what happens if a service server crashes
4. **Reason** about timeout: "If my service takes 2 seconds, timeout should be..."
5. **Design** a system: "Configuration changes should use services because..."

---

*Word Count: 1,300*
*Reading Time: 8 minutes*
*Prerequisites: A0, A1, A2, B1, B4a*
*Next: B3*