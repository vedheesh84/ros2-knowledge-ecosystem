# ros2_quadruped_kit

**Advanced Quadruped Learning Kit**

A systems learning platform for legged locomotion, dynamic balance, and Model Predictive Control.
Not a toy. Not a demo. A teaching tool for real understanding.

---

## What This Kit Is

This is the embodied locomotion kit in the ROS2 Learning Kit series:

| Kit / Prerequisite | Focus | Core Skills Mastered | Link |
|---|---|---|---|
| **ROS2_kits_ws** | Fundamentals | Lifecycle, topics, services, actions | [README](../ROS2_kits_ws/README.md) |
| **turtlebot3_ws** | AMR Foundation | SLAM, Nav2, EKF state estimation | [README](../../AMR_ws/turtlebot3_ws/README.md) |
| **ros2_arm_kit** | Kinematics Foundation | Analytical FK/IK, trajectory generation | [README](../ros2_arm_kit/README.md) |
| **ros2_mobile_manipulator_kit** | Systems Integration | Coordinated perception & manipulation | [README](../ros2_mobile_manipulator_kit/README.md) |
| **ros2_quadruped_kit** | Legged Locomotion | MPC, gaits, floating-base balance | Primary Workspace |

**Prerequisites:** Complete the fundamental kits. This kit assumes you understand:
- Analytical leg inverse kinematics and Jacobians
- Floating-base state estimation (EKF + IMU fusion)
- Control theory basics (Joint PD and Ground Reaction Force distribution)
- Contact state scheduling (stance vs. swing phases)

---

## Quadruped & Hexapod Unified Architecture

> [!NOTE]
> **Quadrupeds (4 legs) and Hexapods (6 legs) share identical 3-DOF leg kinematics.**
> Each leg consists of a Hip Abduction/Adduction joint ($q_1$), Hip Pitch joint ($q_2$), and Knee Pitch joint ($q_3$). The analytical leg solver and Bézier swing trajectory generator in `quadruped_locomotion` apply directly to both 4-legged (diagonal trot / crawl) and 6-legged (alternating tripod / wave) embodiments.

---

## What This Kit Is NOT

- A production locomotion stack
- A deep learning showcase
- A complete autonomy system
- A replacement for Spot SDK

---

## Core Philosophy

### Legged Robots Are Different

Wheeled robots stay on the ground. Quadrupeds **float in 3D space**.

This means:
- No wheel encoders for odometry (must estimate velocity)
- Contact state changes (feet lift/land)
- Dynamic balance (can fall over)
- Higher control bandwidth (ms-level loops)

### The Control Hierarchy

```
Behavior Layer (10 Hz)     "Walk to the kitchen"
       │
       ▼
Locomotion Layer (100 Hz)  "MPC: compute GRF for next 0.3s"
       │
       ▼
Whole-Body Control (500 Hz) "Convert forces to joint torques"
       │
       ▼
Joint Control (1000 Hz)    "PD control with feedforward"
       │
       ▼
Hardware (motor drivers)
```

Each layer has different physics and different timescales.

---

## Package Architecture

```
ros2_quadruped_kit/src/
│
├── quadruped_description/    # TRUTH: What the robot IS (URDF, ros2_control)
├── quadruped_hardware/       # INTERFACE: C++ hardware plugins
├── quadruped_bringup/        # ORCHESTRATION: Launch files
├── quadruped_estimation/     # STATE: Floating-base EKF, contact detection
├── quadruped_locomotion/     # MOTION: Gait scheduler, MPC, swing trajectories
├── quadruped_control/        # EXECUTION: Whole-body control, joint PD
├── quadruped_perception/     # SENSING: Terrain mapping
├── quadruped_behaviors/      # DECISIONS: Behavior state machine
└── quadruped_demos/          # LEARNING: 7 demos + failure injection
```

---

## Quick Start

```bash
# Build
cd ros2_quadruped_kit
colcon build --symlink-install
source install/setup.bash

# Visualize robot (no physics)
ros2 launch quadruped_description display.launch.py

# Run with mock hardware
ros2 launch quadruped_bringup hardware.launch.py use_fake_hardware:=true

# Start with Demo 01
ros2 run quadruped_demos demo_01_joint_control
```

---

## Demo Progression

| Demo | Focus | What You Learn |
|------|-------|----------------|
| 01 | Joint Control | Effort interfaces, joint limits |
| 02 | Leg Kinematics | FK/IK, Jacobians |
| 03 | Standing | Static balance, CoM |
| 04 | Weight Shifting | Dynamic balance while standing |
| 05 | Walking | Walk gait (1 leg at a time) |
| 06 | Trotting | Trot gait (diagonal pairs) |
| 07 | Disturbance | Push recovery |

**Do them in order.** Each builds on the previous.

---

## Key Concepts

### Gait Patterns

```
WALK:   FL ── FR ── RL ── RR ──     (one at a time)
        █░░░ █░░░ █░░░ █░░░

TROT:   FL+RR ───── FR+RL ─────     (diagonal pairs)
        █░░░░░░░░░ █░░░░░░░░░

BOUND:  FL+FR ───── RL+RR ─────     (front then rear)
        █░░░░░░░░░ █░░░░░░░░░
```

### Model Predictive Control (MPC)

MPC predicts the future and optimizes:

