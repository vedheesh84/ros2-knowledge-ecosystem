# simple_robot_car

Basic 4-wheel robot car platform with SolidWorks-generated URDF and high-precision CAD geometry.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Robot Description](#robot-description)
- [Launch Files](#launch-files)
- [Usage](#usage)

---

## Overview

This package provides a simple 4-wheel car platform:

- **CAD-Generated** - Exported from SolidWorks with precise geometry
- **Skid Steering** - All 4 wheels independently controlled
- **Minimal Dependencies** - No sensors or complex systems
- **Prototype Platform** - Base for adding custom features

### Design Philosophy

```
     Front
  ┌─────────────┐
  │ FL       FR │
  │  ○       ○  │
  │             │
  │    BASE     │
  │             │
  │  ○       ○  │
  │ BL       BR │
  └─────────────┘
     Back

FL = Front Left    FR = Front Right
BL = Back Left     BR = Back Right
```

---

## Package Structure

```
simple_robot_car/
├── CMakeLists.txt
├── package.xml
├── launch/
│   ├── display.launch.py      # Gazebo + RViz
│   └── robot_rviz.launch.py   # RViz only
├── urdf/
│   └── simple_robot_car.urdf  # CAD-generated URDF
├── meshes/
│   ├── base_link.STL          # Chassis (11 KB)
│   ├── FR_wheel_link.STL      # Front right (63 KB)
│   ├── FL_wheel_link.STL      # Front left (63 KB)
│   ├── BR_wheel_link.STL      # Back right (63 KB)
│   └── BL_wheel_link.STL      # Back left (63 KB)
└── config/
    └── joint_names_simple_robot_car.yaml
```

---

## Robot Description

### Physical Specifications

This robot was designed in SolidWorks and exported to URDF format. All inertia values are calculated from the CAD model with high precision.

| Link | Mass | Notes |
|------|------|-------|
| Base | 0.02955 kg | Main chassis |
| FR Wheel | 0.00163 kg | Front right |
| FL Wheel | 0.00163 kg | Front left |
| BR Wheel | 0.00163 kg | Back right |
| BL Wheel | 0.00163 kg | Back left |
| **Total** | ~0.036 kg | Small-scale prototype |

### Joint Configuration

| Joint | Type | Position (xyz) | Axis |
|-------|------|----------------|------|
| `FR_wheel_joint` | continuous | (0.015, 0.03, 0) | (0, 1, 0) |
| `FL_wheel_joint` | continuous | (0.023, -0.024, -0.013) | (0, 1, 0) |
| `BR_wheel_joint` | continuous | (-0.023, 0.024, -0.013) | (0, 1, 0) |
| `BL_wheel_joint` | continuous | (-0.023, -0.024, -0.013) | (0, 1, 0) |

### Visual Properties

- Color: Light blue (0.792, 0.820, 0.933)
- All geometry from STL mesh files
- High-precision inertia tensors from CAD

---

## Launch Files

### display.launch.py

Comprehensive Gazebo and RViz display.

```bash
ros2 launch simple_robot_car display.launch.py
```

**Nodes:**
- `robot_state_publisher` - URDF to TF
- `rviz2` - 3D visualization
- Gazebo server/client
- Entity spawner

### robot_rviz.launch.py

RViz-only visualization (no Gazebo).

```bash
ros2 launch simple_robot_car robot_rviz.launch.py
```

Useful for examining the URDF without simulation overhead.

---

## Usage

### Visualize Robot

```bash
# Full simulation with Gazebo
ros2 launch simple_robot_car display.launch.py

# RViz only (faster startup)
ros2 launch simple_robot_car robot_rviz.launch.py
```

### Control Robot

```bash
# After launching Gazebo
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Note: Requires skid-steer controller plugin
# Add to URDF for full control
```

### Inspect URDF

```bash
# Validate URDF
check_urdf src/simple_robot_car/urdf/simple_robot_car.urdf

# View TF tree
ros2 run tf2_tools view_frames
```

---

## Extending This Robot

### Add Differential Drive Controller

Add to your URDF:

```xml
<gazebo>
  <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
    <left_joint>FL_wheel_joint</left_joint>
    <right_joint>FR_wheel_joint</right_joint>
    <wheel_separation>0.048</wheel_separation>
    <wheel_diameter>0.04</wheel_diameter>
    <command_topic>cmd_vel</command_topic>
    <odometry_topic>odom</odometry_topic>
  </plugin>
</gazebo>
```

### Add Skid Steer Controller

For 4-wheel drive control:

```xml
<gazebo>
  <plugin name="skid_steer" filename="libgazebo_ros_planar_move.so">
    <command_topic>cmd_vel</command_topic>
    <odometry_topic>odom</odometry_topic>
    <odometry_frame>odom</odometry_frame>
    <robot_base_frame>base_link</robot_base_frame>
  </plugin>
</gazebo>
```

### Add a Sensor

```xml
<!-- Add camera -->
<link name="camera_link">
  <visual>
    <geometry>
      <box size="0.01 0.02 0.02"/>
    </geometry>
  </visual>
</link>

<joint name="camera_joint" type="fixed">
  <parent link="base_link"/>
  <child link="camera_link"/>
  <origin xyz="0.03 0 0.01"/>
</joint>
```

---

## SolidWorks Export Notes

This URDF was generated using SolidWorks URDF exporter:

1. **Precision** - All inertia values use scientific notation
2. **Meshes** - Exported as STL in meters
3. **Origins** - Relative to assembly origin
4. **Materials** - Generic visual properties

To modify:
1. Edit original SolidWorks assembly
2. Re-export URDF
3. Or manually edit URDF values

---

## Dependencies

- `robot_state_publisher`
- `joint_state_publisher`, `joint_state_publisher_gui`
- `gazebo_ros`
- `rviz2`

---

## Related Packages

- [mobilerobot](../mobilerobot/README.md) - Full navigation robot
- [line_follower_robot](../line_follower_robot/README.md) - Line following
- [simple_linefollower_robot](../simple_linefollower_robot/README.md) - Simple diff drive
