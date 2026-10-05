# learning_simulation

**Simulation Time and Gazebo Concepts**

Learn how simulation time works and why it matters.

---

## Key Concept: use_sim_time

```
WALL TIME:        1 second = 1 real second (always)
SIMULATION TIME:  1 second = however fast Gazebo runs

If Gazebo runs at 0.5x speed, sim time runs at 0.5x
Your robot code still works correctly!
```

---

## Usage

```bash
# Build
colcon build --packages-select learning_simulation
source install/setup.bash

# Run with wall time (default)
ros2 run learning_simulation sim_time_node

# Run with simulation time
ros2 run learning_simulation sim_time_node --ros-args -p use_sim_time:=true

# Test fake actuator
ros2 run learning_simulation fake_actuator_node &
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.5}}"
ros2 topic echo /odom
```

---

## Nodes

| Node | Purpose |
|------|---------|
| `sim_time_node` | Demonstrates simulation vs wall time |
| `fake_actuator_node` | Simulates differential drive (cmd_vel → odom) |
