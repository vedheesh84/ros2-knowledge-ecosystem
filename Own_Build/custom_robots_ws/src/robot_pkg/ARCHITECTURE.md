# `robot_pkg` Architecture

## Package composition

```text
launch scenario
 ├── URDF/Xacro from urdf/ ──> robot_state_publisher ──> TF ──> RViz config
 ├── Gazebo world from worlds/ ──> Gazebo spawn entity
 ├── Gazebo plugins <── /cmd_vel ──> /odom and (where defined) /scan
 └── optional config/
     ├── SLAM Toolbox ──> /map
     ├── Nav2 + maps/my_map.yaml ──> navigation
     └── ros2_control for the humanoid
```

## Model families

- **Numbered URDF files (`01`–`07`)** form a progression from one link through visual, flexible, and physics-rich articulated examples.
- **`robot*.xacro`, `gazebo_urdf.xacro`, `gaja.urdf`, `fusion.urdf`** are vehicle experiments. Differential-drive plugins translate `/cmd_vel` into wheel movement.
- **`navy.urdf.xacro`** is the most complete mobile manipulator: wheeled base, LiDAR, camera, arm and gripper. The Navy launches use it for display, SLAM, and Nav2.
- **`human_robot.urdf`** declares ros2_control joints; `human_controllers.yaml` supplies their controller definitions.
- **`cat.urdf` and `simple_robot.urdf`** are smaller visual/simulation demos.

## Launch progression for Navy

1. `navy_launch.py`: starts Gazebo, Navy spawn, state publishing, joint-state publishing, RViz.
2. `navy_mapping_launch.py`: replaces the joint-state path with SLAM Toolbox using `navy_mapper_params.yaml`; it creates a map from LiDAR scans.
3. `navy_nav_launch.py`: loads `maps/my_map.yaml` and `navy_nav2_params.yaml` to run Nav2 against an existing map.

## Maintenance notes

`package.xml` lists many runtime dependencies while `CMakeLists.txt` installs assets. The two standalone Python files at the package root (`dual_cam_server.py`, `podcast_clip_agent.py`) are not installed as ROS executables or referenced by launch files, so they are outside the ROS package runtime path. The manifest also retains placeholder description/license text; replace those before public distribution.
