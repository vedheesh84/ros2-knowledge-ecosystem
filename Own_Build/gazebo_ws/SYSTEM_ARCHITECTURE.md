# gazebo_ws - System Architecture

## Package Overview

| Package | Layer | Purpose |
|---------|-------|---------|
| `mobilerobot` | Full Stack | Mobile robot with SLAM, Nav2, sensors |
| `line_follower_robot` | Visualization | Mesh-based differential drive model |
| `simple_robot_car` | Visualization | SolidWorks 4WD model (minimal) |
| `simple_linefollower_robot` | Visualization | Parameterized differential drive |

---

## 1. Package-by-Package Analysis

### mobilerobot (Full Stack)

**Purpose:** Complete mobile robot simulation with SLAM, navigation, and sensor suite

**Architecture Layers:**
- **Perception:** Camera, LIDAR (720 samples), IMU
- **Navigation:** Nav2 stack, Cartographer SLAM
- **Control:** Differential drive controller
- **System:** Gazebo simulation infrastructure

**Nodes:**
| Node | Responsibility |
|------|----------------|
| `robot_state_publisher` | TF tree from URDF |
| `gazebo_ros_diff_drive` | Differential drive physics |
| `gazebo_ros_camera` | Camera simulation (640×480, 30Hz) |
| `gazebo_ros_ray_sensor` | LIDAR (720 samples, 10Hz) |
| `gazebo_ros_imu` | IMU (50Hz) |
| `map_server` | Static map provider |
| `amcl` | Particle filter (2000 particles) |
| `planner_server` | NavFn global planner |
| `controller_server` | DWB local planner |
| `bt_navigator` | Behavior tree navigation |
| `cartographer_node` | Online SLAM |

**Topics Published:**
| Topic | Type | Rate | Purpose |
|-------|------|------|---------|
| `/camera/image_raw` | Image | 30Hz | Front camera |
| `/scan` | LaserScan | 10Hz | LIDAR (720 samples, 0.12-20m) |
| `/imu/data` | Imu | 50Hz | IMU measurements |
| `/odom` | Odometry | - | Wheel odometry |
| `/map` | OccupancyGrid | - | Static/SLAM map |
| `/cmd_vel` | Twist | - | Velocity commands |

**Key Parameters:**
```yaml
Differential Drive:
  wheel_separation: 0.28 m (Gazebo) / 0.25 m (controller - MISMATCH!)
  wheel_diameter: 0.10 m
  max_wheel_torque: 20 Nm

AMCL:
  min_particles: 500
  max_particles: 2000
  laser_model_type: likelihood_field

Nav2 Controller:
  max_vel_x: 0.26 m/s
  max_vel_theta: 1.0 rad/s
```

**Known Issues:**
- **Wheel separation mismatch:** Gazebo (0.28m) vs controller (0.25m) causes ~10% odometry error
- **TF conflicts:** Multiple nodes publishing odom→base_link

---

### line_follower_robot (Visualization Layer)

**Purpose:** Demonstration robot using SolidWorks meshes

**URDF Structure:**
```
base_link (STL mesh)
├── left_wheel (continuous joint)
├── right_wheel (continuous joint)
└── castor_base_link
    └── castor_wheel (passive)
```

**Node:** `wheel_publisher.py`
- Publishes constant wheel velocity (4.0 rad/s) at 50Hz
- **Note:** Not integrated with Gazebo physics (demo only)

**Launch Variants (7 files):**
- `gazebo_xacro_rviz.launch.py` - XACRO visualization
- `gazebo_empty.launch.py` - Empty Gazebo world
- `gazebo_sdf.launch.py` - SDF model spawn
- `rviz_xacro.launch.py` - RViz only
- `rviz_urdf.launch.py` - Static URDF

**Issue:** wheel_publisher runs independently of Gazebo simulation

---

### simple_robot_car (Minimal Visualization)

**Purpose:** SolidWorks-generated 4WD visualization model

**URDF Structure:**
```
base_link
├── FR_wheel_joint (continuous)
├── FL_wheel_joint (continuous)
├── BR_wheel_joint (continuous)
└── BL_wheel_joint (continuous)
```

**Status:** Visualization only, no control integration

---

### simple_linefollower_robot (Parameterized Model)

**Purpose:** Best-practice parameterized differential drive template

**URDF Structure (Parameterized):**
```xml
Properties:
  Sphere radius: 0.06 m
  Wheel radius: 0.04 m, width: 0.03 m
  Box (base): 0.30 × 0.20 × 0.10 m
  Material density: 2700 kg/m³ (aluminum)

Links:
  base_link → LW_link, RW_link, sphear_link (passive caster)
```

**Strengths:**
- Fully parameterized geometry
- No mesh dependencies
- Auto-calculated inertias
- Good template for other robots

---

## 2. System Architecture Analysis

### Package Tiers

