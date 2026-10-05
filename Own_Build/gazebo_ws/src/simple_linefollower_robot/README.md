# simple_linefollower_robot

Simplified line follower robot with parametric URDF design, geometric primitives, and educational focus.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Robot Description](#robot-description)
- [Launch Files](#launch-files)
- [Usage](#usage)
- [Learning Notes](#learning-notes)

---

## Overview

This is a simplified version of the line follower robot designed for:

- **Learning URDF** - Clear, readable Xacro with comments
- **Parametric Design** - Dimensions defined as variables
- **Lightweight** - Small mesh files (164 KB total)
- **Easy to Modify** - Simple geometry for experimentation

### Comparison to line_follower_robot

| Feature | simple_linefollower | line_follower_robot |
|---------|---------------------|---------------------|
| Mesh size | 164 KB | 4.3 MB |
| Complexity | Low | Medium |
| Joints | 3 | 4 |
| Caster type | Sphere | 2-joint assembly |
| Inertia | Calculated | From CAD |

---

## Package Structure

```
simple_linefollower_robot/
├── CMakeLists.txt
├── package.xml
├── launch/
│   ├── linefollowerGazebo.launch.py   # Gazebo simulation
│   ├── gazebo_empty.launch.py         # Empty world
│   ├── empty_world.launch.py          # Alternative empty
│   ├── line_robot_rviz.launch.py      # RViz visualization
│   ├── spawn_line_robot.launch.py     # Spawn module
│   └── test_gazebo.launch.py          # Full test launch
├── urdf/
│   ├── line_follower_simple_robot.urdf.xacro
│   └── line_follower_simple_model.csv   # Parameter data
├── meshes/
│   ├── base_link.STL      # Chassis (24 KB)
│   ├── LW_link.STL        # Left wheel (11 KB)
│   ├── RW_link.STL        # Right wheel (11 KB)
│   └── sphear_link.STL    # Caster sphere (115 KB)
└── config/
    └── joint_names_line_follower_simple_model.yaml
```

---

## Robot Description

### Parametric Design

The URDF uses Xacro properties for easy modification:

```xml
<!-- Material Properties -->
<xacro:property name="aluminium_density" value="2700"/>  <!-- kg/m³ -->

<!-- Geometry -->
<xacro:property name="sphear_radius" value="0.06"/>      <!-- meters -->
<xacro:property name="wheel_radius" value="0.04"/>       <!-- meters -->
<xacro:property name="wheel_length" value="0.03"/>       <!-- meters -->
<xacro:property name="box_length" value="0.30"/>         <!-- meters -->
<xacro:property name="box_width" value="0.20"/>          <!-- meters -->
<xacro:property name="box_height" value="0.10"/>         <!-- meters -->
```

### Physical Specifications

| Link | Shape | Dimensions | Calculated Mass |
|------|-------|------------|-----------------|
| Base | Box | 0.30 × 0.20 × 0.10 m | ~1.62 kg |
| Left Wheel | Cylinder | ⌀0.08 × 0.03 m | ~0.015 kg |
| Right Wheel | Cylinder | ⌀0.08 × 0.03 m | ~0.015 kg |
| Sphere (caster) | Sphere | ⌀0.12 m | ~0.92 kg |

### Joint Configuration

| Joint | Type | Position | Axis |
|-------|------|----------|------|
| `LW_joint` | continuous | (-0.13, 0.13, -0.08) | (0, 0, -1) |
| `RW_joint` | continuous | (-0.13, -0.13, -0.08) | (0, 0, 1) |
| `sphear_joint` | continuous | (0.1, 0, 0.1) | (0.577, 0.577, 0.577) |

### Inertia Calculations

The URDF includes explicit inertia tensor calculations:

```xml
<!-- Box Inertia -->
<ixx> = (1/12) * mass * (width² + height²) </ixx>
<iyy> = (1/12) * mass * (length² + height²) </iyy>
<izz> = (1/12) * mass * (length² + width²) </izz>

<!-- Cylinder Inertia (wheel) -->
<ixx> = (1/12) * mass * (3*r² + h²) </ixx>
<iyy> = (1/12) * mass * (3*r² + h²) </iyy>
<izz> = (1/2) * mass * r² </izz>

<!-- Sphere Inertia -->
<ixx> = (2/5) * mass * r² </ixx>
<iyy> = (2/5) * mass * r² </iyy>
<izz> = (2/5) * mass * r² </izz>
```

---

## Launch Files

### linefollowerGazebo.launch.py

Primary Gazebo simulation launch.

```bash
ros2 launch simple_linefollower_robot linefollowerGazebo.launch.py
```

**Nodes:**
- Xacro processing
- Gazebo server/client
- Robot spawning (entity: "simple_linefollower_robot")

### line_robot_rviz.launch.py

RViz visualization with optional joint GUI.

```bash
ros2 launch simple_linefollower_robot line_robot_rviz.launch.py gui:=true
```

### spawn_line_robot.launch.py

Modular spawn launch for integration.

```bash
ros2 launch simple_linefollower_robot spawn_line_robot.launch.py x:=1.0 y:=2.0
```

### test_gazebo.launch.py

Full test with Gazebo + robot_state_publisher.

```bash
ros2 launch simple_linefollower_robot test_gazebo.launch.py
```

---

## Usage

### Basic Visualization

```bash
# RViz with joint sliders
ros2 launch simple_linefollower_robot line_robot_rviz.launch.py gui:=true

# Move sliders to see wheels rotate
```

### Gazebo Simulation

```bash
# Launch simulation
ros2 launch simple_linefollower_robot linefollowerGazebo.launch.py

# Control with keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Modify Robot Parameters

1. Edit `line_follower_simple_robot.urdf.xacro`
2. Change property values (e.g., `wheel_radius`)
3. Rebuild or use `--symlink-install`
4. Relaunch to see changes

---

## Learning Notes

### Why This Design?

**Simple Caster (Sphere):**
- Single link vs 2-joint assembly
- Easier to understand kinematically
- Passive stabilization

**Parametric Properties:**
- All dimensions in one place
- Easy to experiment with sizes
- Teaches URDF/Xacro best practices

**Calculated Inertia:**
- Shows the math explicitly
- Teaches proper physics setup
- Avoids CAD dependency

### Exercises

1. **Change Wheel Size**
   - Modify `wheel_radius` property
   - Observe effect on robot height

2. **Add a Sensor**
   - Create a camera link
   - Attach with fixed joint
   - Add Gazebo sensor plugin

3. **Change Material**
   - Modify `aluminium_density`
   - See how mass changes

---

## Dependencies

- `robot_state_publisher`
- `joint_state_publisher`, `joint_state_publisher_gui`
- `gazebo_ros`
- `xacro`
- `rviz2`

---

## Related Packages

- [line_follower_robot](../line_follower_robot/README.md) - More detailed version
- [simple_robot_car](../simple_robot_car/README.md) - 4-wheel platform
