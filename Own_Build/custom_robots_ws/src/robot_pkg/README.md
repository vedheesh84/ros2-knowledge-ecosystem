# `robot_pkg`

`robot_pkg` is an ament-CMake ROS 2 package used to learn robot description and simulation. It contains several separate robots, so choose the launch file that matches the model you want; it is not one single production robot.

## What you can run

| Goal | Start here | What it starts |
|---|---|---|
| Inspect a basic model | `rviz.launch.py`, `display_robot.launch.py`, or `demo_launch.py` | Robot State Publisher, joint-state publisher, RViz. |
| Simulate a vehicle | `gazebo.launch.py`, `gazebo_rviz.launch.py`, `gaja_launch.py`, or `fusion_car.launch.py` | Gazebo and a selected vehicle model. |
| Simulate a humanoid | `human_gazebo.launch.py` | Gazebo, ros2_control, and the humanoid controllers. |
| Drive/map/navigate the Navy robot | `navy_launch.py`, `navy_mapping_launch.py`, `navy_nav_launch.py` | Gazebo plus RViz; mapping adds SLAM Toolbox and navigation adds Nav2. |

## Build

```bash
cd ~/ros2_ws
colcon build --packages-select robot_pkg
source install/setup.bash
```

## Example commands

```bash
ros2 launch robot_pkg navy_launch.py
ros2 launch robot_pkg navy_mapping_launch.py
ros2 launch robot_pkg navy_nav_launch.py
```

Use a second terminal (also sourced) for keyboard driving when the selected launch supports it:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

The model/plugin consumes velocity commands on `/cmd_vel` and normally publishes `/odom`; models with LiDAR additionally publish `/scan`.

## Folder guide

- `urdf/`: source robot descriptions, from numbered learning examples to the Navy mobile manipulator.
- `launch/`: runnable ROS 2 scenarios. Read its README before choosing one.
- `config/`: controller, SLAM, and Nav2 settings.
- `worlds/`: Gazebo environments; `maps/`: saved map image and metadata.
- `meshes/`: STL parts referenced by some models; `rviz/`: saved RViz layouts.

See `ARCHITECTURE.md` for the full relationship between these folders and a note on known limitations.
