## MM 15: PHYSICAL ROBOT CASE STUDY: THE 4WD + 6-DOF GRIPPER CAR

*Purpose: Deep dive into the physical production deployment of the autonomous mobile manipulator (`gripper_car_ws`). Analyze real hardware schematics, Arduino Mega firmware, PCA9685 servo integration, YDLiDAR X2L bringup, Raspberry Pi Camera V2, and QR-routed autonomous pick-and-place.*

### Must Answer
- What is the physical embodiment of the 4WD + 6-DOF Gripper Car in `Mobile_Manipulator_ws`?
- How is the Arduino Mega firmware structured to handle 4 DC encoder motors and 6 analog servos concurrently?
- How does the YDLiDAR X2L driver publish `/scan` for Cartographer 2D SLAM and Nav2 navigation?
- How does the Raspberry Pi Camera V2 capture video streams and extract QR routing metadata?
- How does the QR-routed pick-and-place application direct the robot across multiple stations?

### Key Insight
The physical `gripper_car_ws` platform transforms theoretical ROS2 code into physical reality, where real DC motor current, sensor noise, and mechanical friction interact in real time.

---

### 1. Physical Hardware Embodiment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      4WD + 6-DOF GRIPPER CAR HARDWARE                       │
│                                                                             │
│   [Chassis]  ──▶ 4WD Aluminum Chassis with 4x TT Geared DC Motors           │
│   [Arm]      ──▶ 6-DOF Articulated Metallic Arm (MG996R / SG90 Servos)      │
│   [Sensors]  ──▶ YDLiDAR X2L 360 Laser + Raspberry Pi Camera V2             │
│   [Compute]  ──▶ Raspberry Pi 4 (8GB RAM / Ubuntu Linux + ROS2)             │
│   [MCU]      ──▶ Arduino Mega 2560 (Real-Time Motor/Encoder Bridge)         │
│   [Drivers]  ──▶ PCA9685 16-Ch PWM Driver + L298N Dual H-Bridge             │
│   [Power]    ──▶ Dual 3S LiPo Batteries with Isolated UBEC Regulators       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Workspace Package Architecture (`gripper_car_ws`)

```text
gripper_car_ws/src/
├── mobile_base/              # 4WD base URDF, diff_drive controllers, and Gazebo plugin
├── arm/                      # 6-DOF arm URDF, joint limit configs, and MoveIt2 pipeline
├── mobile_manipulator/       # Unified base + arm hardware interfaces and Nav2 configs
├── sensors/                  # YDLiDAR X2L driver and Pi Camera V2 video capture node
├── applications/
│   └── pick_and_place/       # QR-routed autonomous warehouse pick-and-place logic
├── simulation/               # Gazebo worlds, obstacle tracks, and visual models
└── bringup/
    └── robot_bringup/        # Master hardware launch files (sim_robot, real_robot)
```

---

### 3. QR-Routed Warehouse Workflow

1. The robot patrols between warehouse stations using **Nav2**.
2. At Station A, the camera scans a **QR code** on a storage bin:
   - QR Payload: `{"item": "PART_402", "dest": "STATION_C", "shelf_z": 0.08}`.
3. The application parses the JSON destination, aligns the base, executes the grasp, verifies payload retention, and navigates autonomously to Station C.

---

### 4. Hands-On Lab & Practical Code References

#### 1. Building and Launching the Physical Robot Workspace:
```bash
# Build gripper_car_ws
cd "02 — Domains/ROS2/Mobile_Manipulator_ws/gripper_car_ws"
colcon build --symlink-install
source install/setup.bash

# Launch full simulation
ros2 launch robot_bringup sim_robot.launch.py

# Launch autonomous pick-and-place application
ros2 launch robot_bringup pick_and_place.launch.py map:=/path/to/map.yaml
```
- Workspace README: [`02 — Domains/ROS2/Mobile_Manipulator_ws/gripper_car_ws/README.md`](file:///e:/Intelligent%20Systems%20Knowledge%20Ecosystem/02%20—%20Domains/ROS2/Mobile_Manipulator_ws/gripper_car_ws/README.md)
