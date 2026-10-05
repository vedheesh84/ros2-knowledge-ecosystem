# gripper_car_ws - System Architecture

## Package Overview

| Package | Layer | Purpose |
|---------|-------|---------|
| `robot_bringup` | System | Master orchestrator for hardware startup |
| `mobile_manipulator_hardware` | Hardware | Unified Arduino communication bridge |
| `base_controller` | Hardware | Modular base controller (deprecated) |
| `arm_controller` | Hardware | Modular arm controller (deprecated) |
| `mobile_base_description` | Description | 4-wheel differential drive platform |
| `arm_description` | Description | 6-DOF arm with gripper |
| `mobile_manipulator_description` | Description | Combined base + arm assembly |
| `ydlidar_ros2_driver` | Sensors | YDLiDAR hardware driver |
| `lidar_bringup` | Sensors | Launch wrapper for LiDAR |
| `camera_driver` | Sensors | Camera with QR code detection |
| `arm_moveit` | Control | MoveIt2 motion planning |
| `mobile_manipulator_navigation` | Planning | Nav2 + SLAM configuration |
| `pick_and_place` | Application | Pick-place state machine (legacy) |
| `mobile_manipulator_application` | Application | Pick-place state machine (current) |
| `mobile_manipulator_sim` | Simulation | Gazebo simulation |
| `navigation_sim` | Simulation | Nav2 simulation configs |
| `mobile_base_gazebo` | Simulation | Legacy base simulation |

---

## 1. Package-by-Package Analysis

### robot_bringup (System Layer)

**Purpose:** Master orchestrator for hardware startup and composition

**Launch Files:**
| Launch File | Purpose |
|-------------|---------|
| `robot.launch.py` | Basic hardware + LiDAR + RSP |
| `teleop.launch.py` | Keyboard teleoperation |
| `slam.launch.py` | Mapping mode with SLAM Toolbox |
| `navigation.launch.py` | Autonomous navigation with Nav2 |
| `pick_and_place.launch.py` | Complete application stack |
| `test_hardware.launch.py` | Hardware diagnostics |

---

### mobile_manipulator_hardware (Hardware Layer)

**Purpose:** Unified hardware abstraction for Arduino communication

**Node:** `hardware_node` (Python)

**Topics Published:**
| Topic | Type | Rate | Purpose |
|-------|------|------|---------|
| `/joint_states` | JointState | 50Hz | All robot joints (6 arm + 4 wheels + 5 mimic) |
| `/odom` | Odometry | 50Hz | Wheel odometry |
| `/hardware/status` | String | - | Arduino status |

**Topics Subscribed:**
| Topic | Type | Purpose |
|-------|------|---------|
| `/arm/joint_commands` | JointState | Arm position commands from MoveIt |
| `/cmd_vel` | Twist | Base velocity from Nav2/teleop |

**TF Broadcast:** `odom → body_link`

**Key Parameters:**
```yaml
serial_port: /dev/ttyACM0
baud_rate: 115200
wheel_radius: 0.075 m
wheel_base: 0.35 m
encoder_cpr: 360
joint_state_rate: 50 Hz
```

**Data Flow:**
```
MoveIt → /arm/joint_commands → hardware_node → Arduino (serial)
                                            ↓
                                    Servo angle conversion
                                            ↓
                                    /joint_states

Nav2 → /cmd_vel → hardware_node → Arduino motor commands
                           ↓
                    Encoder feedback (ENC)
                           ↓
                    /odom + TF (odom → body_link)
```

---

### mobile_base_description (Description Layer)

**Purpose:** 4-wheel differential drive platform description

**TF Tree:**
```
odom
└── body_link (chassis)
    ├── front_left_link, front_right_link
    ├── back_left_link, back_right_link
    ├── lidar_link
    ├── camera_link
    └── arm_mount_link
```

**Physical Parameters:**
- Chassis: 0.5m × 0.3m × 0.15m, 20 kg
- Wheels: radius 0.075m, width 0.05m, 2.5 kg each
- Wheel base: 0.35m

---

### arm_description (Description Layer)

**Purpose:** 6-DOF arm with gripper mechanical description

