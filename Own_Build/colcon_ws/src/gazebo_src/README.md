# gazebo_src

Gazebo simulation configuration package for robot simulation and world management. Contains launch files, world definitions, and robot spawning configurations.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Worlds](#worlds)
- [Launch Files](#launch-files)
- [Usage](#usage)

---

## Overview

This package provides Gazebo simulation capabilities:

- **World Management** - Pre-defined simulation environments
- **Robot Spawning** - Spawn robots from URDF/SDF
- **Physics Simulation** - Realistic physics with ODE

### Gazebo Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Gazebo Simulation                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  gzserver   │  │  gzclient   │  │ spawn_entity│              │
│  │  (physics)  │  │   (GUI)     │  │   (robots)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│         │                                   │                    │
│         ▼                                   ▼                    │
│    World SDF                          Robot URDF/SDF             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Package Structure

```
gazebo_src/
├── launch/
│   ├── gazebo_world.launch.py        # Cafe world simulation
│   └── gazebo_turtleworld.launch.py  # TurtleBot world
├── worlds/
│   ├── cafe_world.world              # Cafe environment
│   ├── simple_world.world            # Simple test env
│   └── turtlebot3_world.world        # TB3 environment
└── CMakeLists.txt
```

---

## Worlds

### cafe_world.world

Multi-room cafe environment with realistic features.

**Features:**
- Ground plane with friction
- Directional sun lighting
- Walls and obstacles
- ODE physics engine

### simple_world.world

Minimal environment for basic testing.

**Features:**
- Flat ground plane
- No obstacles
- Good for sensor testing

### turtlebot3_world.world

TurtleBot3-specific environment.

**Features:**
- Compatible with TB3 navigation demos
- Standard layout for benchmarking

---

## Launch Files

### gazebo_world.launch.py

Launches Gazebo with cafe world and spawns robot.

```bash
ros2 launch gazebo_src gazebo_world.launch.py
```

**Nodes:**
- `gzserver` - Physics simulation (headless)
- `gzclient` - Gazebo GUI
- `spawn_entity.py` - Robot spawner

**Robot Spawned:** `simple_robot_car` from robot_description topic

### gazebo_turtleworld.launch.py

TurtleBot3 world variant.

```bash
ros2 launch gazebo_src gazebo_turtleworld.launch.py
```

---

## Usage

### Launch Simulation

```bash
# Launch cafe world with robot
ros2 launch gazebo_src gazebo_world.launch.py

# Headless mode (no GUI)
ros2 launch gazebo_src gazebo_world.launch.py gui:=false
```

### Spawn Additional Robots

```bash
# Spawn robot at specific position
ros2 run gazebo_ros spawn_entity.py \
  -topic robot_description \
  -entity my_robot \
  -x 1.0 -y 2.0 -z 0.1
```

### Control Robot

```bash
# Keyboard teleoperation
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Topic: /cmd_vel
```

### Check Simulation

```bash
# List spawned models
ros2 service call /get_model_list gazebo_msgs/srv/GetModelList

# Check physics state
ros2 topic echo /gazebo/model_states
```

---

## Creating Custom Worlds

### SDF World Template

```xml
<?xml version="1.0" ?>
<sdf version="1.7">
  <world name="my_world">
    <!-- Ground plane -->
    <include>
      <uri>model://ground_plane</uri>
    </include>

    <!-- Lighting -->
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Your models here -->
  </world>
</sdf>
```

### Adding to Package

1. Save world file to `worlds/` directory
2. Update CMakeLists.txt to install it
3. Reference in launch file

---

## Troubleshooting

### Gazebo not starting

```bash
# Check Gazebo installation
gazebo --version

# Kill zombie processes
killall gzserver gzclient
```

### Robot not spawning

```bash
# Verify robot_description topic
ros2 topic echo /robot_description --once

# Check spawn_entity output
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity test
```

### Physics issues

```bash
# Reduce simulation speed if needed
# Edit world file physics parameters
```

---

## Dependencies

- `gazebo_ros`
- `gazebo_ros_pkgs`
- `robot_state_publisher`
- `xacro`

---

## Related Packages

- [rviz_tutorial](../rviz_tutorial/README.md) - Robot visualization
- [nav2_src](../nav2_src/README.md) - Navigation in simulation
