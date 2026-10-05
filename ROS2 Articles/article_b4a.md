## B4a: HOW TO THINK ABOUT COMMUNICATION CHOICES (Decision Heuristics)

*Purpose: Teach decision frameworks BEFORE diving into concrete examples. Enable learners to make independent choices about communication patterns.*

### Must Answer
- When do you use broadcast vs. request-response vs. long-running tasks?
- What questions should you ask before choosing a communication pattern?
- How do real robot constraints guide your choice?
- What happens when you choose wrong?

### Key Insight
Choosing a communication pattern isn't about memorizing rules. It's about asking the right questions about your data and your timing.

---

### The Decision Framework: Four Questions

Before you write a single node, ask these four questions:

**Question 1: How Often Does This Data Change?**

- **Changes continuously** (30+ times per second): Broadcast (topic)
  Example: Camera images (30 FPS), motor feedback (100+ Hz)
  
- **Changes rarely** (<1 time per second): Request-response (service)
  Example: Battery level (check once per minute), configuration query (once at startup)
  
- **Changes during a task** (on-demand): Goal-feedback (action)
  Example: "Navigate here" (happens when you ask), "Pick this object" (requested, not continuous)

**Question 2: What Happens if the Message Is Lost?**

- **Loss is acceptable**: Broadcast (topic)
  Example: Camera frame rate is 30 FPS. Losing one frame is fine (another arrives in 33ms).
  
- **Loss is unacceptable**: Request-response (service)
  Example: "What's your battery?" You need the answer. If the message is lost, you ask again.
  
- **Loss during task is unusual, but recovery is possible**: Goal-feedback (action)
  Example: "Navigate to room 5." Network drops momentarily. You resend the goal or cancel it.

**Question 3: Do You Need a Guarantee of Delivery?**

- **No guarantee needed** (best-effort): Broadcast
  The publisher doesn't care if anyone listens. It just publishes.
  
- **Guarantee required** (confirmed delivery): Request-response
  The client doesn't continue until the server responds. Synchronous guarantee.
  
- **Guarantee with flexibility** (can be cancelled): Goal-feedback
  The client knows the task was accepted. Can monitor progress or cancel.

**Question 4: How Long Does Processing Take?**

- **Fast** (<10ms): Any pattern works
  
- **Slow** (100ms - seconds): Use broadcast or goal-feedback, NOT request-response
  Why? Because request-response blocks the requester. If the server is slow, the requester waits. Bad for real-time.
  
- **Very slow** (seconds to hours): Use goal-feedback
  Why? Because broadcast is for "fire and forget." Goal-feedback lets you track progress and cancel if needed.

---

### The Decision Tree (Simplified)

```
START: "I need to communicate something"

Is this continuous, streaming data (>1 Hz)?
  YES → Use TOPIC (broadcast)
  NO → Go to next question

Is this a query where I need a guaranteed answer?
  YES → Use SERVICE (request-response)
  NO → Go to next question

Is this a task I might want to cancel mid-way?
  YES → Use ACTION (goal-feedback)
  NO → You probably don't need to communicate this
```

---

### Red Flags: Choosing Wrong

**Red Flag 1: Using Request-Response for Streaming Data**

Wrong:
```
Main loop:
  response = ask_camera_for_image()
  wait for response
  process image
```

This blocks between each image. Your code stops while waiting for the camera. Latency explodes.

Right:
```
Camera publishes images to topic
Main loop:
  receive_latest_image_if_available()
  process image immediately
```

Your code never blocks on the camera.

**Red Flag 2: Using Broadcast for Critical Queries**

Wrong:
```
publish "battery status?" to a topic
hope someone publishes the answer
```

You have no guarantee you get an answer. What if no one is listening?

Right:
```
call battery_query service
wait for answer (with timeout)
now you have the answer
```

**Red Flag 3: Using Request-Response for Long-Running Tasks**

Wrong:
```
client calls "navigate" service
client blocks for 5 minutes waiting for response
```

The client is frozen the entire time. If the network flickers, the whole operation fails.

Right:
```
client sends "navigate" action goal
server accepts goal, starts navigating
server sends progress: "20% done... 50% done..."
client can check progress or cancel anytime
```

---

### Real-World Reasoning Examples

**Scenario 1: Publishing Motor Speed**

Question 1: How often changes? → Continuously (100+ Hz)
Question 2: Okay to lose? → Yes (next command is coming in 10ms)
Question 3: Need guarantee? → No
Question 4: How long? → Instant

Answer: **TOPIC**

Why? Motor speed is streaming. Missing one update is fine. The next command is already on the way.

**Scenario 2: Querying Robot Battery Level**

Question 1: How often changes? → Rarely (once per minute check)
Question 2: Okay to lose? → No (you need the answer)
Question 3: Need guarantee? → Yes
Question 4: How long? → Fast (milliseconds)

Answer: **SERVICE**

Why? Battery is a query. You need the answer. Loss is unacceptable. Processing is fast.

