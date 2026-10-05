# mobile_manipulator_application

High-level application coordinator for pick-and-place manipulation tasks with QR code detection integration. Manages state machine transitions and arm/gripper control.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Nodes](#nodes)
- [Launch Files](#launch-files)
- [Configuration](#configuration)
- [Usage](#usage)
- [State Machine](#state-machine)
- [Troubleshooting](#troubleshooting)

---

## Overview

This package provides the application-level logic for autonomous pick-and-place operations. It coordinates:

- **State Machine** for sequencing pick-and-place operations
- **QR Code Detection** integration for target identification
- **Arm Control** via joint trajectory commands
- **Gripper Control** for object manipulation

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     pick_and_place_node                              │
│                                                                      │
│  ┌──────────────┐                           ┌──────────────┐        │
│  │   State      │◀── /qr_scanner/data ──────│  QR Scanner  │        │
│  │   Machine    │                           │   (camera)   │        │
│  └──────┬───────┘                           └──────────────┘        │
│         │                                                            │
│         │ /arm/joint_commands                                        │
│         ▼                                                            │
│  ┌──────────────┐                           ┌──────────────┐        │
│  │     Arm      │◀── /joint_states ─────────│   MoveIt2    │        │
│  │   Control    │                           │  (feedback)  │        │
│  └──────────────┘                           └──────────────┘        │
│                                                                      │
│  States: IDLE → SEARCHING → APPROACHING → PICKING → PLACING         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Package Structure

```
mobile_manipulator_application/
├── CMakeLists.txt
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── mobile_manipulator_application
├── launch/
│   └── pick_and_place.launch.py
├── config/
│   └── pick_and_place_params.yaml
└── mobile_manipulator_application/
    ├── __init__.py
    └── pick_and_place_node.py
```

---

## Nodes

### pick_and_place_node

Main application coordinator implementing a state machine for pick-and-place operations.

#### Topics

**Subscribed:**

| Topic | Type | Description |
|-------|------|-------------|
| `/qr_scanner/data` | `std_msgs/String` | Detected QR code data |
| `/joint_states` | `sensor_msgs/JointState` | Current arm joint positions |

**Published:**

| Topic | Type | Description |
|-------|------|-------------|
| `/arm/joint_commands` | `trajectory_msgs/JointTrajectoryPoint` | Arm command trajectory |
| `/pick_and_place/status` | `std_msgs/String` | Current state machine status |

#### Services

| Service | Type | Description |
|---------|------|-------------|
| `/pick_and_place/start` | `std_srvs/Trigger` | Start pick-and-place sequence |
| `/pick_and_place/stop` | `std_srvs/Trigger` | Stop and return to home position |

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `arm_joints` | `list` | See config | List of arm joint names |
| `motion_time` | `float` | `2.0` | Arm motion duration (seconds) |
| `gripper_time` | `float` | `1.0` | Gripper open/close duration |
| `gripper_open` | `float` | `0.5` | Gripper open position (radians) |
| `gripper_closed` | `float` | `0.0` | Gripper closed position (radians) |

---

## Launch Files

### pick_and_place.launch.py

Launches the pick-and-place application node.

```bash
ros2 launch mobile_manipulator_application pick_and_place.launch.py
```

**Note:** This launch file is typically included by `robot_bringup/pick_and_place.launch.py` for full system integration.

---

## Configuration

### pick_and_place_params.yaml

```yaml
pick_and_place_node:
  ros__parameters:
    arm_joints:
      - joint_1
      - joint_2
      - joint_3
      - joint_4
      - gripper_base_joint
      - left_gear_joint
    motion_time: 2.0        # Arm motion duration (seconds)
    gripper_time: 1.0       # Gripper operation duration
    gripper_open: 0.5       # Open position (radians)
    gripper_closed: 0.0     # Closed position (radians)
```

---

## Usage

### Start Pick-and-Place Sequence

```bash
# Launch the full robot system first
ros2 launch robot_bringup robot.launch.py

# In another terminal, start the application
ros2 launch mobile_manipulator_application pick_and_place.launch.py

# Trigger the sequence
ros2 service call /pick_and_place/start std_srvs/srv/Trigger
```

### Monitor State Machine

```bash
# Watch current state
ros2 topic echo /pick_and_place/status

# Monitor arm commands
ros2 topic echo /arm/joint_commands
```

### Stop Sequence

```bash
ros2 service call /pick_and_place/stop std_srvs/srv/Trigger
```

---

## State Machine

The node implements a 6-state finite state machine:

```
                    ┌───────────┐
                    │   IDLE    │◀──────────────────┐
                    └─────┬─────┘                   │
                          │ start service           │
                          ▼                         │
                    ┌───────────┐                   │
            ┌──────▶│ SEARCHING │──────┐            │
            │       └───────────┘      │            │
            │             │            │ timeout    │
            │             │ QR found   │            │
            │             ▼            │            │
            │       ┌───────────┐      │            │
            │       │APPROACHING│◀─────┘            │
            │       └─────┬─────┘                   │
            │             │ at position             │
            │             ▼                         │
            │       ┌───────────┐                   │
            │       │  PICKING  │                   │
            │       └─────┬─────┘                   │
            │             │ object grasped          │
            │             ▼                         │
            │       ┌───────────┐                   │
            │       │  PLACING  │                   │
            │       └─────┬─────┘                   │
            │             │ object placed           │
            │             ▼                         │
            │       ┌───────────┐                   │
            └───────│ RETURNING │───────────────────┘
                    └───────────┘
```

### State Descriptions

| State | Description | Exit Condition |
|-------|-------------|----------------|
| **IDLE** | Waiting for start command | `/pick_and_place/start` called |
| **SEARCHING** | Moves to search pose, monitors QR | Target QR detected |
| **APPROACHING** | Positions for picking | At pre-pick position |
| **PICKING** | Opens gripper → moves → closes → lifts | Object grasped |
| **PLACING** | Moves to place → opens → retracts | Object released |
| **RETURNING** | Returns to home position | At home position |

### Predefined Poses

The node uses predefined joint configurations:

| Pose | Description |
|------|-------------|
| `home` | Safe resting position |
| `search` | Camera pointing at work area |
| `pre_pick` | Position above target object |
| `pick` | Lowered to grasp object |
| `carry` | Carrying position (object secured) |
| `pre_place` | Position above drop location |
| `place` | Lowered to release object |

---

## Troubleshooting

### State machine stuck in SEARCHING

```bash
# Check QR scanner is publishing
ros2 topic echo /qr_scanner/data

# Verify camera is running
ros2 topic hz /camera/image_raw
```

### Arm not moving

```bash
# Check joint commands are being published
ros2 topic echo /arm/joint_commands

# Verify arm controller is running
ros2 control list_controllers | grep arm
```

### Gripper not responding

```bash
# Check gripper joint in joint_states
ros2 topic echo /joint_states | grep gripper

# Verify gripper parameters
ros2 param get /pick_and_place_node gripper_open
```

### Service calls failing

```bash
# List available services
ros2 service list | grep pick_and_place

# Check node is running
ros2 node list | grep pick_and_place
```

---

## Dependencies

- `rclpy`
- `std_msgs`, `geometry_msgs`, `sensor_msgs`
- `trajectory_msgs`, `moveit_msgs`, `nav2_msgs`
- `tf2_ros`, `tf2_geometry_msgs`

---

## Related Packages

- [pick_and_place](../../applications/pick_and_place/README.md) - Application configuration
- [arm_controller](../../arm/arm_controller/README.md) - Arm hardware interface
- [camera_driver](../../sensors/camera_driver/README.md) - QR code detection
