# navigation_sim

Modular Nav2 navigation and SLAM simulation package providing plug-and-play autonomous navigation capability through SLAM Toolbox mapping and Navigation2 stack.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Launch Files](#launch-files)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

---

## Overview

This package provides a complete simulation environment for testing navigation and SLAM capabilities of the mobile manipulator. It integrates:

- **SLAM Toolbox** for online asynchronous mapping
- **Navigation2** for autonomous path planning and control
- **Gazebo** simulation with robot spawning
- **RViz** visualization for monitoring

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        navigation_sim                            │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Gazebo     │───▶│ SLAM Toolbox │───▶│    Nav2      │       │
│  │  Simulation  │    │   Mapping    │    │  Navigation  │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────────────────────────────────────────────┐       │
│  │                    /scan, /odom, /tf                  │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Package Structure

```
navigation_sim/
├── CMakeLists.txt
├── package.xml
├── launch/
│   └── sim_mapping.launch.py      # SLAM mapping simulation
├── config/
│   ├── localisation_params.yaml   # SLAM Toolbox localization mode
│   ├── mapping_params.yaml        # SLAM Toolbox mapping mode
│   └── nav2_params.yaml           # Navigation2 stack parameters
└── maps/                          # Pre-recorded maps (if any)
```

---

## Launch Files

### sim_mapping.launch.py

Comprehensive simulation launch for SLAM mapping with Gazebo.

**Nodes Launched:**
- `robot_state_publisher` - Publishes TF transforms from URDF
- `joint_state_publisher` - Publishes joint states
- `spawn_entity.py` - Spawns robot in Gazebo
- `diff_drive_controller` - Differential drive control
- `joint_state_broadcaster` - Broadcasts joint states
- `teleop_twist_keyboard` - Manual control (new terminal)
- `slam_toolbox` - SLAM mapping node
- `rviz2` - Visualization

**Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `use_sim_time` | `true` | Enable Gazebo simulation clock |
| `x_pose` | `0.0` | Initial X position |
| `y_pose` | `0.0` | Initial Y position |
| `z_pose` | `0.1` | Initial Z position (robot height) |

---

## Configuration

### mapping_params.yaml

SLAM Toolbox parameters for building new maps.

| Parameter | Value | Description |
|-----------|-------|-------------|
| `solver_plugin` | `solver_plugins::CeresSolver` | Optimization backend |
| `odom_frame` | `odom` | Odometry TF frame |
| `map_frame` | `map` | Map TF frame |
| `base_frame` | `body_link` | Robot base TF frame |
| `scan_topic` | `/scan` | Laser scan input topic |
| `max_laser_range` | `20.0` | Maximum laser range (meters) |
| `resolution` | `0.05` | Map resolution (meters/cell) |
| `mode` | `mapping` | SLAM mode |

### localisation_params.yaml

SLAM Toolbox parameters for localizing in existing maps.

| Parameter | Value | Description |
|-----------|-------|-------------|
| `mode` | `localization` | Localization mode |
| `map_file_name` | (set at runtime) | Pre-built map to load |

### nav2_params.yaml

Complete Navigation2 stack configuration (~350 lines).

**Key Components:**

| Component | Description |
|-----------|-------------|
| **AMCL** | Adaptive Monte Carlo Localization (500-2000 particles) |
| **Controller Server** | DWB local planner for differential drive |
| **Planner Server** | NavFn global path planner |
| **Behavior Server** | Recovery behaviors (spin, backup, wait) |
| **Costmaps** | Local and global with obstacle/inflation layers |
| **Velocity Smoother** | Open-loop velocity smoothing |

**Motion Limits:**

| Parameter | Value |
|-----------|-------|
| Max linear velocity | 0.26 m/s |
| Max angular velocity | 1.0 rad/s |
| Linear acceleration | 2.5 m/s² |
| Angular acceleration | 3.2 rad/s² |
| Goal tolerance (xy) | ±0.25 m |
| Goal tolerance (yaw) | ±0.25 rad |

---

## Usage

### Create a New Map

```bash
# Terminal 1: Launch mapping simulation
ros2 launch navigation_sim sim_mapping.launch.py

# Terminal 2: Drive the robot using keyboard
# (automatically opened by launch file)
# Use: i=forward, j=left, l=right, k=stop, ,=backward

# Terminal 3: Save the map when done
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```

### Localize in Existing Map

```bash
# Modify localisation_params.yaml to point to your map
# Then launch with localization mode
ros2 launch navigation_sim sim_mapping.launch.py \
  slam_params_file:=$(ros2 pkg prefix navigation_sim)/share/navigation_sim/config/localisation_params.yaml
```

### Send Navigation Goals

```bash
# Use RViz: Click "2D Goal Pose" button and click on map
# Or use command line:
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.0}}}}"
```

---

## Troubleshooting

### Robot not moving in simulation

```bash
# Check if controllers are loaded
ros2 control list_controllers

# Verify cmd_vel is being published
ros2 topic echo /cmd_vel
```

### SLAM not building map

```bash
# Check laser scan data
ros2 topic echo /scan --once

# Verify TF tree is complete
ros2 run tf2_tools view_frames
```

### Navigation goals failing

```bash
# Check costmap updates
ros2 topic echo /local_costmap/costmap --once

# Verify localization
ros2 topic echo /amcl_pose
```

---

## Dependencies

- `nav2_bringup`, `nav2_bt_navigator`, `nav2_controller`
- `nav2_planner`, `nav2_behaviors`, `nav2_map_server`
- `nav2_amcl`, `nav2_lifecycle_manager`, `nav2_costmap_2d`
- `slam_toolbox`
- `tf2_ros`, `tf2`

---

## Related Packages

- [mobile_manipulator_sim](../mobile_manipulator_sim/README.md) - Full system Gazebo simulation
- [mobile_manipulator_navigation](../../mobile_manipulator/mobile_manipulator_navigation/README.md) - Real robot navigation
