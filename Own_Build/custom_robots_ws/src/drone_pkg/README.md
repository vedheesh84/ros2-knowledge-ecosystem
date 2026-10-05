# `drone_pkg`

`drone_pkg` is an educational ROS 2 Humble package for a four-propeller drone model in RViz and classic Gazebo. Its manual controller changes the Gazebo entity pose from `/cmd_vel`; it is **not** an aerodynamic, PX4, or MAVLink flight stack.

## Build and launch

```bash
cd ~/ros2_ws
colcon build --packages-select drone_pkg
source install/setup.bash
ros2 launch drone_pkg drone_gazebo.launch.py
```

Use `drone_rviz.launch.py` when you only need the model visualisation. For commands, model generation, and the `/cmd_vel` mapping, read `docs/USAGE.md`. `ARCHITECTURE.md` explains the controller-service path and propeller animation.
