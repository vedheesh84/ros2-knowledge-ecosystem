# cartographer_src

Google Cartographer SLAM configuration package for 2D/3D laser-based mapping. Provides launch files and Lua configuration for high-quality SLAM.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Launch Files](#launch-files)
- [Configuration](#configuration)
- [Usage](#usage)
- [Comparison](#comparison)

---

## Overview

This package wraps Google Cartographer for ROS2:

- **High-Quality SLAM** - Loop closure and pose graph optimization
- **2D Mapping** - Laser-based occupancy grid mapping
- **Real-time Performance** - Optimized for online operation

### Cartographer vs SLAM Toolbox

| Feature | Cartographer | SLAM Toolbox |
|---------|--------------|--------------|
| Loop closure | Excellent | Good |
| CPU usage | Higher | Lower |
| Map quality | Very high | Good |
| Configuration | Lua files | YAML files |
| Lifelong SLAM | Limited | Built-in |

---

## Package Structure

```
cartographer_src/
├── launch/
│   ├── cartographer_SimpleCar.launch.py  # Main Cartographer launch
│   └── occupancy_grid.launch.py          # Grid publisher
├── config/
│   └── turtlebot3_lds_2d.lua             # 2D SLAM configuration
└── CMakeLists.txt
```

---

## Launch Files

### cartographer_SimpleCar.launch.py

Launches Cartographer SLAM with occupancy grid generation.

```bash
ros2 launch cartographer_src cartographer_SimpleCar.launch.py
```

**Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `cartographer_config_dir` | Package config | Config directory |
| `configuration_basename` | `turtlebot3_lds_2d.lua` | Lua config file |
| `use_sim_time` | `false` | Use simulation clock |

**Nodes:**
- `cartographer_node` - SLAM node
- `cartographer_occupancy_grid_node` - Grid publisher

### occupancy_grid.launch.py

Standalone occupancy grid publisher.

```bash
ros2 launch cartographer_src occupancy_grid.launch.py
```

**Parameters:**
- `resolution` - Grid resolution (default: 0.05m)
- `publish_period_sec` - Update rate (default: 1.0s)

---

## Configuration

### turtlebot3_lds_2d.lua

Lua configuration for 2D laser SLAM.

#### Map Builder Settings

```lua
map_builder = MAP_BUILDER
trajectory_builder = TRAJECTORY_BUILDER

-- Frames
map_frame = "map"
tracking_frame = "base_link"
published_frame = "odom"
odom_frame = "odom"
```

#### Sensor Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `num_laser_scans` | `1` | Number of laser scanners |
| `num_point_clouds` | `0` | Number of 3D sensors |
| `use_odometry` | `true` | Use wheel odometry |
| `use_imu_data` | `false` | Use IMU (disabled) |

#### Range Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| `min_range` | `0.12` | Minimum valid range (m) |
| `max_range` | `3.5` | Maximum valid range (m) |

#### Pose Graph Optimization

| Parameter | Value | Description |
|-----------|-------|-------------|
| `constraint_builder.min_score` | `0.65` | Local match threshold |
| `global_localization_min_score` | `0.7` | Global match threshold |
| `optimize_every_n_nodes` | `90` | Optimization frequency |

---

## Usage

### Run Cartographer SLAM

```bash
# Terminal 1: Launch robot or simulation

# Terminal 2: Start Cartographer
ros2 launch cartographer_src cartographer_SimpleCar.launch.py use_sim_time:=true

# Terminal 3: Drive robot
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Save Map

```bash
# Finish trajectory first
ros2 service call /finish_trajectory cartographer_ros_msgs/srv/FinishTrajectory "{trajectory_id: 0}"

# Write state
ros2 service call /write_state cartographer_ros_msgs/srv/WriteState "{filename: '/tmp/my_map.pbstream'}"

# Convert to standard map format
ros2 run nav2_map_server map_saver_cli -f ~/my_map
```

### Visualize in RViz

Add displays:
- **Map** - Topic: `/map`
- **Submaps** - Topic: `/submap_list`
- **Trajectory** - Topic: `/trajectory_node_list`
- **Constraints** - Topic: `/constraint_list`

---

## Tuning Guide

### For Large Environments

```lua
-- Increase submap size
TRAJECTORY_BUILDER_2D.submaps.num_range_data = 120

-- More aggressive loop closure
POSE_GRAPH.constraint_builder.min_score = 0.55
```

### For Noisy Sensors

```lua
-- Filter outliers
TRAJECTORY_BUILDER_2D.min_range = 0.2
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 1.0
```

### For Faster Updates

```lua
-- Reduce resolution
TRAJECTORY_BUILDER_2D.submaps.resolution = 0.1
```

---

## Troubleshooting

### No map being built

```bash
# Check laser scan
ros2 topic echo /scan --once

# Verify TF tree
ros2 run tf2_tools view_frames
```

### Poor loop closure

```bash
# Lower threshold in Lua config
# constraint_builder.min_score = 0.5
```

### High CPU usage

```bash
# Increase optimize_every_n_nodes
# Reduce submap resolution
```

---

## Dependencies

- `cartographer_ros`
- `nav_msgs`
- `sensor_msgs`
- `tf2_ros`

---

## Related Packages

- [slam_toolbox_src](../slam_toolbox_src/README.md) - Alternative SLAM
- [nav2_src](../nav2_src/README.md) - Navigation integration
