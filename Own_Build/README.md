# Custom Robot Builds & Experimental Packages (`Own_Build`)

**Experimental Robot Models, Custom Simulations & Engineering Assessments**

This directory houses custom robot models, experimental packages, simulation worlds, and technical assessment reports developed within the Intelligent Systems Knowledge Ecosystem.

---

## 1. Directory Structure & Architecture

```text
Own_Build/
├── README.md                             # Primary index & guide (this document)
├── ASSESSMENT_REPORTS/                   # Technical & academic static code audit reports
│   ├── README.md                         # Assessment framework & score overview
│   ├── 01_robot_pkg.md                   # Multi-model learning & Nav2 package audit
│   ├── 02_balancing_robot.md             # Two-wheeled inverted pendulum audit
│   ├── 03_cad_description.md             # 4WD CAD rover description audit
│   ├── 04_drone_pkg.md                   # Quadrotor kinematic flight audit
│   ├── 05_spider_pkg.md                  # 18-DOF Hexapod spider & C++ gait plugin audit
│   └── ARCHITECTURE.md                   # Assessment report mapping
│
├── custom_robots_ws/                     # Active multi-package ROS 2 workspace
│   └── src/
│       ├── robot_pkg/                    # Multi-robot URDF lessons, Gazebo & Nav2 pipelines
│       ├── spider_pkg/                   # 18-DOF Hexapod spider with C++ gait node & plugin
│       ├── balancing_robot_description/  # Two-wheeled inverted pendulum self-balancing robot
│       ├── cad_description/              # 4WD rover with 2D LiDAR & depth camera CAD meshes
│       └── drone_pkg/                    # Quadrotor drone model & Gazebo flight world
│
├── gazebo_ws/                            # Custom Gazebo simulation workspace
│   ├── SYSTEM_ARCHITECTURE.md
│   └── src/
│       ├── line_follower_robot/          # Differential drive camera-guided line tracker
│       ├── mobilerobot/                  # 4-wheel mobile base with mapping & RViz configs
│       ├── simple_linefollower_robot/    # Lightweight 2-wheel line follower
│       └── simple_robot_car/             # Minimalist differential drive robot vehicle
│
└── colcon_ws/                            # Supplementary build workspace
```

---

## 2. Package Summary & Capabilities

| Package Name | Embodiment | Key Capabilities | Core Technologies | Status |
|---|---|---|---|---|
| **`spider_pkg`** | 18-DOF Hexapod Spider | C++ tripod/wave gait generator, Gazebo model plugin, 2D LiDAR, SLAM Toolbox mapping | C++, URDF/Xacro, Gazebo Plugin, SLAM | Prototype (72/100) |
| **`drone_pkg`** | Quadrotor Drone | 6-DOF visual mesh, downward/forward cameras, keyboard pose teleop, empty world simulation | URDF/Xacro, Gazebo, Python Teleop | Prototype (68/100) |
| **`cad_description`** | 4WD CAD Rover | High-fidelity CAD STL meshes, differential drive plugin, 2D LiDAR, Depth camera | URDF/Xacro, DAE/STL Meshes, Sensors | Prototype (65/100) |
| **`balancing_robot_description`** | 2-Wheeled Self-Balancer | Inverted pendulum chassis, high-center-of-mass URDF, IMU sensor plugin, differential drive | URDF/Xacro, IMU, Gazebo Plugins | Prototype (62/100) |
| **`robot_pkg`** | Multi-Robot Learning Suite | Progressive URDF exercises, arm models, humanoid torso, Navy mobile manipulator with Nav2 | URDF, Gazebo, Nav2, SLAM Toolbox | Exploratory (56/100) |

---

## 3. Quick Start & Build Instructions

### Prerequisites
- **OS**: Ubuntu 22.04 LTS (or ROS 2 container)
- **ROS 2 Distribution**: ROS 2 Humble Hawksbill / Iron
- **Simulator**: Gazebo Classic (`gazebo_ros_pkgs`)

