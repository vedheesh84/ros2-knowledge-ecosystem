## B3: ACTIONS: LONG-RUNNING DECISIONS AND FEEDBACK

*Purpose: Introduce goal-feedback pattern for complex, long-running tasks. Teach cancellation and progress tracking.*

### Must Answer
- How are actions different from services?
- Why do you need feedback during a task?
- How can you cancel an action?
- When do you use actions instead of services?

### Key Insight
Actions are how robots execute complex tasks asynchronously. You send a goal. The server works on it. Sends progress updates. You can monitor or cancel. Perfect for navigation, manipulation, long-running operations.

---

### The Mental Model: Hiring a Contractor

Hiring someone to build a deck:

- **You request**: "Please build a deck (here are specs)"
- **Contractor accepts**: "I'll do it"
- **Work begins**: You don't wait on-site. You go about your life.
- **Progress updates**: "Foundation done", "50% complete", "Finished"
- **Feedback**: You can ask how it's going
- **Cancellation**: "Actually, never mind, stop"

Asynchronous. You can do other things. Feedback available. Can cancel.

---

### Goal-Feedback Pattern

An **action client** sends a goal:

```
Navigator client: "Navigate to room 5"
Sends the request, doesn't wait for completion
```

An **action server** handles the goal:

```
Navigation server receives: "Navigate to room 5"
Accepts: "Okay, I'll do it"
Starts working: sends feedback every second
  "5% done", "10% done", ..., "100% done"
Finishes: sends result
```

The client doesn't block. It can ask for progress. It can cancel anytime.

---

### Real Example: Navigation Task

Robot is navigating to a distant waypoint (takes 30 seconds):

**With a service (wrong):**
```
Planner calls navigate_to service
Planner blocks for 30 seconds
If network drops during navigation, entire operation fails
If obstacle appears, planner can't react
```

**With an action (correct):**
```
Planner sends navigate_to action goal
Planner doesn't block
Navigation server works: publishes progress feedback
Planner can monitor: "20% done, 80% to go"
Obstacle appears? Planner can cancel goal immediately
Navigation server stops, responds "Cancelled"
```

Asynchronous. Responsive. Robust.

---

### The Action Lifecycle

1. **Goal Sent**: Client sends goal to server
2. **Goal Accepted**: Server says "I'll do this" or "Rejected"
3. **Execution**: Server works on the goal
4. **Feedback**: Server sends periodic progress updates
5. **Result**: Server finishes, sends final result (success/failure/cancelled)

---

### Cancellation: A First-Class Concept

Actions support **cancellation**, unlike services.

```
Client sends goal: "Pick up object"
Server starts: reaching toward object
Client: "Cancel!"
Server: stops reaching, responds "Cancelled"
```

Services don't have this. If you call a service, you must wait (or timeout).

**Why cancellation matters:**
- User says "Never mind, go to different room" → cancel navigation
- Obstacle appears → cancel motion
- Battery drops dangerously low → cancel long task

Cancellation is essential for responsive robots.

---

### Feedback: Progress Tracking

Actions publish **feedback** periodically:

```
Client sends goal: "Process 1000 images"
Server starts processing
Feedback 1: "Processed 100 images"
Feedback 2: "Processed 250 images"
...
Feedback 1000: "Processed 1000 images, task complete"
```

The client can check progress without blocking. Useful for:
- User interfaces ("Progress: 50%")
- Preempting slow tasks ("This is taking too long, cancel it")
- Debugging ("Where did the task get stuck?")

---

### When to Use Each Pattern

**Use Topic** if:
- Data streams continuously
- Subscribers don't care about occasional losses
- No coordination needed (fire-and-forget)

**Use Service** if:
- One-time query
- Need guaranteed answer
- Task is fast (milliseconds)
- Okay to block temporarily

**Use Action** if:
- Task is long-running (seconds or more)
- Need feedback during execution
- Might need to cancel mid-way
- Client needs to know completion status

---

### Common Misconceptions

**Myth: Actions are always slower**

Truth: Actions have more overhead (yes) but are the RIGHT tool for long tasks. Using a service for a 30-second task is worse than using an action.

**Myth: Use actions for safety**

Truth: Actions provide feedback and cancellation (useful for safety). But don't confuse actions with true safety measures (which need lifecycle and state machines, covered later).

---

### Hands-On Lab & Practical Code References

To observe the complete action lifecycle (goal acceptance, incremental feedback streams, cancellation, and final result):

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_comms/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_comms/README.md)
- **Source Code to Inspect:**
  - `learning_comms/action_server_node.py` — Handles goal execution thread, publishes feedback loop, and processes cancellation requests
  - `learning_comms/action_client_node.py` — Sends goal and registers feedback callback
- **Launch Orchestration:** `launch/action_demo.launch.py`

#### 1. Launch the Action Demo
```bash
cd ROS2_kits_ws
source install/setup.bash
ros2 launch learning_comms action_demo.launch.py
```

#### 2. Send Action Goals & Monitor Feedback via CLI
In a second terminal:

```bash
# 1. Discover all active action servers
ros2 action list

# 2. Inspect the action server and client endpoints
ros2 action info /count_to_number

# 3. Send a goal with real-time feedback streaming
ros2 action send_goal --feedback /count_to_number learning_comms/action/CountToNumber "{target_number: 5, delay_between_counts: 0.5}"
```

---

### How This Connects Forward

Next: In Article B3b ("Coordinating Multiple Actions in a System"), you'll see how to orchestrate multiple actions together. Individual actions are powerful. Coordinated actions create complex robot behaviors.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Explain** why "navigate to waypoint" must be an action (not a service)
2. **Design** the feedback loop for a task (what progress updates matter?)
3. **Predict** what happens if you cancel an action mid-execution
4. **Identify** when an action is overkill (use service instead)
5. **Reason** about task failures: "If the action times out, server might still be working..."

---

*Word Count: 1,450*
*Reading Time: 9 minutes*
*Prerequisites: A0, A1, A2, B1, B2, B4a*
*Next: B3b or B4b*