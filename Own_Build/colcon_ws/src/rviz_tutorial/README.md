# rviz_tutorial

RViz visualization and URDF tutorial package providing robot description examples, launch files, and visualization configurations.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [URDF Models](#urdf-models)
- [Launch Files](#launch-files)
- [RViz Configurations](#rviz-configurations)
- [Usage](#usage)

---

## Overview

This package teaches robot visualization fundamentals:

- **URDF/Xacro** - Robot description format
- **RViz2** - 3D visualization tool
- **TF2** - Transform tree management
- **Robot State Publisher** - URDF to TF conversion

### Learning Objectives

1. Understand URDF structure (links, joints, visuals)
2. Create modular robot descriptions with Xacro
3. Visualize robots and sensor data in RViz
4. Configure RViz displays for different use cases

---

## Package Structure

```
rviz_tutorial/
├── launch/
│   ├── urdf_rviz.launch.py          # Basic URDF visualization
│   ├── demo.launch.py               # Full demo with joint GUI
│   ├── rviz_SimpleCar.launch.py     # Simple car visualization
│   ├── simple_car_spawn_full.launch.py
│   ├── Q_rviz_launch.py             # RViz-only launch
│   ├── Q_slam_launch.py             # SLAM visualization
│   ├── Q_localization_launch.py     # Localization viz
│   └── Q_navigation_launch.py       # Navigation viz
├── urdf/
│   ├── robot.urdf.xacro             # Main robot (composite)
│   ├── simple_robot_car.xacro       # Base platform
│   ├── lidar.xacro                  # LiDAR sensor
│   ├── camera.xacro                 # Camera sensor
│   ├── IMU_link.xacro               # IMU sensor
│   ├── myfirst.urdf                 # Simple single-link
│   └── full_demo.urdf               # Complete demo robot
├── config/
│   ├── default.rviz                 # Default RViz config
│   ├── camera.rviz                  # Camera view config
│   ├── map.rviz                     # Map visualization
│   └── tb3_cartographer.rviz        # Cartographer SLAM
└── CMakeLists.txt
```

---

## URDF Models

### robot.urdf.xacro (Main Robot)

Composite robot description including all components:

```xml
<xacro:include filename="simple_robot_car.xacro"/>
<xacro:include filename="lidar.xacro"/>
<xacro:include filename="camera.xacro"/>
<!-- <xacro:include filename="IMU_link.xacro"/> -->
```

### simple_robot_car.xacro (Base Platform)

Two-wheeled differential drive robot:

| Component | Dimensions |
|-----------|------------|
| Body | 0.30m × 0.20m × 0.10m |
| Wheel radius | 0.0425m |
| Wheel width | 0.03m |
| Wheel separation | 0.22m |
| Mass | 3.0 kg |

**Links:**
- `base_link` - Main chassis
- `left_wheel_link` - Left wheel (continuous joint)
- `right_wheel_link` - Right wheel (continuous joint)

### lidar.xacro (Laser Scanner)

LiDAR sensor attachment:
- Geometry: Cylinder (0.04m radius, 0.03m height)
- Position: Fixed at (0.0, 0.0, 0.15) from base_link
- Frame: `laser_frame`

### camera.xacro (Camera Sensor)

Camera sensor definition for visual perception.

### myfirst.urdf (Simple Example)

Minimal URDF with single link:
- Base link: Cylinder (0.6m height, 0.2m radius)
- Good starting point for URDF learning

---

## Launch Files

### demo.launch.py

Full demonstration with interactive joint control.

```bash
ros2 launch rviz_tutorial demo.launch.py
```

**Nodes:**
- `joint_state_publisher_gui` - Interactive slider control
- `robot_state_publisher` - URDF to TF conversion
- `rviz2` - 3D visualization

### urdf_rviz.launch.py

Basic URDF visualization without joint GUI.

```bash
ros2 launch rviz_tutorial urdf_rviz.launch.py
```

### Q_slam_launch.py

SLAM visualization with SLAM Toolbox integration.

```bash
ros2 launch rviz_tutorial Q_slam_launch.py
```

### Q_navigation_launch.py

Navigation2 stack visualization.

```bash
ros2 launch rviz_tutorial Q_navigation_launch.py
```

---

## RViz Configurations

### default.rviz

Standard robot visualization setup:
- Robot Model display
- TF display
- Grid

### camera.rviz

Camera-focused visualization:
- Image display
- Camera info
- Point cloud (if available)

### map.rviz

Map and navigation visualization:
- Map display
- Costmap layers
- Path display

### tb3_cartographer.rviz

Cartographer SLAM visualization:
- Submaps display
- Trajectory
- Constraints

---

## Usage

### Visualize a Robot

```bash
# Launch with joint GUI for interactive control
ros2 launch rviz_tutorial demo.launch.py

# Move sliders in joint_state_publisher_gui to animate robot
```

### View TF Tree

```bash
# Generate TF tree visualization
ros2 run tf2_tools view_frames

# View generated PDF
evince frames_*.pdf
```

### Inspect Robot Description

```bash
# Process Xacro to URDF
xacro robot.urdf.xacro > robot.urdf

# Validate URDF
check_urdf robot.urdf
```

### Customize RViz

1. Launch RViz with a configuration
2. Add/remove displays as needed
3. Save configuration: File → Save Config As

---

## Learning Exercises

### Exercise 1: Simple URDF

1. Open `myfirst.urdf` and examine its structure
2. Modify the cylinder dimensions
3. Launch with `urdf_rviz.launch.py` to see changes

### Exercise 2: Add a Sensor

1. Study `lidar.xacro` structure
2. Create a new sensor xacro file
3. Include it in `robot.urdf.xacro`
4. Verify in RViz

### Exercise 3: Create RViz Config

1. Launch demo and customize displays
2. Add LaserScan display
3. Configure fixed frame
4. Save as new configuration

---

## Dependencies

- `robot_state_publisher`
- `joint_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`
- `xacro`
- `tf2_ros`

---

## Related Packages

- [slam_toolbox_src](../slam_toolbox_src/README.md) - SLAM configuration
- [nav2_src](../nav2_src/README.md) - Navigation configuration
