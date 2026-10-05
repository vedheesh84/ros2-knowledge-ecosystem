# slam_toolbox_src

SLAM Toolbox configuration package for 2D laser-based mapping and localization. Provides launch files, parameter configurations, and pre-recorded maps.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Launch Files](#launch-files)
- [Configuration](#configuration)
- [Maps](#maps)
- [Usage](#usage)

---

## Overview

This package wraps SLAM Toolbox with custom configurations for:

- **Online Mapping** - Build maps in real-time
- **Localization** - Localize in existing maps
- **Lifelong SLAM** - Long-term map updates

### SLAM Toolbox Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `mapping` | Creates new maps from scratch | Exploring new environments |
| `localization` | Uses existing map for positioning | Navigation in known areas |
| `lifelong` | Updates maps over time | Long-term deployment |

---

## Package Structure

```
slam_toolbox_src/
├── launch/
│   ├── slam_mapping.launch.py       # Online mapping mode
│   ├── slam_localisation.launch.py  # Localization mode
│   └── amcl_localisation.launch.py  # AMCL alternative
├── config/
│   ├── mapping_params.yaml          # Mapping configuration
│   └── localisation_params.yaml     # Localization configuration
├── maps/
│   ├── box_map/                     # Box environment
│   ├── cafe_map/                    # Cafe environment
│   └── turtle3_map/                 # TurtleBot3 map
└── CMakeLists.txt
```

---

## Launch Files

### slam_mapping.launch.py

Online asynchronous SLAM mapping mode.

```bash
ros2 launch slam_toolbox_src slam_mapping.launch.py
```

**Nodes:**
- `robot_state_publisher` - TF from URDF
- `slam_toolbox` (async mode) - SLAM node
- `rviz2` - Visualization

### slam_localisation.launch.py

Localization in a pre-built map.

```bash
ros2 launch slam_toolbox_src slam_localisation.launch.py
```

**Prerequisites:** Set `map_file_name` in `localisation_params.yaml`

### amcl_localisation.launch.py

Alternative localization using AMCL with map server.

```bash
ros2 launch slam_toolbox_src amcl_localisation.launch.py
```

---

## Configuration

### mapping_params.yaml

| Parameter | Value | Description |
|-----------|-------|-------------|
| `solver_plugin` | `solver_plugins::CeresSolver` | Optimization backend |
| `ceres_linear_solver` | `SPARSE_NORMAL_CHOLESKY` | Solver type |
| `odom_frame` | `odom` | Odometry frame |
| `map_frame` | `map` | Map frame |
| `base_frame` | `base_link` | Robot base frame |
| `scan_topic` | `/scan` | Laser scan input |
| `resolution` | `0.05` | Map resolution (m/cell) |
| `max_laser_range` | `20.0` | Max scan range (m) |
| `mode` | `mapping` | SLAM mode |

**Loop Closure Parameters:**

| Parameter | Value | Description |
|-----------|-------|-------------|
| `loop_search_maximum_distance` | `8.0` | Search radius (m) |
| `loop_match_minimum_chain_size` | `10` | Min matches for closure |
| `do_loop_closing` | `true` | Enable loop closure |

### localisation_params.yaml

Same structure as mapping, with key differences:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `mode` | `localization` | Localization mode |
| `map_file_name` | (set path) | Pre-built map file |

---

## Maps

Pre-recorded maps for testing and development:

### box_map/

Simple rectangular environment.
- `box_map.save.pgm` - Occupancy grid image
- `box_map.save.yaml` - Map metadata
- `box_map.serial.data` - SLAM Toolbox data
- `box_map.serial.posegraph` - Pose graph

### cafe_map/

Complex indoor environment (cafe layout).

### turtle3_map/

TurtleBot3 compatible environment.

---

## Usage

### Create a New Map

```bash
# 1. Launch your robot or simulation

# 2. Start SLAM mapping
ros2 launch slam_toolbox_src slam_mapping.launch.py

# 3. Drive robot around to explore
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 4. Save the map
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap \
  "{name: {data: 'my_map'}}"
```

### Localize in Existing Map

```bash
# 1. Edit localisation_params.yaml to set map_file_name
# 2. Launch localization
ros2 launch slam_toolbox_src slam_localisation.launch.py
```

### View Map in RViz

Add these displays:
- **Map** - Topic: `/map`
- **LaserScan** - Topic: `/scan`
- **TF** - Show transform tree

---

## Troubleshooting

### Map not building

```bash
# Check laser scan data
ros2 topic echo /scan --once

# Verify TF tree
ros2 run tf2_tools view_frames

# Check odom → base_link transform exists
```

### Localization drifting

```bash
# Increase particle count in params
# Check scan matcher parameters
# Ensure map matches environment
```

---

## Dependencies

- `slam_toolbox`
- `nav_msgs`
- `sensor_msgs`
- `tf2_ros`
- `robot_state_publisher`

---

## Related Packages

- [cartographer_src](../cartographer_src/README.md) - Alternative SLAM
- [nav2_src](../nav2_src/README.md) - Navigation integration
