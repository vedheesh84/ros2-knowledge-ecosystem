# learning_tf

**TF2 Coordinate Frames and Transforms**

Learn how robots track "Where is X relative to Y?"

---

## Learning Objectives

1. Understand coordinate frames and the TF tree
2. Broadcast static transforms (fixed relationships)
3. Broadcast dynamic transforms (moving frames)
4. Look up transforms between any frames

---

## The TF Tree

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TF TREE CONCEPT                                   │
│                                                                             │
│   Every frame has ONE parent, can have MANY children                        │
│                                                                             │
│                            world                                            │
│                              │                                              │
│                          base_link                                          │
│                         /    │    \                                         │
│                        /     │     \                                        │
│                  camera  lidar  rotating_sensor                             │
│                                    (dynamic!)                               │
│                                                                             │
│   You can ask for transform between ANY two frames!                         │
│   TF2 chains them automatically.                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Usage

```bash
# Build
colcon build --packages-select learning_tf
source install/setup.bash

# Run all nodes
ros2 launch learning_tf full_tf_demo.launch.py

# View the TF tree
ros2 run tf2_tools view_frames

# Echo a transform
ros2 run tf2_ros tf2_echo world camera_link

# Visualize in RViz
rviz2 -d config/tf_rviz.rviz
```

---

## Nodes

| Node | Purpose |
|------|---------|
| `static_tf_node` | Broadcasts fixed transforms (world→base, base→sensors) |
| `dynamic_tf_node` | Broadcasts rotating sensor frame |
| `tf_listener_node` | Looks up transforms and logs them |

---

## Key Concepts

**Static vs Dynamic:**
- **Static:** Published once, never changes (sensor mounts)
- **Dynamic:** Published continuously at 10+ Hz (robot motion)

**Quaternions:** Rotations are represented as quaternions (x, y, z, w).
For Z-axis rotation: `z = sin(angle/2), w = cos(angle/2)`

---

## Further Reading

- [TF2 Tutorial](https://docs.ros.org/en/humble/Tutorials/Intermediate/Tf2/Tf2-Main.html)
