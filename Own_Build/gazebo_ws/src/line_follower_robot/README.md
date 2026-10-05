# line_follower_robot

Line following robot simulation with dual URDF/SDF representations, detailed mesh models, and multiple launch configurations.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Robot Description](#robot-description)
- [Launch Files](#launch-files)
- [Usage](#usage)

---

## Overview

This package provides a differential drive robot designed for line following:

- **Detailed Meshes** - High-quality STL models from CAD
- **Dual Representation** - Both URDF (ROS) and SDF (Gazebo)
- **4-DOF System** - Two drive wheels + 2-joint caster assembly
- **Multiple Launch Options** - 7 launch configurations

### Robot Design

```
       ┌────────────────────────────┐
       │      Castor Assembly       │
       │     ┌─────┐                │
       │     │  ○  │◀── castor_wheel│
       │     └──┬──┘                │
       │        │                   │
       │    castor_base             │
       └────────┼───────────────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
  ┌─┴─┐    ┌────┴────┐    ┌─┴─┐
  │ L │    │  Base   │    │ R │
  │ W │    │  Link   │    │ W │
  └───┘    └─────────┘    └───┘
   Left                   Right
   Wheel                  Wheel
```

---

## Package Structure

```
line_follower_robot/
├── CMakeLists.txt
├── package.xml
├── launch/
│   ├── gazebo_xacro_rviz.launch.py  # Gazebo with XACRO
│   ├── gazebo_empty.launch.py       # Empty Gazebo world
│   ├── gazebo_sdf.launch.py         # SDF model spawning
│   ├── gazebo_spawn.launch.py       # Robot spawner module
│   ├── rviz_xacro.launch.py         # RViz with XACRO
│   ├── rviz_urdf.launch.py          # RViz with URDF
│   └── test.launch.py               # Test launch
├── urdf/
│   ├── line_follower_robot.urdf.xacro  # Xacro description
│   └── line_follower_robot.urdf        # Static URDF
├── meshes/                          # 4.3 MB total
│   ├── base_link.STL                # Chassis (1.8 MB)
│   ├── left_wheel.STL               # Left wheel (1.0 MB)
│   ├── right_wheel.STL              # Right wheel (1.0 MB)
│   ├── castor_base_link.STL         # Caster mount (239 KB)
│   └── castor_wheel.STL             # Caster wheel (287 KB)
├── models/
│   ├── line_follower_robot.sdf      # SDF model
│   └── model.config                 # Model metadata
├── config/
│   └── joint_names_line_follower_robot.yaml
└── script/
    └── wheel_publisher.py           # Joint state simulator
```

---

## Robot Description

### Physical Specifications

| Link | Mass | Mesh |
|------|------|------|
| Base | 0.128 kg | base_link.STL |
| Left Wheel | 0.0214 kg | left_wheel.STL |
| Right Wheel | 0.0214 kg | right_wheel.STL |
| Castor Base | ~0.01 kg | castor_base_link.STL |
| Castor Wheel | ~0.01 kg | castor_wheel.STL |

### Joint Configuration

| Joint | Type | Parent | Child |
|-------|------|--------|-------|
| `left_wheel_joint` | continuous | base_link | left_wheel |
| `right_wheel_joint` | continuous | base_link | right_wheel |
| `castor_joint` | continuous | base_link | castor_base |
| `castor_wheel_joint` | continuous | castor_base | castor_wheel |

### Wheel Geometry

- Wheel radius: ~0.055m
- Left wheel position: (-0.0333, 0.0758, -0.0138)
- Right wheel position: (-0.0333, -0.0758, -0.0138)
- Caster position: (0.0726, 0, -0.0025)

---

## Launch Files

### gazebo_xacro_rviz.launch.py

Comprehensive Gazebo launch with XACRO processing.

```bash
ros2 launch line_follower_robot gazebo_xacro_rviz.launch.py
```

### gazebo_sdf.launch.py

Spawn robot from SDF model definition.

```bash
ros2 launch line_follower_robot gazebo_sdf.launch.py \
  x:=1.0 y:=2.0 robot_name:=my_robot
```

**Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `world` | `empty_world` | Gazebo world file |
| `robot_name` | `line_follower` | Entity name |
| `x` | `0.0` | Spawn X position |
| `y` | `0.0` | Spawn Y position |

### rviz_xacro.launch.py

RViz visualization with joint control GUI.

```bash
ros2 launch line_follower_robot rviz_xacro.launch.py gui:=true
```

### rviz_urdf.launch.py

RViz visualization from static URDF.

```bash
ros2 launch line_follower_robot rviz_urdf.launch.py
```

### gazebo_empty.launch.py

Empty Gazebo environment (no robot spawn).

```bash
ros2 launch line_follower_robot gazebo_empty.launch.py
```

---

## Usage

### Visualize in RViz

```bash
# With joint control sliders
ros2 launch line_follower_robot rviz_xacro.launch.py gui:=true

# Static visualization
ros2 launch line_follower_robot rviz_urdf.launch.py
```

### Simulate in Gazebo

```bash
# Launch with XACRO robot
ros2 launch line_follower_robot gazebo_xacro_rviz.launch.py

# Or use SDF model
ros2 launch line_follower_robot gazebo_sdf.launch.py
```

### Test Wheel Movement

```bash
# Run wheel publisher script
ros2 run line_follower_robot wheel_publisher.py

# This publishes JointState at 50 Hz with simulated rotation
```

### Control via Teleop

```bash
# After launching Gazebo
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

---

## Scripts

### wheel_publisher.py

Simulates wheel rotation by publishing JointState messages.

```python
# Publishes at 50 Hz
# Angular velocity: 4.0 rad/s
# Topic: /joint_states
```

Useful for testing joint state visualization without hardware or controllers.

---

## URDF vs SDF

This package provides both representations:

| Format | File | Use Case |
|--------|------|----------|
| URDF/Xacro | `urdf/line_follower_robot.urdf.xacro` | ROS integration, RViz |
| SDF | `models/line_follower_robot.sdf` | Native Gazebo features |

**When to use SDF:**
- Direct Gazebo model insertion
- Advanced Gazebo-specific features
- Model database integration

**When to use URDF:**
- ROS toolchain (robot_state_publisher, MoveIt)
- RViz visualization
- Cross-simulator compatibility

---

## Dependencies

- `robot_state_publisher`
- `joint_state_publisher`, `joint_state_publisher_gui`
- `gazebo_ros`
- `xacro`
- `rviz2`
- `tf2_ros`

---

## Related Packages

- [simple_linefollower_robot](../simple_linefollower_robot/README.md) - Simplified version
- [mobilerobot](../mobilerobot/README.md) - Full navigation robot
