# nav2_src

Navigation2 stack configuration package for autonomous robot navigation. Contains launch files and parameter configurations for path planning, control, and behavior management.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Launch Files](#launch-files)
- [Configuration](#configuration)
- [Usage](#usage)

---

## Overview

This package provides Navigation2 configurations for:

- **Path Planning** - Global route computation
- **Local Control** - Obstacle avoidance and trajectory following
- **Localization** - AMCL Monte Carlo localization
- **Behaviors** - Recovery actions (spin, backup, wait)

### Nav2 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Behavior Tree Navigator                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Planner   │  │ Controller  │  │  Behaviors  │              │
│  │   Server    │  │   Server    │  │   Server    │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
    Global Path      Local Cmd_vel     Recovery Actions
```

---

## Package Structure

```
nav2_src/
├── launch/
│   ├── navigation_launch.py      # Full Nav2 stack
│   └── nav2_SimpleCar.launch.py  # SimpleCar configuration
├── config/
│   └── nav2_params.yaml          # Navigation parameters
└── CMakeLists.txt
```

---

## Launch Files

### navigation_launch.py

Complete Navigation2 stack launch with lifecycle management.

```bash
ros2 launch nav2_src navigation_launch.py
```

**Lifecycle Nodes:**
- `controller_server` - Local trajectory control
- `planner_server` - Global path planning
- `behavior_server` - Recovery behaviors
- `bt_navigator` - Behavior tree navigation
- `waypoint_follower` - Waypoint following
- `velocity_smoother` - Velocity smoothing

**Features:**
- Node respawning for robustness
- Configurable log levels
- Namespace support
- Optional containerized deployment

### nav2_SimpleCar.launch.py

Simplified launch for SimpleCar robot platform.

---

## Configuration

### nav2_params.yaml

#### AMCL (Localization)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `max_particles` | `2000` | Maximum particle count |
| `min_particles` | `500` | Minimum particle count |
| `laser_model_type` | `likelihood_field` | Sensor model |
| `alpha_fast` | `0.1` | Fast decay for adaptive |
| `alpha_slow` | `0.001` | Slow decay for adaptive |
| `update_min_d` | `0.2` | Min translation for update |
| `update_min_a` | `0.5` | Min rotation for update |

#### Controller Server

| Parameter | Value | Description |
|-----------|-------|-------------|
| `controller_frequency` | `20.0` | Control loop rate (Hz) |
| `controller_plugins` | `[FollowPath]` | Controller plugins |
| `progress_checker_plugin` | `progress_checker` | Progress monitoring |
| `goal_checker_plugin` | `general_goal_checker` | Goal verification |

#### Planner Server

| Parameter | Value | Description |
|-----------|-------|-------------|
| `planner_plugins` | `[GridBased]` | Planner plugins |
| `GridBased.plugin` | `nav2_navfn_planner/NavfnPlanner` | A* planner |
| `GridBased.tolerance` | `0.5` | Goal tolerance (m) |

#### Costmaps

| Layer | Description |
|-------|-------------|
| `static_layer` | Pre-built map obstacles |
| `obstacle_layer` | Dynamic sensor obstacles |
| `voxel_layer` | 3D obstacle representation |
| `inflation_layer` | Safety buffer around obstacles |

---

## Usage

### Start Navigation

```bash
# 1. Ensure robot is localized (map + AMCL running)
# 2. Launch navigation stack
ros2 launch nav2_src navigation_launch.py

# 3. Send navigation goal via RViz "2D Goal Pose" tool
```

### Command Line Navigation

```bash
# Send goal programmatically
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 1.0}, orientation: {w: 1.0}}}}"
```

### Waypoint Following

```bash
# Send multiple waypoints
ros2 action send_goal /follow_waypoints nav2_msgs/action/FollowWaypoints \
  "{poses: [{header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.0}}},
            {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 1.0}}}]}"
```

---

## Troubleshooting

### Navigation fails to start

```bash
# Check lifecycle node states
ros2 lifecycle list
ros2 lifecycle get /controller_server

# Verify parameters loaded
ros2 param list /controller_server
```

### Robot not moving

```bash
# Check cmd_vel output
ros2 topic echo /cmd_vel

# Verify costmap is updating
ros2 topic hz /local_costmap/costmap
```

### Path planning fails

```bash
# Check global costmap
ros2 topic echo /global_costmap/costmap --once

# Verify start and goal are in free space
```

---

## Dependencies

- `nav2_bringup`
- `nav2_bt_navigator`
- `nav2_planner`
- `nav2_controller`
- `nav2_behaviors`
- `nav2_map_server`
- `nav2_amcl`
- `nav2_lifecycle_manager`
- `nav2_waypoint_follower`

---

## Related Packages

- [slam_toolbox_src](../slam_toolbox_src/README.md) - SLAM for map creation
- [gazebo_src](../gazebo_src/README.md) - Simulation environment
