# learning_integration

**Capstone: Complete Robot System Integration**

Demonstrates everything you've learned working together!

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INTEGRATED ROBOT SYSTEM                              │
│                                                                             │
│   ┌──────────────────┐        ┌────────────────────┐                       │
│   │  Sensor Fusion   │───────▶│    Robot Brain     │                       │
│   │  (Publisher)     │ topic  │   (State Machine)  │                       │
│   └──────────────────┘        └────────────────────┘                       │
│                                        │                                    │
│                                        │ service                            │
│                                        ▼                                    │
│                               ┌────────────────────┐                       │
│                               │ Command Executor   │                       │
│                               │    (Service)       │                       │
│                               └────────────────────┘                       │
│                                                                             │
│   Data Flow: Sensors → Brain → Actions                                     │
│   Patterns: Topics (streaming) + Services (commands)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Usage

```bash
# Build
colcon build --packages-select learning_integration
source install/setup.bash

# Run the complete system
ros2 launch learning_integration full_system.launch.py

# Watch the state machine
ros2 topic echo /robot_status

# Watch sensor data
ros2 topic echo /sensor_data
```

---

## Nodes

| Node | Role | Pattern |
|------|------|---------|
| `sensor_fusion_node` | Simulates sensors, publishes fused data | Publisher |
| `robot_brain_node` | State machine coordinator | Sub + Service Client |
| `command_executor_node` | Executes robot commands | Service Server |

---

## Congratulations!

You've completed the ROS2 Learning Workspace!

You now understand:
- Nodes and the computation graph
- Topics, services, and actions
- Launch files and composition
- Lifecycle nodes
- TF2 coordinate frames
- Simulation concepts
- Debugging tools
- System integration

**Next steps:**
- Explore Nav2 for navigation
- Learn MoveIt2 for manipulation
- Build your own robot!
