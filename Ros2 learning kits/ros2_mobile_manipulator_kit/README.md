# ros2_mobile_manipulator_kit

**Advanced Mobile Manipulator Learning Kit**

A systems learning platform for manipulation + perception.
Not a toy. Not a demo. A teaching tool for real understanding.

---

## What This Kit Is

This is the flagship integration kit in the ROS2 Learning Kit series:

| Kit / Prerequisite | Focus | Core Skills Mastered | Link |
|---|---|---|---|
| **ROS2_kits_ws** | Fundamentals | Lifecycle, topics, services, actions | [README](../ROS2_kits_ws/README.md) |
| **turtlebot3_ws** | AMR Foundation | SLAM, Nav2, EKF, diff_drive control | [README](../../AMR_ws/turtlebot3_ws/README.md) |
| **ros2_arm_kit** | Kinematics Foundation | Analytical FK/IK, MoveIt2, gripper actions | [README](../ros2_arm_kit/README.md) |
| **ros2_mobile_manipulator_kit** | Integrated Perception & Action | Mobile manipulation, vision, coordination FSM | Primary Workspace |

**Prerequisites:** Complete the fundamental kits. This kit assumes you understand:
- Coordinate frame transformations & TF trees ($\text{Camera} \rightarrow \text{Base} \rightarrow \text{Arm}$)
- MoveIt2 planning pipelines and joint trajectory execution
- Nav2 goal navigation and spatial localization
- Launch composition and state machine coordination

---

## What This Kit Is NOT

❌ A complete autonomous system
❌ A production-ready manipulation stack
❌ A deep learning showcase
❌ A Nav2 tutorial (covered in AMR kit)

---

## Core Philosophy

### Manipulation ≠ Motion

Motion planning (MoveIt) is one component.
**Manipulation** is the coordination of:

```
Perception → Decision → Planning → Control → Recovery
   "what"      "why"     "how"     "do"      "oops"
```

This kit teaches the full loop, not just the "how."

### Navigation is Secondary

In this kit, Nav2 exists to get the robot near objects.
The cognitive center is:

1. **Where is the object?** (perception)
2. **Can I reach it?** (arm workspace)
3. **How do I grasp it?** (grasp planning)
4. **What if it fails?** (recovery)

### Failure is Curriculum

The `breakers/` directory contains intentional failure scripts.
Use them. Break things. That's how manipulation becomes real.

---

## Package Architecture

```
ros2_mobile_manipulator_kit/src/
│
├── mobile_manipulator_description/   # TRUTH: What the robot IS
├── mobile_manipulator_hardware/      # INTERFACE: How it talks to reality
├── mobile_manipulator_bringup/       # ORCHESTRATION: How it starts up
├── mobile_manipulator_arm_control/   # PLANNING: How the arm moves
├── mobile_manipulator_perception/    # SENSING: What it sees
├── mobile_manipulator_manipulation/  # COORDINATION: What it decides
└── mobile_manipulator_demos/         # LEARNING: What you practice
```

**Do not merge these packages.** The separation teaches that robotics is systems integration.

---

## Quick Start

```bash
# Build
cd ros2_mobile_manipulator_kit
colcon build --symlink-install
source install/setup.bash

# Visualize robot
ros2 launch mobile_manipulator_description display.launch.py

# Run simulation
ros2 launch mobile_manipulator_bringup simulation.launch.py

# Start with Demo 01
ros2 launch mobile_manipulator_demos demo_01_joint_control.launch.py
```

---

## Demo Progression

| Demo | Focus | What You Learn |
|------|-------|----------------|
| 01 | Joint Control | ros2_control, trajectories |
| 02 | Gripper Control | Actions, stall detection |
| 03 | Camera TF | Frame conventions, transforms |
| 04 | Object Detection | OpenCV, 2D→3D math |
| 05 | Static Pick-Place | Full manipulation loop |
| 06 | Mobile Pick-Place | System integration |

**Do them in order.** Each builds on the previous.

---

## Failure Injection (Breakers)

Run these to understand what breaks and why:

| Breaker | What It Breaks | What You Learn |
|---------|----------------|----------------|
| `break_camera_tf` | TF accuracy | Camera calibration matters |
| `break_grasp_frame` | Grasp pose | Frame conventions matter |
| `break_controller` | Controller state | ros2_control architecture |
| `break_ik` | IK reachability | Workspace limits |
| `break_vision` | Detection quality | Perception robustness |