### Building `custom_robots_ws`
```bash
# Navigate to custom robots workspace
cd "02 — Domains/ROS2/Own_Build/custom_robots_ws"

# Install missing system dependencies
rosdep install --from-paths src --ignore-src -r -y

# Build all packages with symlink install
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

---

## 4. Launch Recipes

### 1. Hexapod Spider Robot (`spider_pkg`)
```bash
# Visualize spider model in RViz
ros2 launch spider_pkg display.launch.py

# Launch Spider in Gazebo with C++ Gait Plugin
ros2 launch spider_pkg spider_launch.launch.py

# Run SLAM Mapping with Spider LiDAR
ros2 launch spider_pkg spider_mapping.launch.py
```

### 2. Quadrotor Drone (`drone_pkg`)
```bash
# Visualize drone model in RViz
ros2 launch drone_pkg display.launch.py

# Launch Drone in Gazebo
ros2 launch drone_pkg gazebo.launch.py
```

### 3. Two-Wheeled Self-Balancing Robot (`balancing_robot_description`)
```bash
# Visualize self-balancing robot in RViz
ros2 launch balancing_robot_description display.launch.py

# Launch Balancer in Gazebo with IMU
ros2 launch balancing_robot_description gazebo.launch.py
```

### 4. 4WD CAD Rover (`cad_description`)
```bash
# Visualize CAD rover in RViz
ros2 launch cad_description display.launch.py

# Launch CAD rover in Gazebo
ros2 launch cad_description gazebo.launch.py
```

### 5. Multi-Robot Learning Package (`robot_pkg`)
```bash
# Launch Navy mobile manipulator simulation
ros2 launch robot_pkg navy_launch.py

# Run Navy SLAM Mapping
ros2 launch robot_pkg navy_mapping_launch.py

# Run Navy Nav2 Autonomous Navigation
ros2 launch robot_pkg navy_nav_launch.py
```

---

## 5. Engineering Assessment Reports

Each custom package in `custom_robots_ws` has undergone a static code review and engineering audit:
- [**Assessment Summary & Score Overview**](ASSESSMENT_REPORTS/README.md)
- [**01: `robot_pkg` Technical Audit**](ASSESSMENT_REPORTS/01_robot_pkg.md) — Score: 56/100
- [**02: `balancing_robot_description` Technical Audit**](ASSESSMENT_REPORTS/02_balancing_robot.md) — Score: 62/100
- [**03: `cad_description` Technical Audit**](ASSESSMENT_REPORTS/03_cad_description.md) — Score: 65/100
- [**04: `drone_pkg` Technical Audit**](ASSESSMENT_REPORTS/04_drone_pkg.md) — Score: 68/100
- [**05: `spider_pkg` Technical Audit**](ASSESSMENT_REPORTS/05_spider_pkg.md) — Score: 72/100

---

## 6. Relationship to Official Product Verticals

These custom packages serve as **experimental and supplementary prototypes** alongside the 5 official learning kits:

| Custom Build | Official Learning Kit Equivalent | Pedagogical Role |
|---|---|---|
| `spider_pkg` | [`ros2_quadruped_kit`](../Ros2%20learning%20kits/ros2_quadruped_kit/README.md) | Hexapod 6-leg wave gait alternative to 4-leg quadruped |
| `drone_pkg` | [`ros2_drone_swarm_kit`](../Ros2%20learning%20kits/ros2_drone_swarm_kit/README.md) | Single quadrotor CAD model & visual testing |
| `cad_description` | [`ros2_mobile_manipulator_kit`](../Ros2%20learning%20kits/ros2_mobile_manipulator_kit/README.md) | Custom 4WD chassis with LiDAR & Camera |
| `balancing_robot_description` | Inverted Pendulum dynamics in [`03_Legged_Locomotion_Series`](../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_04_inverted_pendulum_and_lipm_dynamics.md) | Physical testbed for 2-wheel balance & IMU feedback |
| `robot_pkg` | [`ROS2_kits_ws`](../Ros2%20learning%20kits/ROS2_kits_ws/README.md) | Exploratory URDF and SLAM/Nav2 exercises |
