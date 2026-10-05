# learning_debugging

**Debugging and Introspection**

Learn to find and fix problems in ROS2 systems.

---

## Debugging Commands

```bash
# See what's running
ros2 node list
ros2 topic list
ros2 service list

# Inspect topics
ros2 topic echo /topic_name
ros2 topic hz /topic_name
ros2 topic info /topic_name

# Visualize
rqt_graph
rqt_console
```

---

## Usage

```bash
# Run noisy node (logging demo)
ros2 run learning_debugging noisy_node

# With debug level
ros2 run learning_debugging noisy_node --ros-args --log-level debug

# Run faulty node (find the bugs!)
ros2 run learning_debugging faulty_node
```

---

## Challenge: Fix the Faulty Node

The faulty_node has 6 intentional bugs. Can you find them?

1. Run: `ros2 run learning_debugging faulty_node`
2. Check: `ros2 topic list` - is the topic name correct?
3. Check: `ros2 topic echo /data_outptu` - what's wrong with the data?
4. Try: `ros2 topic pub /data_input std_msgs/String "data: 'test'"`

**Bugs to find:**
- [ ] Typo in topic name
- [ ] Counter never increments
- [ ] Callback logs at debug level
- [ ] Crash on certain input
