# Robotic_Arm_ws

**Robotic Arm Manipulation Workspace**

This workspace serves as the primary development and experimentation environment for articulated robot arms within the Intelligent Systems Knowledge Ecosystem.

---

## 1. Overview & Architecture

`Robotic_Arm_ws` contains the core packages, kinematics solvers, MoveIt2 configurations, and progressive learning curriculum for 5/6-DOF articulated robotic arms.

For the full learning kit, progressive demos, and failure breakers, refer to:
👉 **[ros2_arm_kit](../Ros2%20learning%20kits/ros2_arm_kit/README.md)**

---

## 2. Core Capabilities

- **Kinematics Engine:** Analytical Forward Kinematics, Inverse Kinematics, and Jacobian Singularity Analysis.
- **Motion Planning:** MoveIt2 with OMPL RRTConnect planners and collision avoidance.
- **Actuation & Bridges:** ros2_control Joint Trajectory Controller with PCA9685 / Arduino serial hardware bridges.
- **Autonomous Manipulation:** Parallel gripper action servers and autonomous pick-and-place state machines.
- **Hardware-in-the-Loop Emulation:** Desktop pseudo-hardware serial PTY emulator (`scripts/pseudo_arm_emulator.py`) and Arduino/ESP32 firmware (`arduino/robotic_arm_controller/`).


---

## 3. Related Systems

- **[Mobile Manipulator (`gripper_car_ws`)](../Mobile_Manipulator_ws/gripper_car_ws/README.md):** Integrated 4WD mobile base + robotic arm platform.
- **[Kits & Products Strategy](../KITS_AND_PRODUCTS_STRATEGY.md):** Strategic product portfolio architecture.
