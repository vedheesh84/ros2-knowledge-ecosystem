# Mobile_Manipulator_ws

**Mobile Manipulator Domain Workspace & Physical Deployment Platform**

This workspace contains the complete production-grade physical robot codebase, simulation models, and application pipelines for the autonomous 4WD + 6-DOF mobile manipulator.

---

## 1. Overview & Architectural Role

`Mobile_Manipulator_ws` represents **Vertical 2: Perception $\rightarrow$ Decision $\rightarrow$ Spatial Action** in the Intelligent Ecosystem. It embodies the full convergence of autonomous mobile robotics (AMR) and articulated manipulation into a single unified cyber-physical platform.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MOBILE MANIPULATOR PLATFORM                           │
│                                                                             │
│                   [RGB/Depth Camera]     [2D LiDAR]                         │
│                           │                  │                              │
│                           ▼                  ▼                              │
│                 [Object Perception]     [Nav2 / SLAM]                       │
│                           │                  │                              │
│                           └────────┬─────────┘                              │
│                                    ▼                                        │
│                        [Master State Machine]                               │
│                                    │                                        │
│                           ┌────────┴─────────┐                              │
│                           ▼                  ▼                              │
│                  [Base Controller]   [MoveIt2 Arm Control]                  │
│                     (4WD Drive)        (6-DOF + Gripper)                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Workspace Structure & Packages

The workspace is organized around the physical robot deployment [`gripper_car_ws`](gripper_car_ws/README.md) and connected to the educational [`ros2_mobile_manipulator_kit`](../Ros2%20learning%20kits/ros2_mobile_manipulator_kit/README.md):

```text
Mobile_Manipulator_ws/
├── README.md                            # Primary domain workspace documentation
└── gripper_car_ws/                      # Production robot workspace
    └── src/
        ├── arm/                         # Arm description, controller, and MoveIt2
        ├── mobile_base/                 # Base description, controller, and Gazebo plugin
        ├── mobile_manipulator/          # Combined hardware interface and Nav2 configs
        ├── sensors/                     # Camera driver and YDLiDAR bringup
        ├── applications/
        │   └── pick_and_place/          # QR-routed autonomous pick-and-place application
        ├── simulation/                  # Gazebo worlds and navigation simulation
        └── bringup/
            └── robot_bringup/           # Master system launch files
```

---

## 3. Quick Start & Execution

### 1. Build the Robot Workspace
```bash
cd "02 — Domains/ROS2/Mobile_Manipulator_ws/gripper_car_ws"
colcon build --symlink-install
source install/setup.bash
```

### 2. Full Simulation Bringup
```bash
# Launch full simulation (Gazebo + Base + Arm + MoveIt2 + Sensors)
ros2 launch robot_bringup sim_robot.launch.py
```

### 3. Run Autonomous Pick-and-Place with QR Routing
```bash
# Execute master pick-and-place application with map
ros2 launch robot_bringup pick_and_place.launch.py map:=/path/to/map.yaml
```

---

## 4. Related Learning Material & Kits

- **[Mobile Manipulation & Perception Series (16 Articles)](../ROS2%20Articles/COMPLETE_INDEX.md#vertical-2-mobile-manipulation--perception-series-16-articles):** Master theoretical and systems engineering curriculum.
- **[ros2_mobile_manipulator_kit](../Ros2%20learning%20kits/ros2_mobile_manipulator_kit/README.md):** Progressive 6-demo learning kit and intentional failure breakers.
- **[ros2_arm_kit](../Ros2%20learning%20kits/ros2_arm_kit/README.md):** Prerequisite robotic arm kinematics and MoveIt2 manipulation kit.
- **[turtlebot3_ws](../AMR_ws/turtlebot3_ws/README.md):** Prerequisite AMR and Nav2 navigation foundation.
- **[Kits & Products Strategy](../KITS_AND_PRODUCTS_STRATEGY.md):** Strategic product portfolio architecture.