**Kinematic Chain:**
```
arm_base_link
├── joint_1 (base rotation: ±π)
│   └── link_1
│       ├── joint_2 (shoulder: ±π/2)
│       │   └── link_2
│       │       ├── joint_3 (elbow: ±π/2)
│       │       │   └── link_3
│       │       │       ├── joint_4 (wrist: ±π/2)
│       │       │       │   └── gripper_base_link
│       │       │       │       ├── left_gear_joint (0 to π/4)
│       │       │       │       └── right_gear_joint (mimic)
```

**Mimic Joints (Gripper):**
- `right_gear_joint`: -1.0 × left_gear_joint
- `left_finger_joint`: 1.0 × left_gear_joint
- `right_finger_joint`: 1.0 × left_gear_joint

---

### arm_moveit (Control Layer)

**Purpose:** MoveIt2 motion planning and IK

**Planning Groups:**
- `arm`: Joints 1-4, gripper_base_joint
- `gripper`: left_gear_joint

**Launch Files:**
- `move_group.launch.py` - Core planning + execution
- `moveit_rviz.launch.py` - Visualization
- `spawn_controllers.launch.py` - Controller manager
- `demo.launch.py` - Demo with fake controllers

**Actions:**
- `/move_group/execute_trajectory` (ExecuteTrajectory)
- `/gripper_controller/gripper_cmd` (GripperCommand)

---

### mobile_manipulator_navigation (Planning Layer)

**Purpose:** Autonomous navigation with SLAM and localization

**Launch Files:**
- `navigation.launch.py` - Nav2 with localization (AMCL)
- `slam_mapping.launch.py` - SLAM Toolbox for mapping

**Nav2 Components:**
- SLAM Toolbox (mapping)
- AMCL (localization)
- Nav2 Controller (DWB)
- Nav2 Planner (Dijkstra/A*)
- Nav2 Behavior Trees

---

### camera_driver (Sensors Layer)

**Purpose:** Camera with QR code detection

**Node:** `qr_scanner.py`

**Topics:**
| Topic | Type | Direction |
|-------|------|-----------|
| `/camera/image_raw` | Image | Subscribe |
| `/qr_scanner/data` | String | Publish |
| `/qr_scanner/detection` | Image | Publish |

---

### pick_and_place (Application Layer)

**Purpose:** Pick-place state machine

**State Machine:**
```
IDLE → GO_PICKUP → PICK_READY → PICKING → SCAN_POSE → SCANNING
    → GO_DROPOFF → PLACING → RETURN → (loop)
    ↕ ERROR/PAUSED (error handling)
```

**Topics:**
| Topic | Type | Direction | Purpose |
|-------|------|-----------|---------|
| `/qr_scanner/data` | String | Subscribe | QR code content |
| `/pick_and_place/command` | String | Subscribe | start/stop/pause |
| `/pick_and_place/state` | String | Publish | Current state |
| `/pick_and_place/status` | String | Publish | Detailed messages |

**Configuration (locations.yaml):**
```yaml
locations:
  pickup:    {x: 0.5, y: 0.0, theta: 0.0}
  station_A: {x: 2.5, y: 2.5, theta: 0.785}
  station_B: {x: 2.5, y: -2.5, theta: -0.785}
  default:   {x: 1.5, y: 1.5, theta: 0.0}
```

---

## 2. System Architecture Analysis

### Control Hierarchy

```
APPLICATION (1-2 Hz)
└── pick_and_place_node
    ├── State machine decisions
    ├── ArmInterface → MoveIt2
    └── NavInterface → Nav2

PLANNING (5-10 Hz)
├── MoveIt2 move_group
│   └── Trajectory generation
└── Nav2 planner_server
    └── Path planning

CONTROL (50 Hz)
├── arm_controller/follow_joint_trajectory
└── Nav2 controller_server (DWB)

HARDWARE (50 Hz)
└── hardware_node
    ├── Serial to Arduino
    ├── Joint state publishing
    └── Odometry computation
```

### Data Flow

