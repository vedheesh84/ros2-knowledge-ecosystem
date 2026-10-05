# Simulation Packages

This directory contains Gazebo simulation packages for testing and development of the mobile manipulator system.

## Packages

| Package | Description | Documentation |
|---------|-------------|---------------|
| **mobile_manipulator_sim** | Full system Gazebo simulation with complete robot | [README](mobile_manipulator_sim/README.md) |
| **navigation_sim** | Navigation and SLAM simulation with Nav2 | [README](navigation_sim/README.md) |

---

## Quick Start

### Full System Simulation

```bash
# Launch complete robot in Gazebo with RViz
ros2 launch mobile_manipulator_sim sim.launch.py
```

### Navigation Testing

```bash
# Launch SLAM mapping simulation
ros2 launch navigation_sim sim_mapping.launch.py
```

---

## Package Descriptions

### mobile_manipulator_sim

Comprehensive Gazebo simulation of the complete mobile manipulator:
- Full robot URDF with differential drive base and 6-DOF arm
- Sensor simulation (LiDAR, camera, IMU)
- ros2_control integration for hardware interfaces
- Multiple launch configurations (sim-only, with MoveIt, with Nav2)

### navigation_sim

Focused simulation for navigation and mapping:
- SLAM Toolbox integration for mapping
- Nav2 configuration for autonomous navigation
- Teleoperation support for manual control
- Pre-configured for common navigation scenarios

---

## Simulation Modes

| Mode | Command | Use Case |
|------|---------|----------|
| Basic simulation | `ros2 launch mobile_manipulator_sim sim.launch.py` | General testing |
| With MoveIt | `ros2 launch mobile_manipulator_sim moveit_gazebo.launch.py` | Arm motion planning |
| SLAM mapping | `ros2 launch navigation_sim sim_mapping.launch.py` | Create maps |
| Navigation | Modify nav2 params | Autonomous navigation |

---

## Dependencies

All simulation packages require:
- `gazebo_ros_pkgs`
- `gazebo_ros2_control`
- `ros2_control`
- `ros2_controllers`

Navigation simulation additionally requires:
- `nav2_bringup`
- `slam_toolbox`
