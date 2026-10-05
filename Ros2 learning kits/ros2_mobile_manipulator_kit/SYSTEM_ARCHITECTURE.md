# ros2_mobile_manipulator_kit - System Architecture

## Package Overview

| Package | Layer | Purpose |
|---------|-------|---------|
| `mobile_manipulator_description` | System | URDF/Xacro, TF tree, hardware config |
| `mobile_manipulator_hardware` | Hardware | C++ ros2_control plugins for base + arm |
| `mobile_manipulator_bringup` | System | Launch orchestration |
| `mobile_manipulator_arm_control` | Planning | MoveIt2 integration, motion planning |
| `mobile_manipulator_perception` | Perception | Object detection, pose estimation |
| `mobile_manipulator_manipulation` | Application | Pick-place state machine |
| `mobile_manipulator_demos` | Application | Progressive demos + failure injection |

---

## 1. Package-by-Package Analysis

### mobile_manipulator_description (System Layer)

**Purpose:** Robot structure, kinematics, hardware interfaces

**TF Tree:**
```
odom
└── body_link (mobile base)
    ├── front_left_wheel, front_right_wheel
    ├── back_left_wheel, back_right_wheel
    ├── camera_mount_link → camera_link → camera_optical_link
    ├── laser_frame (LiDAR)
    └── arm_mount_link → arm_base_link
        ├── joint_1 → link_1 (base rotation)
        ├── joint_2 → link_2 (shoulder pitch)
        ├── joint_3 → link_3 (elbow pitch)
        ├── joint_4 → link_4 (wrist pitch)
        ├── gripper_base_joint → gripper_base_link
        ├── left_gear_joint → left_finger_link
        ├── right_gear_joint → right_finger_link (MIMIC)
        └── tool_joint → tool_frame (grasp point)
```

**Hardware Systems (Two Independent):**

```yaml
base_system:
  Plugin: BaseHardwareInterface
  Serial: /dev/ttyACM0
  Joints: 4 wheels (velocity control)
  Protocol: "VEL,<left>,<right>\n" / "ENC,<fl>,<fr>,<bl>,<br>\n"

arm_system:
  Plugin: ArmHardwareInterface
  Serial: /dev/ttyACM1
  Joints: 5 arm + 1 gripper (position control)
  Protocol: "SET_ALL_SERVOS,..." / "SERVO_POS,..."
```

**Controllers:**
- `joint_state_broadcaster` - All joint states
- `diff_drive_controller` - Base motion
- `arm_controller` - 5-DOF arm trajectory
- `gripper_controller` - Gripper position

---

### mobile_manipulator_arm_control (Planning Layer)

**Purpose:** MoveIt2 integration for motion planning

**SRDF Planning Groups:**
```yaml
arm:
  Joints: [joint_1, joint_2, joint_3, joint_4, gripper_base_joint]
  Purpose: 5-DOF manipulation planning

gripper:
  Joints: [left_gear_joint]
  Purpose: Gripper control
```

**Named Poses:**
| Pose | Joint Values | Purpose |
|------|--------------|---------|
| home | [0, 0, 0, 0, 0] | All zeros |
| ready | [0, 0.5, 0.7, 0.4, 0] | Pre-grasp |
| extended | [0, 0.3, 0, 0, 0] | Maximum reach |
| open | [0.8] | Gripper open |
| closed | [0.0] | Gripper closed |

**Kinematics:**
```yaml
solver: KDLKinematicsPlugin
search_resolution: 0.005 rad
timeout: 0.5 sec
```

**ArmInterface API:**
```python
go_to_named_pose(name)      # Move to SRDF pose
go_to_joint_values(angles)  # Direct joint control
go_to_pose(x, y, z, ...)    # Cartesian IK
open_gripper() / close_gripper()
stop()                       # Emergency stop
```

---

### mobile_manipulator_perception (Perception Layer)

**Purpose:** Object detection and 3D pose estimation

**Object Detection Pipeline:**
```
/camera/image_raw (BGR)
        ↓
Convert BGR → HSV
        ↓
Morphological operations (denoise)
        ↓
Find contours matching color
        ↓
Filter by area
        ↓
Detection (center_x, center_y, width, height)
```