```
pick_and_place_node (state machine)
    ├─→ ArmInterface
    │   └→ MoveIt2 → /arm_controller/follow_joint_trajectory
    │       └→ hardware_node → Arduino (servos)
    │
    └─→ NavInterface
        └→ Nav2 NavigateToPose → DWB controller
            └→ /cmd_vel → hardware_node → Arduino (motors)

Sensor Pipeline:
/scan (LiDAR) → SLAM/AMCL → /map, /tf
/camera/image_raw → qr_scanner → /qr_scanner/data → pick_and_place
```

---

## 3. Coordination Patterns

### Action-Based Coordination

```
pick_and_place_node
  ├─ Calls: NavigateToPose action (Nav2)
  ├─ Waits for result
  └─ Proceeds to next state

pick_and_place_node
  ├─ Calls: FollowJointTrajectory action (MoveIt)
  ├─ Waits for result
  └─ Proceeds to next state
```

### Unified Hardware Interface

```
All motion requests → hardware_node
                   ├→ Serial bridge to Arduino
                   ├→ Encoder/odometry processing
                   └→ Joint state publishing
```

---

## 4. Coupling Analysis

### Tight Couplings

| Coupling | Risk |
|----------|------|
| Arduino serial connection | Single point of failure |
| Joint names (URDF ↔ hardware_node) | Name mismatch causes crash |
| Servo angle mapping | Hardcoded in servo_bridge |
| MoveIt group names | Renamed groups break planning |

### Single Points of Failure

| Component | Impact |
|-----------|--------|
| Arduino Serial | Complete system halt |
| hardware_node | Loss of motion and feedback |
| robot_state_publisher | TF tree breaks |

---

## 5. Failure Propagation

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Arduino disconnect | No encoder data | Reconnection logic |
| Joint name mismatch | MoveIt error | Manual fix |
| LiDAR disconnection | No `/scan` | Navigation unavailable |
| Camera failure | QR timeout | Fallback location |
| Map file missing | Nav2 init error | Manual intervention |

---

## 6. Reusability Analysis

### High Reusability

| Component | Reason |
|-----------|--------|
| mobile_base_description | Standard differential drive |
| arm_description | Generic arm kinematics |
| arm_moveit | Standard MoveIt2 config |
| mobile_manipulator_navigation | Standard Nav2 config |

### Low Reusability

| Component | Reason |
|-----------|--------|
| pick_and_place | Hardcoded state machine |
| mobile_manipulator_hardware | Specific serial protocol |
| Location configurations | Application-specific |

---

## 7. Topic Summary

| Topic | Publisher | Subscriber | Type |
|-------|-----------|------------|------|
| `/joint_states` | hardware_node | MoveIt, RSP | JointState |
| `/odom` | hardware_node | Nav2 | Odometry |
| `/cmd_vel` | Nav2/teleop | hardware_node | Twist |
| `/arm/joint_commands` | MoveIt | hardware_node | JointState |
| `/scan` | ydlidar_driver | SLAM, Nav2 | LaserScan |
| `/camera/image_raw` | camera | qr_scanner | Image |
| `/qr_scanner/data` | qr_scanner | pick_and_place | String |
| `/pick_and_place/state` | pick_and_place | Monitor | String |

---

## 8. Parameter Summary

| Node | Key Parameters |
|------|----------------|
| hardware_node | `serial_port`, `baud_rate`, `wheel_radius`, `wheel_base` |
| arm_moveit | Planning groups, IK solver, velocity scaling |
| navigation | `max_vel_x`, `max_vel_theta`, costmap params |
| pick_and_place | Timeouts, retries, place locations |

---

## 9. Integration Complexity Hotspots

| Hotspot | Issue | Mitigation |
|---------|-------|------------|
| Serial communication | USB disconnect | Reconnection logic |
| TF lookup | Missing transform | Static TF publishers |
| IK solver | No solution | Workspace validation |
| Controller timing | Trajectory too fast | Velocity scaling |

---

## 10. Architecture Insights

**Strengths:**
- Clear layered hierarchy
- Unified hardware interface
- Standard ROS2 patterns (MoveIt, Nav2)
- Modular state machine

**Limitations:**
- Single point of failure (Arduino)
- Tight coupling at hardware level
- Hardcoded application logic
- No velocity feedback from arm

**Suitable For:**
- Mobile manipulation research
- Pick-and-place applications
- Educational demonstrations