**Scenario 3: Commanding the Robot to Navigate Somewhere**

Question 1: How often changes? → On-demand (you request occasionally)
Question 2: Okay to lose? → No (you want confirmation it was received)
Question 3: Need guarantee? → Yes (must know task was accepted)
Question 4: How long? → Slow (5-30 seconds typically)

Answer: **ACTION**

Why? Navigation is a task. It takes time. You want progress updates. You might cancel it.

**Scenario 4: Publishing Current Time**

Question 1: How often changes? → Continuously (60+ Hz)
Question 2: Okay to lose? → Somewhat (next timestamp is coming)
Question 3: Need guarantee? → No (it's just FYI)
Question 4: How long? → Instant

Answer: **TOPIC**

Why? Time is a stream. Subscribers use it as reference. Missing one timestamp is fine.

**Scenario 5: Requesting the Robot's Current Pose**

Question 1: How often changes? → Varies (depends on motion)
Question 2: Okay to lose? → No (planning needs current pose)
Question 3: Need guarantee? → Yes
Question 4: How long? → Fast (milliseconds)

Answer: **SERVICE**

Why? Pose is a critical query. You need the answer before planning. Loss is unacceptable.

---

### The Anti-Patterns (What Breaks)

**Anti-Pattern 1: Designing Everything as Request-Response**

Reasoning: "Synchronous is safer. I'll call a service for everything."

What breaks: Your code becomes serial instead of parallel. You wait for one response, then request the next thing. Throughput drops. Real-time performance collapses.

**Anti-Pattern 2: Designing Everything as Topics**

Reasoning: "Asynchronous is faster. I'll publish everything."

What breaks: You have no way to know if your commands were received. No error handling. Navigation fails silently. Critical errors go unnoticed.

**Anti-Pattern 3: Overcomplicating with Actions**

Reasoning: "Actions are the most flexible, so I'll use them for everything."

What breaks: Simple queries become complex. You're writing cancellation logic for things that don't need it. Code bloat. Maintenance nightmare.

---

### When to Break the Rules

There are exceptions. Sometimes you deviate from the framework:

**Exception 1: High-Frequency Queries via Service**

If you need battery level at 10 Hz (unusual, but possible), you might call a service that fast. ROS2 handles it. Not ideal, but workable.

**Exception 2: Low-Frequency Topics**

If you publish a status once per minute, broadcast is fine. It's technically a topic, even if infrequent.

**Exception 3: Hybrid Approaches**

Publish continuous data on a topic, but also provide a service to get the latest value on-demand. Both channels available.

---

### Decision Checklist

Before writing your node, fill this out:

For each piece of data you need to communicate:

```
Data Name: _______________
Frequency: _____ times per second (or "on-demand")
Can lose messages?: YES / NO
Need guarantee?: YES / NO
Processing time: _____ milliseconds

Decision:
[ ] TOPIC (broadcast)
[ ] SERVICE (query)
[ ] ACTION (task)
```

Do this for every piece of communication in your system. You'll find patterns emerge.

---

### Hands-On Lab & Practical Code References

To observe all three communication primitives running concurrently in a single system:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_comms/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_comms/README.md)
- **Launch Orchestration:** `launch/all_comms.launch.py`

#### 1. Launch All Communication Primitives
```bash
cd ROS2_kits_ws
source install/setup.bash
ros2 launch learning_comms all_comms.launch.py
```

#### 2. Evaluate Communication Decisions in the Live Graph
In a second terminal, verify each interface and apply the 4-question decision checklist:

```bash
# 1. Inspect Topics (Streaming broadcast: /chatter)
ros2 topic list
ros2 topic hz /chatter

# 2. Inspect Services (Guaranteed synchronous query: /add_two_ints)
ros2 service list
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 10, b: 20}"

# 3. Inspect Actions (Long-running goal + feedback: /count_until)
ros2 action list
ros2 action send_goal --feedback /count_until example_interfaces/action/Fibonacci "{order: 5}"
```

---

### How This Connects Forward

Next: After you've learned the individual patterns (Topics in B1, Services in B2, Actions in B3), we'll come back to this framework in Article B4b with concrete trade-off analysis. You'll see what happens in edge cases and how professionals make these decisions.

---

### Learning Outcome Test

After reading this article, you should be able to:

1. **Ask** the four questions about any piece of data and predict the communication pattern
2. **Identify** the red flags when a pattern is being misused
3. **Explain** why "continuous sensor data" almost always means topic, and "critical query" almost always means service
4. **Defend** your choice: "I chose SERVICE for battery level because..." (and the reasons are sound)
5. **Predict** what would break if you chose wrong for each scenario

If you can do these, you're ready to learn the specific patterns. You'll know not just what to do, but why.

---

*Word Count: 1,800*
*Reading Time: 11 minutes*
*Prerequisites: A0, A1*
*Next: B1 (Topics) or B2 (Services), then B4b*