**Color Ranges (HSV):**
```yaml
red:    H=[0-10, 160-180], S>100, V>100
green:  H=[35-85], S>100, V>100
blue:   H=[100-130], S>100, V>100
yellow: H=[20-35], S>100, V>100
```

**Pose Estimation (Pinhole Model):**
```
Depth: Z = (known_width * fx) / pixel_width
X = (u - cx) * Z / fx
Y = (v - cy) * Z / fy
```

**perception_node:**
| Topic | Direction | Type | Purpose |
|-------|-----------|------|---------|
| `/camera/image_raw` | Sub | Image | Input |
| `/camera/camera_info` | Sub | CameraInfo | Calibration |
| `/perception/detections` | Pub | Image | Visualization |
| `/perception/object_pose` | Pub | PoseStamped | 3D position |

**Parameters:**
```yaml
target_color: "red"
object_width: 0.05 m
detection_rate: 10.0 Hz
target_frame: "arm_base_link"
```

---

### mobile_manipulator_manipulation (Application Layer)

**Purpose:** Pick-place state machine

**State Machine:**
```
IDLE → DETECTING → PRE_GRASP → GRASPING → POST_GRASP
                                              ↓
         IDLE ← RETRACTING ← PLACING ← PRE_PLACE ← TRANSPORTING
```

**State Details:**
| State | Action | Transition |
|-------|--------|-----------|
| IDLE | Wait for command | "start" → DETECTING |
| DETECTING | Call perception | Object found → PRE_GRASP |
| PRE_GRASP | Move above object | Reached → GRASPING |
| GRASPING | Move down, close gripper | Grasped → POST_GRASP |
| POST_GRASP | Lift object | Lifted → TRANSPORTING |
| TRANSPORTING | Move to place | Reached → PRE_PLACE |
| PRE_PLACE | Approach place pose | Reached → PLACING |
| PLACING | Open gripper | Released → RETRACTING |
| RETRACTING | Lift away | Done → IDLE |

**Grasp Planning:**
```python
plan_top_down_grasp(x, y, z)  # Approach from above
plan_side_grasp(x, y, z)      # Horizontal approach
compute_pre_grasp(grasp)      # Offset above target
compute_post_grasp(grasp)     # Lift position
```

**Configuration:**
```yaml
tick_rate: 10.0 Hz
detection_timeout: 15.0 s
motion_timeout: 10.0 s
gripper_timeout: 2.0 s
place_x: 0.25 m
place_y: 0.15 m
place_z: 0.05 m
```

---

## 2. System Architecture Analysis

### Data Flow Diagram

```
CAMERA
└── /camera/image_raw, /camera/camera_info
        ↓
PERCEPTION NODE
├── Color detection (HSV)
├── Pose estimation (pinhole)
├── TF transform to arm_base_link
└── /perception/object_pose
        ↓
MANIPULATION NODE
├── State machine logic
├── Grasp planning
└── Motion commands
        ↓
ARM INTERFACE
├── MoveIt planning
├── IK computation
└── /arm_controller/follow_joint_trajectory
        ↓
ARM CONTROLLER (ros2_control)
└── ArmHardwareInterface → Servos
```

### Control Loop Hierarchy

```
manipulation_node (10 Hz)
    ↓ State machine decisions
ArmInterface.go_to_pose()
    ↓ Planning request
MoveIt move_group
    ↓ Trajectory generation
/arm_controller/follow_joint_trajectory
    ↓ Trajectory execution
arm_controller (100 Hz)
    ↓ Setpoint tracking
ArmHardwareInterface.write()
    ↓ Serial commands
Arduino → Servos
```

---

## 3. Coordination Patterns

### Controller Coordination

```
Controller Manager
├── joint_state_broadcaster (reads all joints)
├── diff_drive_controller (claims wheel velocity)
├── arm_controller (claims arm position)
└── gripper_controller (claims gripper position)

No conflicts: Each controller claims exclusive interfaces
```

### Hardware/Simulation Switching

```yaml
sim_mode=true:
  - URDF loads gazebo.urdf.xacro
  - Gazebo physics + gazebo_ros2_control

sim_mode=false:
  - URDF loads ros2_control.urdf.xacro
  - BaseHardwareInterface + ArmHardwareInterface
```

### Launch Sequencing

