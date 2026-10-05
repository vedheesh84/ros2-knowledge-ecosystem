## B1: TOPICS: CONTINUOUS DATA IN ROBOTICS

*Purpose: Teach the first communication pattern students experience. Make topics feel inevitable, not magical.*

### Must Answer
- What are topics and why are they one-way?
- When do you lose messages and why is that okay?
- Why don't topics have guaranteed delivery?
- How do you publish and subscribe to a topic?

### Key Insight
Topics are how robots broadcast continuous data streams without caring who listens. Fire and forget. The publisher doesn't wait. Perfect for sensor data.

---

### The Mental Model: Broadcast Radio

A topic is like a broadcast radio station:

- **Station publishes** continuously: "Current weather: 25°C, humidity 60%"
- **Listeners tune in** whenever they want
- **Listeners miss broadcasts** they weren't tuned in for (that's okay)
- **Station doesn't care** if anyone is listening (keeps broadcasting anyway)
- **Multiple listeners** can tune in (each independent)

The publisher doesn't know or care who's listening. Listeners don't ask permission. It's one-way.

---

### Publishers and Subscribers

A **publisher** sends messages to a topic:

```
Camera node publishes images to /camera/image
```

A **subscriber** receives messages from a topic:

```
Obstacle detector subscribes to /camera/image
Receives images as they arrive
Processes each image
```

The camera node doesn't know the obstacle detector exists. The detector didn't ask permission. They're decoupled.

---

### Real Example: Multi-Sensor Robot

A robot publishes sensor data continuously:

```
Camera node → publishes to /camera/image (30 Hz)
Lidar node → publishes to /scan (10 Hz)
IMU node → publishes to /imu (100 Hz)

Logger node subscribes to /camera/image, /scan, /imu
Obstacle detector subscribes to /camera/image
Navigator subscribes to /scan
Balance controller subscribes to /imu
```

Each publisher broadcasts. Each subscriber picks what it needs. No coordination required.

---

### Why Topics, Not Function Calls?

Why not just call a function?

```
// BAD: Function call
while True:
  image = camera.get_image()  // Blocks until image ready
  detect_obstacles(image)      // Process
  plan_path(...)               // Process
```

Problem: Sequential. Each step waits for the previous. If camera is slow, planner waits. Bottleneck.

With topics:

```
// GOOD: Topic-based
Camera publishes at 30 Hz (independently)
Detector processes as images arrive (independently)
Planner processes as data arrives (independently)
```

Parallel. All happening simultaneously. No blocking. Resilient.

---

### Message Loss: Why It's Okay Sometimes

Topics use **best-effort delivery**. Messages may be lost.

When the camera publishes image #50:
- Detector receives it ✓
- Logger receives it ✓
- Viewer misses it (was processing image #49) ✗

The viewer misses one frame. Is that bad?

For camera at 30 FPS, another image arrives in 33ms. One lost frame is negligible.

**For streaming data: message loss is acceptable.**

For critical queries (battery level), you'd use a service instead.

---

### Common Questions

**Q: What if no one is subscribed?**

Publisher keeps publishing. Messages are discarded (no subscribers to receive them). Publisher doesn't care.

**Q: What if there are 100 subscribers?**

Publisher publishes once. All 100 receive it (in parallel). Efficient.

**Q: What if subscriber is slow?**

Publisher doesn't wait. It publishes again with new data. If subscriber is too slow, it misses messages.

**Q: How do I know if my message arrived?**

You don't. Topics are fire-and-forget. If you need confirmation, use a service or action.

---

### Hands-On Lab & Practical Code References

To observe asynchronous publisher-subscriber broadcast and measure topic metrics:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_comms/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_comms/README.md)
- **Source Code to Inspect:**
  - `learning_comms/talker_node.py` — Timer-based continuous topic publisher
  - `learning_comms/listener_node.py` — Asynchronous subscription callback
- **Launch Orchestration:** `launch/pubsub_demo.launch.py`

#### 1. Launch the Pub/Sub Demo
```bash
cd ROS2_kits_ws
source install/setup.bash
ros2 launch learning_comms pubsub_demo.launch.py
```

#### 2. Introspect Topic Traffic & Frequency
In a second terminal:

```bash
# 1. Echo continuous streaming data
ros2 topic echo /chatter

# 2. Measure publishing frequency (rate)
ros2 topic hz /chatter

# 3. Measure bandwidth consumption
ros2 topic bw /chatter

# 4. Check publisher and subscriber endpoint details
ros2 topic info /chatter -v
```

---

### How This Connects Forward

Next: In Article B2 ("Services: When Robotics Needs Certainty"), you'll learn when topics are NOT appropriate. When do you need guaranteed delivery? That's services.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Explain** topics as broadcast (not function calls)
2. **Identify** when message loss is acceptable (streaming) vs. unacceptable (queries)
3. **Predict** what happens if a subscriber is slow or disconnected
4. **Describe** the publisher-subscriber decoupling (why they don't know each other)
5. **Reason** about topic frequency (30 Hz camera implies what about message loss tolerance?)

---

*Word Count: 1,400*
*Reading Time: 9 minutes*
*Prerequisites: A0, A1, A2, B4a*
*Next: B2 or B4a (decision heuristics)*