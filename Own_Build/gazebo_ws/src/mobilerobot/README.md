# mobilerobot

Comprehensive mobile robot simulation package with differential drive, multiple sensors (LiDAR, camera, IMU), and full Nav2/SLAM integration.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Robot Description](#robot-description)
- [Launch Files](#launch-files)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

---

## Overview

This package provides a complete mobile robot simulation featuring:

- **Differential Drive** - Two-wheel base with caster
- **LiDAR Sensor** - 360° laser scanner for navigation
- **Camera** - Front-facing RGB camera
- **IMU** - Inertial measurement unit
- **Nav2 Integration** - Full autonomous navigation
- **SLAM** - Mapping with SLAM Toolbox or Cartographer

### Robot Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        mobilerobot                               │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Camera  │  │  LiDAR   │  │   IMU    │  │Diff Drive│        │
│  │  Plugin  │  │  Plugin  │  │  Plugin  │  │  Plugin  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │             │               │
│       ▼             ▼             ▼             ▼               │
│  /camera/*      /scan        /imu/data      /cmd_vel           │
│                                              /odom              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Package Structure

```
mobilerobot/
├── CMakeLists.txt
├── package.xml
├── README.md
├── launch/
│   ├── mobilebot.launch.py          # RViz visualization only
│   ├── display.launch.py            # Gazebo + robot spawn
│   ├── gazebo_launch.py             # Full Gazebo with house world
│   ├── gazebohousebot_launch.py     # House world variant
│   ├── cartographer.launch.py       # Cartographer SLAM
│   ├── navigation_launch.py         # Nav2 navigation
│   └── occupancy_grid.launch.py     # Grid publisher
├── urdf/
│   ├── mobilebot.urdf.xacro         # Main robot (includes others)
│   ├── mobilerobot.xacro            # Base platform + sensors
│   └── gazebo_control.xacro         # Diff drive controller
├── config/
│   ├── ros2_controllers.yaml        # Controller config
│   ├── nav2_params.yaml             # Navigation parameters
│   ├── amcl_params.yaml             # AMCL configuration
│   ├── rparams.yaml                 # Robot parameters
│   └── mobilerobot_lds_2d.lua       # Cartographer config
├── rviz/
│   ├── mobilrob.rviz                # General RViz config
│   └── tb3_navigation2.rviz         # Navigation RViz config
├── map/
│   ├── map.pgm                      # Pre-built map
│   └── map.yaml                     # Map metadata
├── models/
│   └── turtlebot3_house/            # Gazebo house model
└── worlds/
    └── turtlebot3_house.world       # House environment
```

---

## Robot Description

### Physical Specifications

| Component | Dimensions | Mass |
|-----------|------------|------|
| Chassis | 0.35m × 0.25m × 0.15m | 2.0 kg |
| Left Wheel | ⌀0.12m × 0.03m | 0.2 kg |
| Right Wheel | ⌀0.12m × 0.03m | 0.2 kg |
| Caster | ⌀0.12m sphere | 0.05 kg |
| **Total** | - | **~2.45 kg** |

### Sensors

#### LiDAR
- Type: Ray sensor (360° scan)
- Samples: 720 per scan
- Range: 0.12m - 20.0m
- Update rate: 10 Hz
- Topic: `/scan`

#### Camera
- Resolution: 640 × 480
- FOV: 60°
- Range: 0.05m - 50.0m
- Update rate: 30 Hz
- Topics: `/camera/image_raw`, `/camera/camera_info`

#### IMU
- Update rate: 50 Hz
- Includes Gaussian noise model
- Topic: `/imu/data`

### Differential Drive

| Parameter | Value |
|-----------|-------|
| Wheel separation | 0.25m |
| Wheel radius | 0.06m |
| Max linear velocity | ~0.5 m/s |
| Max angular velocity | ~2.0 rad/s |

---

## Launch Files

### mobilebot.launch.py

RViz visualization with joint control (no Gazebo).

```bash
ros2 launch mobilerobot mobilebot.launch.py
```

### gazebo_launch.py

Full Gazebo simulation with TurtleBot3 house world.

```bash
ros2 launch mobilerobot gazebo_launch.py
```

### cartographer.launch.py

SLAM mapping with Google Cartographer.

```bash
ros2 launch mobilerobot cartographer.launch.py use_sim_time:=true
```

**Remappings:**
- `/scan` → `/gazebo_ros_ray_sensor/out`
- `/imu` → `/imu/data`

### navigation_launch.py

Autonomous navigation with Nav2.

```bash
ros2 launch mobilerobot navigation_launch.py use_sim_time:=true
```

**Components:**
- Map server with pre-built map
- AMCL localization
- Path planning (NavFn)
- DWB local planner
- Recovery behaviors

---

## Configuration

### ros2_controllers.yaml

```yaml
controller_manager:
  ros__parameters:
    update_rate: 50

diff_drive_controller:
  ros__parameters:
    wheel_separation: 0.25
    wheel_radius: 0.075
    left_wheel_names: ["left_wheel_joint"]
    right_wheel_names: ["right_wheel_joint"]
```

### nav2_params.yaml (265 lines)

Key settings:

| Component | Key Parameters |
|-----------|----------------|
| AMCL | 500-2000 particles, likelihood field |
| Controller | DWB planner, 20 Hz loop |
| Planner | NavFn A* global planner |
| Costmaps | 0.05m resolution, inflation 0.55m |

---

## Usage

### Quick Start Simulation

```bash
# Launch Gazebo with robot
ros2 launch mobilerobot gazebo_launch.py

# Drive with keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Create a Map

```bash
# Launch simulation
ros2 launch mobilerobot gazebo_launch.py

# Start Cartographer SLAM
ros2 launch mobilerobot cartographer.launch.py use_sim_time:=true

# Drive around, then save map
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```

### Autonomous Navigation

```bash
# Launch simulation
ros2 launch mobilerobot gazebo_launch.py

# Start navigation (uses pre-built map)
ros2 launch mobilerobot navigation_launch.py use_sim_time:=true

# In RViz: Use "2D Goal Pose" to send goals
```

### View Sensor Data

```bash
# LiDAR
ros2 topic echo /scan --once

# Camera
ros2 run rqt_image_view rqt_image_view

# IMU
ros2 topic echo /imu/data
```

---

## Troubleshooting

### Robot not moving

```bash
# Check controller is loaded
ros2 control list_controllers

# Verify cmd_vel
ros2 topic echo /cmd_vel
```

### No LiDAR data

```bash
# Check topic (Gazebo remaps)
ros2 topic list | grep -E "scan|ray"

# Echo correct topic
ros2 topic echo /gazebo_ros_ray_sensor/out
```

### Navigation fails

```bash
# Check TF tree
ros2 run tf2_tools view_frames

# Verify map is loaded
ros2 topic echo /map --once
```

---

## Dependencies

- `gazebo_ros`, `gazebo_ros2_control`
- `ros2_control`, `ros2_controllers`
- `nav2_bringup`, `nav2_amcl`, `nav2_planner`, `nav2_controller`
- `slam_toolbox`, `cartographer_ros`
- `robot_state_publisher`, `joint_state_publisher`
- `xacro`, `rviz2`

---

## Related Packages

- [line_follower_robot](../line_follower_robot/README.md) - Line following simulation
- [simple_robot_car](../simple_robot_car/README.md) - Basic car platform
