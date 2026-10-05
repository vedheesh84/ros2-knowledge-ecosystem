# `spider_pkg`

`spider_pkg` is a ROS 2 C++ simulation package for a mechanical six-legged spider. It pairs a Xacro robot description with a joint-animation node and a Gazebo movement plugin; LiDAR and SLAM are available for mapping demonstrations.

## Build

From the workspace root:

```bash
colcon build --packages-select spider_pkg
source install/setup.bash
```

## Run

```bash
ros2 launch spider_pkg display.launch.py
```

The launch file starts:

- `robot_state_publisher`
- `spider_gait_node`
- RViz with the included robot display config

The spider only starts walking when a `cmd_vel` command is active. Use a teleop node such as `teleop_twist_keyboard` to publish those commands.

You can tune the movement by changing `speed_hz`, `hip_swing`, `femur_lift`, `tibia_lift`, and `motion_timeout` in `launch/display.launch.py`.

## Gazebo and mapping

Terminal 1:
```bash
source /opt/ros/humble/setup.bash
source ~/spidy/install/setup.bash
ros2 launch spider_pkg gazebo.launch.py gui:=true use_rviz:=true use_slam:=true
```

Terminal 2 (teleop):
```bash
source /opt/ros/humble/setup.bash
source ~/spidy/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Drive with `i` / `,` / `j` / `l`. In RViz you should see:
- spider moving in the `map` frame
- red lidar `/scan`
- map building on `/map`

Save the map later with:
```bash
ros2 run nav2_map_server map_saver_cli -f ~/spider_map
```

## Choose a launch file

| Launch file | Use it when |
|---|---|
| `display.launch.py` | You want to inspect the articulated model and gait in RViz only. |
| `gazebo.launch.py` | You want the configurable full simulation; its arguments choose GUI, RViz, teleop, SLAM, and world. |
| `spider_launch.launch.py` | You want the standard Gazebo simulation without the mapping focus. |
| `spider_mapping.launch.py` | You want the mapping-oriented world and SLAM Toolbox. |

See `ARCHITECTURE.md` for the topic flow and the responsibility of each C++ component.
