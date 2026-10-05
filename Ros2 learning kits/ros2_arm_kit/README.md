# ros2_arm_kit

**Robotic Arm Learning Kit & Kinematic Manipulation Platform**

A precision learning platform for articulated robot kinematics, trajectory planning, MoveIt2 integration, and tabletop manipulation.

---

## 1. Overview & Identity

`ros2_arm_kit` is the primary manipulation learning kit in the Intelligent Ecosystem. It isolates and deep-dives into **Kinematic & Precision Manipulation Intelligence** using a 5/6-DOF articulated robotic arm equipped with a parallel gripper.

It bridges fundamental ROS2 communication with advanced spatial kinematics, analytical IK solvers, MoveIt2 motion planning pipelines, and autonomous pick-and-place state machines.

---

## 2. Package Architecture

```text
ros2_arm_kit/
├── resources/
│   ├── arm_kinematics_derivation.md     # Forward/Inverse kinematics & Jacobian derivations
│   └── moveit2_planning_pipeline.md     # OMPL & MoveIt2 motion planning architecture
├── src/
│   ├── arm_description/                 # URDF/Xacro models, STL meshes, and RViz display
│   ├── arm_hardware/                    # Mock hardware and PCA9685/Arduino serial bridges
│   ├── arm_kinematics/                  # Pure Python FK, IK, and Jacobian singularity solvers
│   ├── arm_manipulation/                # Gripper action server and pick-and-place state machine
│   ├── arm_moveit/                      # MoveIt2 SRDF, OMPL configuration, and kinematics
│   ├── arm_bringup/                     # Master simulation and hardware launch orchestration
│   └── arm_demos/                       # 6 progressive educational demos + 4 failure breakers
└── README.md                            # Primary workspace documentation
```

---

## 3. Quick Start

```bash
# 1. Build workspace
cd "02 — Domains/ROS2/Ros2 learning kits/ros2_arm_kit"
colcon build --symlink-install
source install/setup.bash

# 2. Visualize robot in RViz with joint slider GUI
ros2 launch arm_description display.launch.py

# 3. Launch full simulated arm environment
ros2 launch arm_bringup arm_sim.launch.py
```

---

## 4. Progressive Demo Curriculum

Execute these demos in sequence to understand the complete manipulation stack:

| Demo | Focus | Concepts & Skills Mastered |
|---|---|---|
| **Demo 01** | `demo_01_joint_control` | ros2_control trajectories, multi-joint interpolation, and timing constraints. |
| **Demo 02** | `demo_02_forward_kinematics` | Calculating end-effector Cartesian pose from `/joint_states` and verifying with TF. |
| **Demo 03** | `demo_03_inverse_kinematics` | Cartesian 3D reaching, trigonometric IK solving, and manipulability metrics. |
| **Demo 04** | `demo_04_gripper_action` | Parallel gripper actuation, effort limits, and stall detection feedback. |
| **Demo 05** | `demo_05_moveit_planning` | Collision-aware trajectory planning around obstacles using MoveIt2 and OMPL. |
| **Demo 06** | `demo_06_pick_place` | Master autonomous state machine executing Approach $\rightarrow$ Grasp $\rightarrow$ Lift $\rightarrow$ Place. |
| **Demo 07** | `demo_07_teleoperation_mirroring` | High-frequency leader-follower bilateral joint mirroring over low-latency ROS2 DDS. |
| **Demo 08** | `demo_08_imitation_learning_recorder` | Multimodal demonstration logging into structured episodic robotics datasets. |
| **Demo 09** | `demo_09_trajectory_playback_policy` | Dynamic Movement Primitives (DMP) trajectory generalization and autonomous execution. |

```bash
# Run Demo 01: Joint Trajectory Control
ros2 run arm_demos demo_01_joint_control

# Run Demo 06: Autonomous Pick-and-Place State Machine
ros2 run arm_manipulation pick_place_state_machine

# Run Demo 07: Leader-Follower Teleoperation Mirroring
ros2 run arm_demos demo_07_teleoperation_mirroring

# Run Demo 09: Autonomous DMP Policy Playback
ros2 run arm_demos demo_09_trajectory_playback_policy
```

---

## 5. Intentional Failure Breakers

Run the breaker nodes in `arm_demos/breakers` to study failure modes and fault recovery:

| Breaker | Injected Fault | Architectural Lesson Learned |
|---|---|---|
| `break_joint_limits` | Commands angles beyond physical bounds | Controller parameter safety and joint saturation clamping. |
| `break_ik_singularity` | Requests points outside workspace radius | Analytical IK reachability limits and singularity detection. |
| `break_gripper_stall` | Simulates missed grasp / dropped payload | Action feedback validation and grasp state transitions. |
| `break_trajectory_timing` | Excessive joint acceleration | Dynamic limits and trajectory tracking error handling. |

```bash
# Example: Test IK reachability failure rejection
ros2 run arm_demos break_ik_singularity
```

---

## 6. Robotic Arm Learning Curriculum (20 Articles)

This kit is accompanied by the comprehensive 20-article **[Robotic Arm Manipulation Series](../../ROS2%20Articles/COMPLETE_INDEX.md#vertical-1-robotic-arm--manipulation-series-20-articles)**:

- **Module 1**: [Spatial Frames (ARM 01)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_01_spatial_frames_and_rotations.md) | [Kinematic Modeling (ARM 02)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_02_kinematic_modeling_dh_vs_urdf.md) | [Forward Kinematics (ARM 03)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_03_forward_kinematics_derivation.md)
- **Module 2**: [IK Problem (ARM 04)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_04_the_inverse_kinematics_problem.md) | [Analytical IK (ARM 05)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_05_analytical_ik_geometric_decoupling.md) | [Jacobians (ARM 06)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_06_differential_kinematics_jacobians.md)
- **Module 3**: [Dynamics (ARM 07)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_07_arm_dynamics_and_torques.md) | [Polynomial Trajectories (ARM 08)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_08_polynomial_trajectory_generation.md) | [TOTG Parameterization (ARM 09)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_09_time_optimal_parameterization.md)
- **Module 4**: [C-Space (ARM 10)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_10_configuration_space_and_obstacles.md) | [OMPL Planners (ARM 11)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_11_sampling_based_planners_ompl.md) | [MoveIt2 System (ARM 12)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_12_moveit2_system_architecture.md) | [Replanning (ARM 13)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_13_planning_latency_and_replanning.md)
- **Module 5**: [ros2_control Pipeline (ARM 14)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_14_ros2_control_execution_pipeline.md) | [Servo Hardware & Serial (ARM 15)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_15_servo_hardware_and_serial_bridges.md)
- **Module 6 (Capstone)**: [Contact Mechanics (ARM 16)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_16_contact_physics_and_grasp_synthesis.md) | [Pick & Place FSM (ARM 17)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_17_closed_loop_pick_place_state_machine.md) | [Fault Recovery (ARM 18)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_18_reactive_replanning_and_fault_recovery.md)
- **Modules 7 & 8**: [Teleoperation Mirroring (ARM 19)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_19_leader_follower_teleoperation_mirroring.md) | [Imitation Learning & DMPs (ARM 20)](../../ROS2%20Articles/01_Robotic_Arm_Series/article_arm_20_learning_from_demonstration_and_imitation.md)

Detailed kinematics mathematical derivation is also available in [arm_kinematics_derivation.md](resources/arm_kinematics_derivation.md).
