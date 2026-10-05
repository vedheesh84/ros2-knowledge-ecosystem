# ROS2 Learning Workspace

A comprehensive, hands-on learning environment for mastering ROS2 (Robot Operating System 2) concepts from first principles.

---

## Table of Contents

- [Overview](#overview)
- [What You Will Learn](#what-you-will-learn)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Package Overview](#package-overview)
- [Learning Path](#learning-path)
- [How to Use This Workspace](#how-to-use-this-workspace)
- [Build Instructions](#build-instructions)
- [Troubleshooting](#troubleshooting)

---

## Overview

This workspace is designed to teach ROS2 through **experience, not explanation**. Each package is a self-contained learning module that:

1. **Explains the concept** - Why does this exist? What problem does it solve?
2. **Provides working code** - Fully functional nodes you can run immediately
3. **Offers challenges** - Exercises to break and rebuild your understanding
4. **Prompts reflection** - Questions to solidify your mental model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ROS2 LEARNING ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Phase 1: Foundation                                                       │
│   ┌─────────────────┐    ┌─────────────────┐                               │
│   │  learning_core  │───▶│ learning_comms  │                               │
│   │  (Mental Model) │    │ (Communication) │                               │
│   └─────────────────┘    └─────────────────┘                               │
│            │                      │                                         │
│            ▼                      ▼                                         │
│   Phase 2: Orchestration                                                    │
│   ┌────────────────────────────────┐                                        │
│   │     learning_execution         │                                        │
│   │  (Launch & Composition)        │                                        │
│   └────────────────────────────────┘                                        │
│            │                                                                │
│            ▼                                                                │
│   Phase 3: Advanced Concepts                                                │
│   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│   │  lifecycle  │ │     tf      │ │ simulation  │ │  debugging  │          │
│   │  (States)   │ │  (Frames)   │ │  (Gazebo)   │ │   (Tools)   │          │
│   └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │
│            │             │               │               │                  │
│            └─────────────┴───────────────┴───────────────┘                  │
│                                    │                                        │
│                                    ▼                                        │
│   Phase 4: Integration                                                      │
│   ┌────────────────────────────────┐                                        │
│   │     learning_integration       │                                        │
│   │    (Complete Robot System)     │                                        │
│   └────────────────────────────────┘                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## What You Will Learn

By completing this workspace, you will be able to:

| Skill | Description |
|-------|-------------|
| **Understand the ROS2 Graph** | Know how nodes, topics, services, and actions connect |
| **Write ROS2 Nodes** | Create publishers, subscribers, services, and action servers |
| **Orchestrate Systems** | Use launch files to compose complex robot systems |
| **Manage Lifecycle** | Build deterministic, fault-tolerant robot software |
| **Work with TF2** | Transform coordinates between frames confidently |
| **Simulate Robots** | Use Gazebo with ROS2 for development and testing |
| **Debug Effectively** | Use introspection tools to diagnose problems |
| **Integrate Systems** | Combine all concepts into complete robot applications |

---

## Prerequisites

### Required Knowledge

- Basic Python programming (functions, classes, loops)
- Familiarity with Linux command line (cd, ls, mkdir)
- Understanding of basic programming concepts

### Required Software

- **Ubuntu 22.04** (Jammy Jellyfish)
- **ROS2 Humble Hawksbill** (LTS)
- **Gazebo** (for simulation package)
- **RViz2** (for visualization)

### Verify Your Installation

```bash
# Check ROS2 installation
ros2 --version

# Expected output: ros2 0.x.x (Humble)

# Check Gazebo
gazebo --version

# Check RViz2
rviz2 --version
```

---

## Quick Start

### 1. Clone and Build

```bash
# Navigate to the workspace
cd ROS2_kits_ws

# Build all packages
colcon build

# Source the workspace
source install/setup.bash
```

### 2. Run Your First Node

```bash
# Run the simplest possible ROS2 node
ros2 run learning_core hello_node

# In another terminal, see it in the graph
ros2 node list
```

### 3. Explore the Graph

```bash
# Run the graph introspector
ros2 run learning_core graph_introspector_node

# Watch topics
ros2 topic list
ros2 topic echo /graph_info
```

---

## Package Overview

| Package | Purpose | Nodes | Difficulty |
|---------|---------|-------|------------|
| [learning_core](src/ros2_learning_common/learning_core/README.md) | ROS2 mental model, workspace basics | 3 | Beginner |
| [learning_comms](src/ros2_learning_common/learning_comms/README.md) | Topics, services, and actions | 6 | Beginner |
| [learning_execution](src/ros2_learning_common/learning_execution/README.md) | Launch files and composition | 3 | Intermediate |
| [learning_lifecycle](src/ros2_learning_common/learning_lifecycle/README.md) | Lifecycle nodes | 2 | Intermediate |
| [learning_tf](src/ros2_learning_common/learning_tf/README.md) | TF2 coordinate frames | 3 | Intermediate |
| [learning_simulation](src/ros2_learning_common/learning_simulation/README.md) | Gazebo and simulation time | 2 | Intermediate |
| [learning_debugging](src/ros2_learning_common/learning_debugging/README.md) | Logging and introspection | 2 | Beginner |
| [learning_integration](src/ros2_learning_common/learning_integration/README.md) | Complete robot system | 3 | Advanced |

---

## Learning Path

See [LEARNING_PATH.md](resources/LEARNING_PATH.md) for a detailed, sequential learning guide.

**Recommended Order:**

```
1. learning_core        ──▶  Start here! Understand what ROS2 IS
        │
        ▼
2. learning_comms       ──▶  Topics, Services, Actions
        │
        ▼
3. learning_execution   ──▶  Launch files, composition
        │
        ▼
4. learning_lifecycle   ──▶  Managed nodes (optional for beginners)
        │
        ▼
5. learning_tf          ──▶  Coordinate frames
        │
        ▼
6. learning_simulation  ──▶  Gazebo integration
        │
        ▼
7. learning_debugging   ──▶  Can be done anytime after core
        │
        ▼
8. learning_integration ──▶  Capstone: everything together
```

---

## How to Use This Workspace

### For Each Package:

1. **Read the README** - Understand the concepts before running code
2. **Run the demos** - Execute the provided launch files
3. **Study the code** - Read the extensively commented source files
4. **Complete challenges** - Each package has 3 difficulty levels
5. **Reflect** - Answer the reflection prompts in each README

### Pro Tips:

- **Use multiple terminals** - You'll often need 2-4 terminals open
- **Watch topics live** - `ros2 topic echo /topic_name` is your friend
- **Visualize with rqt_graph** - `rqt_graph` shows the computation graph
- **Read error messages** - They're usually quite informative in ROS2

---

## Build Instructions

### Build All Packages

```bash
cd ROS2_kits_ws
colcon build
source install/setup.bash
```

### Build a Single Package

```bash
colcon build --packages-select learning_core
source install/setup.bash
```

### Build with Debug Info

```bash
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Debug
```

### Clean Build

```bash
rm -rf build install log
colcon build
```

---

## Troubleshooting

### Common Issues

#### "Package not found"

```bash
# Make sure you've sourced the workspace
source install/setup.bash
```

#### "No executable found"

```bash
# Rebuild the package
colcon build --packages-select <package_name>
source install/setup.bash
```

#### "Import error"

```bash
# Check that ROS2 Humble is sourced
source /opt/ros/humble/setup.bash
```

#### Node runs but nothing happens

```bash
# Check if topics are being published
ros2 topic list
ros2 topic hz /topic_name

# Check the graph
rqt_graph
```

---

## Contributing

This is a learning workspace. If you find errors or want to suggest improvements:

1. Document the issue clearly
2. Suggest a fix if possible
3. Keep the pedagogical focus in mind

---

## License

MIT License - Learn freely, share widely.

---

## See Also

- [ROS2 Official Documentation](https://docs.ros.org/en/humble/)
- [ROS2 Tutorials](https://docs.ros.org/en/humble/Tutorials.html)
- [GLOSSARY.md](resources/GLOSSARY.md) - ROS2 terminology reference
- [LEARNING_PATH.md](resources/LEARNING_PATH.md) - Detailed learning guide
- [LEARNING_MAP.md](resources/LEARNING_MAP.md) - Visual learning map
