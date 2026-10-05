# FreeCAD Drone Package

`drone_pkg` is a ROS 2 Humble package for a simple aerial drone model. The STL meshes and URDF are generated with FreeCAD Python, then launched in RViz and classic Gazebo.

## Generate the Model

From the source package:

```bash
cd "/home/bhuvanesh/ai robot/cad_ws/src/drone_pkg"
freecadcmd scripts/generate_drone_freecad.py
```

From an installed package:

```bash
cd "/home/bhuvanesh/ai robot/cad_ws"
source install/setup.bash
DRONE_PKG_OUTPUT_ROOT="/home/bhuvanesh/ai robot/cad_ws/src/drone_pkg" ros2 run drone_pkg generate_drone_freecad.py
```

The script writes:

- `meshes/*.stl`
- `urdf/drone.urdf`

## Build

```bash
cd "/home/bhuvanesh/ai robot/cad_ws"
colcon build --packages-select drone_pkg
source install/setup.bash
```

## RViz

```bash
ros2 launch drone_pkg drone_rviz.launch.py
```

## Gazebo And Manual Control

Terminal 1:

```bash
ros2 launch drone_pkg drone_gazebo.launch.py
```

Terminal 2 — keyboard teleop (preferred):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Keys:

- `i` / `,` : forward / back
- `j` / `l` : left / right yaw
- `t` / `b` : up / down
- `k` : stop

Orange propeller blades spin continuously (faster while you send motion commands).

Terminal 2 — direct topic examples:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.5}, angular: {z: 0.0}}" -r 10
```

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.6, y: 0.0, z: 0.0}, angular: {z: 0.0}}" -r 10
```

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {z: 0.7}}" -r 10
```

Stop by publishing zeros:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"
```

## Command Mapping

- `linear.x`: forward/back
- `linear.y`: left/right
- `linear.z`: up/down
- `angular.z`: yaw

This controller is an educational manual-control demo. It is not a PX4, MAVLink, or aerodynamic flight controller.