```
Tier 1 - Full Featured (mobilerobot):
├── Sensors (Camera, LIDAR, IMU)
├── Navigation (Nav2 stack)
├── SLAM (Cartographer)
├── Localization (AMCL)
└── Control (ros2_control)

Tier 2 - Medium (line_follower_robot):
├── Multiple simulation formats (XACRO, URDF, SDF)
├── Multiple launch variants
└── Demo control (wheel_publisher.py)

Tier 3 - Minimal (simple_robot_car, simple_linefollower_robot):
├── Visualization focus
├── No control integration
└── Learning/template purpose
```

### Data Flow (mobilerobot)

```
Gazebo Simulator
    ↓
├─→ Sensor Simulators (Camera, LIDAR, IMU)
│       ↓
│       ├─→ /scan → Cartographer SLAM / AMCL
│       └─→ /imu/data → State estimation
│
├─→ Odometry (diff_drive plugin)
│       ↓
│       └─→ /odom (TF: odom→base_link)
│
└─→ cmd_vel Input
        ↓
        └─→ diff_drive_controller → Wheel Physics
```

---

## 3. Coordination Patterns

### Lifecycle Management (mobilerobot)

```
lifecycle_manager orchestrates:
1. map_server (provides /map)
2. amcl (consumes /map, /scan)
3. planner_server (consumes /map)
4. controller_server (consumes /local_plan)
5. bt_navigator (orchestrates navigation)
```

### Simulation Time Synchronization

- All nodes configured with `use_sim_time: true`
- Gazebo publishes simulated time on `/clock`
- Navigation stack consumes simulated time

---

## 4. Coupling Analysis

### Tight Couplings

| Coupling | Risk |
|----------|------|
| Wheel separation mismatch | 10% odometry error |
| URDF ↔ Gazebo plugins | Hardcoded joint names |
| Map-AMCL dependency | No pre-exploration capability |
| TF tree consistency | Multiple transform publishers |

### Loose Couplings

| Component | Why Loose |
|-----------|-----------|
| RViz visualization | Optional, reads /tf only |
| Cartographer vs AMCL | Independent consumers of /scan |
| wheel_publisher ↔ Gazebo | Independent systems |

---

## 5. Failure Propagation Paths

| Failure Mode | Impact | Severity |
|--------------|--------|----------|
| Wheel separation mismatch | Localization drift | HIGH |
| Missing /scan | Costmap fails, navigation blind | HIGH |
| TF conflicts (odom→base_link) | Race condition | MEDIUM |
| Gazebo crash (/clock stops) | All nodes hang | HIGH |
| Missing Cartographer config | Launch fails | MEDIUM |

---

## 6. Reusability Analysis

### High Reusability

| Component | Reason |
|-----------|--------|
| simple_linefollower_robot XACRO | Fully parameterized |
| Nav2 configuration | Standard patterns |
| AMCL parameters | Tunable for robots |

### Low Reusability

| Component | Reason |
|-----------|--------|
| Gazebo plugins (joint names) | Hardcoded |
| SolidWorks meshes | Not parameterized |
| wheel_publisher.py | Demo only |

---

## 7. Topic Summary

| Topic | Publisher | Subscriber | Type |
|-------|-----------|------------|------|
| `/scan` | gazebo_ros_ray_sensor | SLAM, Nav2 | LaserScan |
| `/camera/image_raw` | gazebo_ros_camera | Perception | Image |
| `/imu/data` | gazebo_ros_imu | Estimation | Imu |
| `/odom` | diff_drive_plugin | Nav2 | Odometry |
| `/map` | map_server/cartographer | Nav2 | OccupancyGrid |
| `/cmd_vel` | Nav2/teleop | diff_drive | Twist |
| `/joint_states` | wheel_publisher | RSP | JointState |

---

## 8. Parameter Summary

| Package | Key Parameters |
|---------|----------------|
| mobilerobot | `wheel_separation`, `wheel_diameter`, AMCL particles |
| line_follower | wheel_publisher rate (50Hz), velocity (4.0 rad/s) |
| simple_linefollower | Geometry parameters (wheel_radius, base dimensions) |

---

## 9. Critical Issues

| Issue | Package | Impact | Fix |
|-------|---------|--------|-----|
| Wheel separation mismatch | mobilerobot | Navigation errors | Synchronize Gazebo and controller values |
| Disconnected wheel_publisher | line_follower | Simulation not synced | Integrate with Gazebo physics |
| Multiple TF publishers | mobilerobot | TF race conditions | Single TF source per transform |

---

## 10. Summary Table

| Aspect | mobilerobot | line_follower | simple_robot_car | simple_linefollower |
|--------|-------------|---------------|------------------|---------------------|
| **Complexity** | Very High | High | Low | Medium |
| **Sensors** | Camera, LIDAR, IMU | None | None | None |
| **Navigation** | Full Nav2 | None | None | None |
| **Control** | ros2_control | Demo only | None | None |
| **URDF Format** | XACRO | Mixed | SolidWorks | XACRO (parameterized) |
| **Reusability** | Medium | Low | Very Low | High |
| **Production Ready** | Partial | Demo | Educational | Template |

