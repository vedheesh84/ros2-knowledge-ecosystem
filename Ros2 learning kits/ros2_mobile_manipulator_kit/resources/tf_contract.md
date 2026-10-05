# TF Contract

This document defines the authoritative TF tree for the mobile manipulator.
**This is the source of truth for frame relationships.**

---

## TF Tree Structure

```
                              map
                               │
                         (SLAM/AMCL)
                               │
                              odom
                               │
                           (EKF fuses)
                               │
                           body_link  ←────────── ROBOT ROOT
               ┌───────────────┼───────────────┬───────────────┐
               │               │               │               │
         front_left_wheel  front_right_wheel  arm_mount_link  camera_mount_link
         back_left_wheel   back_right_wheel         │               │
                                                    │               │
                                              arm_base_link    camera_link
                                                    │               │
                                                 link_1       camera_link_optical
                                                    │
                                                 link_2
                                                    │
                                                 link_3
                                                    │
                                                 link_4
                                                    │
                                            gripper_base_link
                                       ┌──────────┴──────────┐
                                       │                     │
                                 left_gear_link        right_gear_link
                                       │                     │
                                left_finger_link      right_finger_link
                                       │
                                  tool_frame  ←───── GRASP REFERENCE
```

---

## Frame Publishers

| Frame | Published By | Rate | Notes |
|-------|-------------|------|-------|
| `map → odom` | SLAM Toolbox / AMCL | 10 Hz | Only when localized |
| `odom → body_link` | robot_localization (EKF) | 50 Hz | Fuses wheel + IMU |
| `body_link → *` (static) | robot_state_publisher | Static | From URDF |
| `body_link → wheels` | robot_state_publisher | 50 Hz | From /joint_states |
| `arm_base_link → tool_frame` | robot_state_publisher | 50 Hz | From /joint_states |

---

## Critical Frames for Each Subsystem

### Navigation
- **Plans in:** `map`
- **Commands in:** `body_link` (via `odom`)
- **Expects:** `map → odom → body_link` chain valid

### Arm Control (MoveIt)
- **Plans in:** `arm_base_link`
- **End effector:** `tool_frame`
- **Expects:** `arm_base_link → tool_frame` chain valid

### Perception
- **Outputs poses in:** `camera_link_optical`
- **Must transform to:** `arm_base_link` for grasping
- **Expects:** `camera_link_optical → arm_base_link` chain valid

### Manipulation State Machine
- **Receives from perception:** `camera_link_optical`
- **Sends to arm control:** `arm_base_link`
- **Coordination frame:** `body_link`

---

## Frame Conventions

### camera_link vs camera_link_optical

```
camera_link (ROS):          camera_link_optical (OpenCV):
    Z (up)                       Y (down)
    │                            │
    │                            │
    └───X (forward)              └───X (right)
       ╱                            ╱
      Y (left)                     Z (forward, into image)
```

**Rule:** Detections from OpenCV are in `camera_link_optical`. Always transform before using.

### tool_frame

- Located at the grasp point between gripper fingers
- Z points along the gripper approach direction
- This is where MoveIt plans end-effector poses

---

## Common TF Errors

| Symptom | Likely Cause | Debug Command |
|---------|--------------|---------------|
| "No transform" | Publisher not running | `ros2 run tf2_tools view_frames` |
| "Transform timeout" | Stale timestamp | `ros2 topic echo /tf --field transforms[0].header.stamp` |
| Arm misses object | camera_link offset wrong | Check camera extrinsics in URDF |
| Object "drifts" | EKF divergence | Check `odom → body_link` stability |

---

## Verification Commands

```bash
# Visualize TF tree
ros2 run tf2_tools view_frames

# Check specific transform
ros2 run tf2_ros tf2_echo arm_base_link tool_frame

# Monitor TF latency
ros2 topic echo /tf --field transforms[0].header.stamp

# List all frames
ros2 run tf2_ros tf2_monitor
```

---

## Contract Rules

1. **robot_state_publisher** owns all static transforms from URDF
2. **EKF** owns `odom → body_link` (not diff_drive_controller)
3. **SLAM/AMCL** owns `map → odom`
4. **Perception outputs** are always in `camera_link_optical`
5. **MoveIt receives** goals in `arm_base_link` frame
6. **Never publish** competing transforms to the same frame pair
