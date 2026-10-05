# `cad_description`

`cad_description` models a four-wheel mobile manipulator: chassis, LiDAR, camera, arm, wrist camera, and parallel gripper. It is an ament-CMake package intended for RViz and classic Gazebo.

## Build and run

```bash
cd ~/ros2_ws
colcon build --packages-select cad_description
source install/setup.bash
ros2 launch cad_description cad_launch.py
```

Use `cad_teleop.launch.py` to start keyboard teleoperation. The main launch supports `use_sim_time`, `use_rviz`, `use_gazebo`, `world`, and `spawn_z` arguments. The `docs/FREECAD_LEARNING_PATH.md` file teaches how to recreate/export the CAD assets; `ARCHITECTURE.md` describes the ROS-side structure.