```bash
# Example: Break camera TF
ros2 run mobile_manipulator_demos break_camera_tf.py --ros-args -p mode:=offset

# Watch grasps fail, then understand why
```

---

## Essential Documentation

Read these before deep-diving:

| Document | Purpose |
|----------|---------|
| [resources/tf_contract.md](resources/tf_contract.md) | Who publishes what TF |
| [resources/moveit_mental_model.md](resources/moveit_mental_model.md) | Why MoveIt fails |
| [resources/perception_assumptions.md](resources/perception_assumptions.md) | 2D→3D truth |

---

## ros2_control Architecture

This kit uses multiple controllers for different subsystems:

```
                    controller_manager
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   diff_drive         arm_controller     gripper_controller
   (velocity)          (position)          (position)
        │                  │                  │
        ▼                  ▼                  ▼
    4 wheels           5 arm joints        1 gripper joint
```

**Key insight:** Different subsystems need different control semantics.

---

## What NOT to Add

This kit is complete at its current scope. Resist adding:

- ❌ Deep learning detection
- ❌ Complex grasp synthesis
- ❌ Dynamic obstacle avoidance
- ❌ Multi-arm coordination
- ❌ Full Nav2 autonomy

More would reduce clarity without improving understanding.

---

## Troubleshooting

### "No IK solution"
→ Check if pose is in arm workspace
→ See [resources/moveit_mental_model.md](resources/moveit_mental_model.md)

### "TF timeout"
→ Run `ros2 run tf2_tools view_frames`
→ See [resources/tf_contract.md](resources/tf_contract.md)

### "Arm misses object"
→ Check camera_link_optical transform
→ See [resources/perception_assumptions.md](resources/perception_assumptions.md)

### "Controller not active"
→ Run `ros2 control list_controllers`
→ Check TimerAction delays in launch files

---

## Learning Path & Master Curriculum (16 Articles)

This kit is accompanied by the comprehensive 16-article **[Mobile Manipulation & Perception Series](../../ROS2%20Articles/COMPLETE_INDEX.md#vertical-2-mobile-manipulation--perception-series-16-articles)**:

- **Module 1 (Systems & Hardware)**: [Systems Architecture & Coupling (MM 01)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_01_systems_architecture_and_coupling.md) | [Distributed Hardware Topology (MM 02)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_02_distributed_hardware_topology.md)
- **Module 2 (Spatial Chains & Calibration)**: [Unified Kinematic Chains & TF (MM 03)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_03_unified_kinematic_chains_and_tf.md) | [Hand-Eye Calibration AX=XB (MM 04)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_04_hand_eye_calibration_eye_in_hand_vs_base.md) | [Dynamic Frame Drift & Visual Servoing (MM 05)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_05_dynamic_frame_drift_and_visual_servoing.md)
- **Module 3 (Robot Vision & 3D PnP)**: [Pinhole Camera Models (MM 06)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_06_pinhole_camera_models_and_intrinsics.md) | [2D Object Detection & ArUco (MM 07)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_07_2d_object_detection_hsv_and_aruco.md) | [3D Pose Estimation & PnP (MM 08)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_08_3d_pose_estimation_and_pnp.md)
- **Module 4 (Reachability & Docking)**: [Reachability Envelopes & Docking (MM 09)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_09_mobile_reachability_and_docking.md) | [Nav2 Costmaps & Footprint Inflation (MM 10)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_10_nav2_costmaps_for_mobile_manipulators.md) | [Closed-Loop Base Docking (MM 11)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_11_closed_loop_visual_servoing_base_alignment.md)
- **Module 5 (Behavior Trees & Recovery)**: [Supervisory Orchestration: FSM vs. BT (MM 12)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_12_supervisory_orchestration_fsm_vs_trees.md) | [Behavior Tree Design (MM 13)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_13_behavior_tree_design_for_mobile_pick_place.md) | [Dynamic Fault Recovery (MM 14)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_14_dynamic_error_recovery_and_resilience.md)
- **Module 6 (Physical Deployment Case Study)**: [Physical Gripper Car Case Study (MM 15)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_15_production_case_study_gripper_car_ws.md) | [Real-World Challenges & Debugging (MM 16)](../../ROS2%20Articles/02_Mobile_Manipulator_Series/article_mm_16_real_world_physical_challenges_and_debugging.md)

---

## Contributing

This is a learning kit. Contributions should:
- Clarify, not complexify
- Add failure modes, not features
- Document assumptions, not hide them

---

## License

MIT License. Use it. Teach with it. Break it. Fix it.