```
Now ──> Predict 0.3s ──> Optimize forces ──> Apply first, discard rest ──> Repeat
```

Outputs **ground reaction forces**, not joint positions.

### Contact Detection

When a foot is in contact:
- It can push against ground (apply GRF)
- Velocity should be zero (kinematics constraint)
- Stance phase active (support robot weight)

---

## Failure Injection (Breakers)

| Breaker | What It Breaks | What You Learn |
|---------|----------------|----------------|
| `break_imu` | IMU noise/bias | State estimation sensitivity |
| `break_contact` | Contact detection | Gait phase importance |
| `break_gait` | Gait timing | Phase coordination |

```bash
# Example: Break IMU with noise
ros2 run quadruped_demos break_imu --ros-args -p mode:=noise
```

---

## TF Tree

```
         base_link (floating)
              │
   ┌──────────┼──────────┐
   │          │          │
 FL_hip    imu_link   FR_hip
   │          │          │
 FL_thigh  camera_link FR_thigh
   │                     │
 FL_calf              FR_calf
   │                     │
 FL_foot              FR_foot
```

**Key insight:** `base_link` is a **floating frame** - not fixed to world.

---

## ros2_control Architecture

```yaml
controller_manager:
  update_rate: 1000  # High rate for legged robots

leg_controller:
  type: effort_controllers/JointGroupEffortController
  joints: [FL_HAA, FL_HFE, FL_KFE, ...]  # 12 joints

imu_broadcaster:
  type: imu_sensor_broadcaster/IMUSensorBroadcaster
```

**Why effort control?**
- Position control is too stiff
- Need compliant contact
- MPC outputs forces, not positions

---

## What NOT to Add

This kit is complete at its current scope. Resist adding:

- Deep reinforcement learning
- Full terrain perception
- Visual SLAM
- Multi-robot coordination
- Autonomous navigation

These are separate research topics, not fundamentals.

---

## Troubleshooting

### "Robot falls over immediately"
→ Check IMU publishing
→ Check all 4 feet in contact
→ Verify standing pose in joint targets

### "Jerky motion"
→ Increase control rate
→ Check PD gains (lower Kp, higher Kd)
→ Verify effort limits

### "Robot drifts"
→ Check state estimator
→ IMU bias calibration
→ Contact detection accuracy

---

## Learning Path & Master Curriculum (18 Articles)

This kit is accompanied by the comprehensive 18-article **[Legged Locomotion & Embodied Intelligence Series](../../ROS2%20Articles/COMPLETE_INDEX.md#vertical-3-legged-locomotion--embodied-intelligence-series-18-articles)**:

- **Module 1 (Morphology & Kinematics)**: [Embodied Physical Intelligence (LEG 01)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_01_embodied_physical_intelligence.md) | [3-DOF Leg Kinematics (LEG 02)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_02_3dof_leg_kinematics_and_workspace.md) | [Support Polygons & Stability (LEG 03)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_03_support_polygons_and_static_stability.md)
- **Module 2 (Dynamic Balance & Inverted Pendulum)**: [Inverted Pendulum & LIPM (LEG 04)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_04_inverted_pendulum_and_lipm_dynamics.md) | [ZMP & Capture Point Dynamics (LEG 05)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_05_zmp_cop_and_capture_point.md) | [Floating-Base Dynamics (LEG 06)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_06_floating_base_dynamics_and_equations_of_motion.md)
- **Module 3 (Gaits & Swing Trajectories)**: [Gait Taxonomy & Phase Clocks (LEG 07)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_07_gait_taxonomy_and_phase_clocks.md) | [Bézier Swing Trajectories (LEG 08)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_08_bezier_swing_trajectories_and_impact_mitigation.md) | [Raibert Foothold Heuristics (LEG 09)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_09_raibert_heuristic_and_foothold_planning.md)
- **Module 4 (State Estimation & Contact)**: [Floating-Base EKF (LEG 10)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_10_floating_base_state_estimation_ekf.md) | [Contact Sensing & Reaction Forces (LEG 11)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_11_contact_detection_and_ground_reaction_forces.md) | [Slip Detection & Adaptive Covariance (LEG 12)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_12_slip_detection_and_estimator_covariance_adaptation.md)
- **Module 5 (Convex MPC & WBC)**: [Single Rigid Body Dynamics (LEG 13)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_13_single_rigid_body_dynamics_srbd.md) | [Convex MPC & QP Forces (LEG 14)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_14_convex_mpc_for_ground_reaction_force_optimization.md) | [Whole-Body Control (LEG 15)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_15_whole_body_control_and_operational_space.md)
- **Module 6 (Terrain Perception & AI Policies)**: [Terrain Perception & Elevation Maps (LEG 16)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_16_elevation_mapping_and_foothold_scoring.md) | [Adaptive Locomotion & Stairs (LEG 17)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_17_adaptive_terrain_locomotion_stairs_and_slopes.md) | [Reinforcement Learning & Sim-to-Real (LEG 18)](../../ROS2%20Articles/03_Legged_Locomotion_Series/article_leg_18_reinforcement_learning_and_sim_to_real_transfer.md)

---

## References

- MIT Cheetah papers (Kim et al.)
- ETH ANYmal papers
- "Introduction to Legged Locomotion" - Russ Tedrake

---

## License

MIT License. Use it. Teach with it. Break it. Fix it.