```
Hardware Mode:
t=0s:  robot_state_publisher
t=0s:  controller_manager (loads plugins)
t=2s:  joint_state_broadcaster
t=4s:  diff_drive, arm, gripper controllers
t=6s:  RViz

Simulation Mode:
t=0s:  robot_state_publisher
t=2s:  Gazebo
t=5s:  spawn_entity
t=8s:  Controllers via gazebo_ros2_control
```

---

## 4. Agent-Based Analysis

### What Each Component Knows

| Component | Local Knowledge | Global Knowledge |
|-----------|-----------------|------------------|
| Perception | Color detection, pinhole math | None |
| ArmInterface | MoveIt API, joint names | None |
| Manipulation | State machine, grasp planning | Aggregate state |
| Hardware Interface | Serial protocol | None |

### What Each Component Assumes

| Component | Assumptions |
|-----------|-------------|
| Perception | Camera calibrated, object width known |
| ArmInterface | MoveIt running, controllers active |
| Manipulation | Perception provides valid poses |
| Grasp Planner | Workspace bounds valid |

### Local vs Delegated Decisions

| Component | Local Decisions | Delegated To |
|-----------|-----------------|--------------|
| Perception | Color matching, pose estimation | Frame transform |
| Manipulation | State transitions, grasp type | Motion execution |
| ArmInterface | None (wrapper) | MoveIt planning |
| MoveIt | Trajectory planning | Controller execution |

---

## 5. Coupling Analysis

### Tight Coupling

| Coupling | Risk |
|----------|------|
| arm_controller ↔ ArmHardwareInterface | Serial loss = arm freeze |
| Perception ↔ Camera | No camera = no detection |
| Manipulation ↔ Perception | Detection timeout = stuck |

### Medium Coupling

| Coupling | Decoupling Strategy |
|----------|---------------------|
| Manipulation ↔ ArmInterface | Could use direct action client |
| Perception ↔ TF | Could publish in camera frame |

### Loose Coupling

| Component | Why Loose |
|-----------|-----------|
| Color detection | Parameterized colors |
| Place location | YAML configuration |
| Grasp type | Modular grasp planner |

---

## 6. Reusability Analysis

### Highly Reusable

| Component | Reason |
|-----------|--------|
| MoveIt2 configuration | Standard patterns |
| Perception framework | Generic CV pipeline |
| State machine structure | Task-agnostic |
| Launch patterns | Sequential startup |

### Robot-Specific

| Component | Reason |
|-----------|--------|
| URDF dimensions | Physical robot |
| Serial protocols | Hardware-specific |
| Kinematics | Arm geometry |
| Grasp workspace | Arm reach limits |

---

## 7. Topic Summary

| Topic | Publisher | Subscriber | Type |
|-------|-----------|------------|------|
| `/camera/image_raw` | Camera | Perception | Image |
| `/camera/camera_info` | Camera | Perception | CameraInfo |
| `/perception/object_pose` | Perception | Manipulation | PoseStamped |
| `/manipulation/state` | Manipulation | Monitor | String |
| `/manipulation/command` | User | Manipulation | String |
| `/joint_states` | joint_state_broadcaster | All | JointState |
| `/cmd_vel` | Nav/Teleop | diff_drive | Twist |

---

## 8. Parameter Summary

| Node | Key Parameters |
|------|----------------|
| Perception | `target_color`, `object_width`, `detection_rate`, `target_frame` |
| Manipulation | `tick_rate`, timeouts, `place_x/y/z`, `max_retries` |
| Arm Controller | Joint velocity limits, goal tolerances |
| Gripper Controller | `goal_tolerance`, `max_effort`, `stall_threshold` |
| diff_drive | Velocity limits, `enable_odom_tf: false` |

---

## 9. Integration Complexity Hotspots

| Hotspot | Issue | Mitigation |
|---------|-------|------------|
| Serial communication | USB disconnect | Reconnection logic |
| TF lookup | Missing transform | Static TF publishers |
| IK solver | No solution | Workspace validation |
| Controller timing | Trajectory too fast | Velocity scaling |
| Perception frame | Calibration drift | Regular calibration |

---

## 10. Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| No velocity feedback from arm | Can't detect stalling | Timeout + retry |
| Position-only control | No force control | Gripper stall detection |
| 5-DOF arm | Limited workspace | Careful placement |
| Classical CV | Known objects only | Tuned colors |
| 10 Hz perception | Slow detection | Faster hardware |
