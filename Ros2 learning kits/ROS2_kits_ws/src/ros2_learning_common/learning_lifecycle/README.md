# learning_lifecycle

**Lifecycle Nodes for Deterministic Robots**

Learn managed state transitions for predictable robot startup and shutdown.

---

## Learning Objectives

1. Understand lifecycle states (unconfigured → inactive → active → finalized)
2. Implement transition callbacks
3. Control lifecycle nodes externally
4. Build fault-tolerant robot systems

---

## Lifecycle States

```
┌─────────────────────────────────────────────────────────────────────────────┐
│   UNCONFIGURED ──configure──▶ INACTIVE ──activate──▶ ACTIVE                │
│        ▲                          ▲                      │                  │
│        │                          │                      │                  │
│     cleanup                  deactivate              deactivate             │
│        │                          │                      │                  │
│        └──────────────────────────┴──────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Usage

```bash
# Build
colcon build --packages-select learning_lifecycle
source install/setup.bash

# Run demo
ros2 launch learning_lifecycle lifecycle_demo.launch.py

# Or manually control
ros2 run learning_lifecycle lifecycle_sensor_node &
ros2 lifecycle set /lifecycle_sensor configure
ros2 lifecycle set /lifecycle_sensor activate
ros2 topic echo /sensor_data
ros2 lifecycle set /lifecycle_sensor deactivate
```

---

## Why Lifecycle Nodes?

**Problem:** Regular nodes start immediately. What if:
- Hardware isn't ready?
- Configuration is missing?
- Dependencies aren't available?

**Solution:** Lifecycle nodes have explicit states:
- **Configure:** Set up resources, validate config
- **Activate:** Start the main function
- **Deactivate:** Pause without releasing resources
- **Cleanup:** Release all resources

This enables **deterministic startup sequences** critical for real robots.

---

## Nodes

| Node | Purpose |
|------|---------|
| `lifecycle_sensor_node` | Demonstrates lifecycle callbacks |
| `lifecycle_controller_node` | Controls sensor's lifecycle externally |

---

## Further Reading

- [ROS2 Managed Nodes](https://design.ros2.org/articles/node_lifecycle.html)
