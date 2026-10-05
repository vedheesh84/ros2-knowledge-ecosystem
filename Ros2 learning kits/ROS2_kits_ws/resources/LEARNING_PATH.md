# ROS2 Learning Path

A structured guide to mastering ROS2 concepts in the optimal order.

---

## Table of Contents

- [Overview](#overview)
- [Before You Begin](#before-you-begin)
- [Phase 1: Foundation](#phase-1-foundation)
- [Phase 2: Orchestration](#phase-2-orchestration)
- [Phase 3: Advanced Concepts](#phase-3-advanced-concepts)
- [Phase 4: Integration](#phase-4-integration)
- [Learning Tips](#learning-tips)
- [Skill Checkpoints](#skill-checkpoints)

---

## Overview

This learning path is designed to build your ROS2 knowledge **layer by layer**. Each phase introduces concepts that depend on the previous phase.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LEARNING PROGRESSION                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: FOUNDATION                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   learning_core ───────────────▶ learning_comms                     │   │
│  │                                                                     │   │
│  │   "What is ROS2?"                "How do nodes talk?"               │   │
│  │   - Nodes & Graph                - Topics (streaming)               │   │
│  │   - Parameters                   - Services (request/response)      │   │
│  │   - Workspaces                   - Actions (long-running)           │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  PHASE 2: ORCHESTRATION                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   learning_execution                                                │   │
│  │                                                                     │   │
│  │   "How do I run multiple nodes?"                                    │   │
│  │   - Launch files                                                    │   │
│  │   - Remapping                                                       │   │
│  │   - Composition                                                     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  PHASE 3: ADVANCED CONCEPTS (can be done in any order)                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │   │
│  │   │learning_life- │  │  learning_tf  │  │learning_simul-│          │   │
│  │   │    cycle      │  │               │  │    ation      │          │   │
│  │   │               │  │               │  │               │          │   │
│  │   │ "Deterministic│  │ "Where am I?" │  │"Test without  │          │   │
│  │   │   robots"     │  │ - Frames      │  │  hardware"    │          │   │
│  │   │ - States      │  │ - Transforms  │  │ - sim_time    │          │   │
│  │   │ - Transitions │  │ - TF tree     │  │ - Gazebo      │          │   │
│  │   └───────────────┘  └───────────────┘  └───────────────┘          │   │
│  │                                                                     │   │
│  │   ┌───────────────────────────────────────────────────────┐        │   │
│  │   │              learning_debugging                        │        │   │
│  │   │                                                        │        │   │
│  │   │   "How do I find problems?"                            │        │   │
│  │   │   - Logging levels                                     │        │   │
│  │   │   - Introspection tools                                │        │   │
│  │   │   - Common debugging patterns                          │        │   │
│  │   └───────────────────────────────────────────────────────┘        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  PHASE 4: INTEGRATION                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   learning_integration                                              │   │
│  │                                                                     │   │
│  │   "Build a complete robot system"                                   │   │
│  │   - State machines                                                  │   │
│  │   - Sensor fusion                                                   │   │
│  │   - System architecture                                             │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Before You Begin

### Verify Your Environment

```bash
# Source ROS2 Humble
source /opt/ros/humble/setup.bash

# Build and source this workspace
cd /home/ved/ros2_doc/ROS2_kits_ws
colcon build
source install/setup.bash
```

### Set Up Your Workspace

Open multiple terminal windows (at least 3). In each, run:

```bash
source /opt/ros/humble/setup.bash
source /home/ved/ros2_doc/ROS2_kits_ws/install/setup.bash
```

**Pro Tip:** Add both lines to your `~/.bashrc` for automatic sourcing.

---

## Phase 1: Foundation

> **Goal:** Understand what ROS2 is and how nodes communicate

### Step 1.1: learning_core

**Objective:** Understand the ROS2 mental model

| Concept | What You'll Learn | Demo Command |
|---------|-------------------|--------------|
| The ROS2 Graph | Nodes, topics, services exist in a runtime graph | `rqt_graph` |
| Minimal Node | What `rclpy.spin()` actually does | `ros2 run learning_core hello_node` |
| Parameters | Runtime configuration without code changes | `ros2 run learning_core parameter_echo_node` |
| Introspection | See what's running | `ros2 run learning_core graph_introspector_node` |

**Complete these before moving on:**
- [ ] Run `hello_node` and see it in `ros2 node list`
- [ ] Change a parameter at runtime using `ros2 param set`
- [ ] Use `rqt_graph` to visualize the computation graph
- [ ] Complete at least 1 challenge from the README

### Step 1.2: learning_comms

**Objective:** Master the three communication patterns

| Pattern | Use Case | Demo Command |
|---------|----------|--------------|
| **Topics** | Streaming data (sensors, commands) | `ros2 launch learning_comms pubsub_demo.launch.py` |
| **Services** | One-time request/response | `ros2 launch learning_comms service_demo.launch.py` |
| **Actions** | Long-running tasks with feedback | `ros2 launch learning_comms action_demo.launch.py` |

**Complete these before moving on:**
- [ ] Run talker + listener and see messages flow
- [ ] Call a service from the command line
- [ ] Watch action feedback as it progresses
- [ ] Explain when to use each pattern (the "decision tree")

---

## Phase 2: Orchestration

> **Goal:** Learn to compose and run multi-node systems

### Step 2.1: learning_execution

**Objective:** Master launch files and composition

| Concept | What You'll Learn | Demo Command |
|---------|-------------------|--------------|
| Launch Files | Orchestrate multiple nodes | `ros2 launch learning_execution separate_processes.launch.py` |
| Remapping | Flexible topic wiring | `ros2 launch learning_execution remapped.launch.py` |
| Composition | Nodes in single process | `ros2 launch learning_execution composed.launch.py` |
| Parameters in Launch | Configure from launch | `ros2 launch learning_execution parameterized.launch.py` |

**Complete these before moving on:**
- [ ] Read and understand a launch file (Python)
- [ ] Successfully remap a topic
- [ ] Explain the difference between separate processes vs composition
- [ ] Create your own simple launch file

---

## Phase 3: Advanced Concepts

> **Goal:** Learn professional-grade robotics patterns

These packages can be done in any order after Phase 2.

### Step 3.1: learning_lifecycle

**Objective:** Build deterministic, fault-tolerant robots

| Concept | What You'll Learn |
|---------|-------------------|
| Lifecycle States | unconfigured → inactive → active → finalized |
| Transitions | on_configure, on_activate, on_deactivate, on_cleanup |
| External Management | Controlling lifecycle from another node |

**Why this matters:** Production robots can't just "crash and restart." They need graceful degradation and recovery.

### Step 3.2: learning_tf

**Objective:** Master coordinate frame transformations

| Concept | What You'll Learn |
|---------|-------------------|
| TF Tree | Parent-child frame relationships |
| Static Transforms | Fixed relationships (sensor mounting) |
| Dynamic Transforms | Moving relationships (robot motion) |
| Transform Lookups | "Where is X relative to Y?" |

**Why this matters:** Every robot has multiple coordinate frames. Without TF, you're doing matrix math by hand.

```
    world
      │
      └── base_link
            │
            ├── camera_link
            │
            └── lidar_link
```

### Step 3.3: learning_simulation

**Objective:** Use simulation effectively

| Concept | What You'll Learn |
|---------|-------------------|
| Simulation Time | The `/clock` topic and `use_sim_time` |
| Simulated Sensors | How sensors work in Gazebo |
| Simulated Actuators | Commanding motion in simulation |

**Why this matters:** You'll spend 80% of development time in simulation. Learn to use it properly.

### Step 3.4: learning_debugging

**Objective:** Find and fix problems efficiently

| Concept | What You'll Learn |
|---------|-------------------|
| Logging | DEBUG, INFO, WARN, ERROR, FATAL |
| Introspection | `ros2 topic`, `ros2 service`, `ros2 node` |
| rqt Tools | `rqt_graph`, `rqt_console`, `rqt_topic` |

**Why this matters:** Half of robotics is debugging. Build these skills early.

---

## Phase 4: Integration

> **Goal:** Build a complete robot system using all concepts

### Step 4.1: learning_integration

**Objective:** Combine everything into a working system

You will build:
- A state machine coordinator
- Sensor fusion with lifecycle management
- Action servers for complex behaviors
- Proper TF tree for all components

**Prerequisites:** Complete all Phase 1-3 packages first!

---

## Learning Tips

### General Advice

1. **Type, don't copy-paste** - The physical act of typing helps memory
2. **Break things intentionally** - The best way to understand is to see failures
3. **Draw diagrams** - Visualize the graph on paper
4. **Teach someone else** - Explaining forces understanding

### Terminal Tips

```bash
# Always have these commands ready:
ros2 topic list           # What's being published?
ros2 topic echo /topic    # What's the data?
ros2 topic hz /topic      # How fast?
ros2 node list            # What nodes are running?
rqt_graph                 # Visualize everything
```

### When You're Stuck

1. Read the error message carefully
2. Check that workspaces are sourced
3. Use `ros2 topic echo` to verify data flow
4. Check `rqt_graph` for disconnections
5. Read the node's code comments

---

## Skill Checkpoints

Use these to verify your progress:

### After Phase 1

- [ ] I can explain what a ROS2 node is
- [ ] I can create a simple publisher and subscriber
- [ ] I know when to use topics vs services vs actions
- [ ] I can set and get parameters

### After Phase 2

- [ ] I can write a Python launch file
- [ ] I can remap topics in a launch file
- [ ] I understand process vs thread composition
- [ ] I can pass parameters through launch files

### After Phase 3

- [ ] I can create and manage a lifecycle node
- [ ] I can broadcast and lookup TF transforms
- [ ] I understand simulation time vs wall time
- [ ] I can debug a misbehaving node

### After Phase 4

- [ ] I can design a multi-node robot system
- [ ] I can integrate multiple communication patterns
- [ ] I can build robust, recoverable robot software
- [ ] I can explain the ROS2 design philosophy

---

## Next Steps

After completing this workspace, you're ready to:

1. **Explore Nav2** - Navigation stack for autonomous mobile robots
2. **Learn MoveIt2** - Motion planning for robot arms
3. **Study ros2_control** - Hardware abstraction layer
4. **Build your own robot** - Apply everything you've learned

---

## Glossary

See [GLOSSARY.md](GLOSSARY.md) for definitions of all ROS2 terms.
