# Session save — Self-balancing spherical robot

Date: 2026-08-03  
Workspace: `/home/bhuvanesh/ai robot/cad_ws`

## What was built

Two ROS 2 packages in `src/`:

| Package | Type | Role |
|---------|------|------|
| `balancing_robot_description` | ament_python | FreeCAD meshes, `selfbalance.urdf`, Gazebo+RViz launch |
| `balancing_robot_control` | ament_cmake (C++) | Stub `balance_controller_node` (PID later) |

**Visual model (current):**
- Blue spherical lower body + blue head
- Cyan stacked torso rings
- Yellow power button + torso accent marks
- Plain head (no ears / no yellow visor)
- Black balloon wheels
- Teleop-stable with thin foot collision + Gazebo `diff_drive`

**Key files:**
- `balancing_robot_description/scripts/generate_balancing_robot_freecad.py`
- `balancing_robot_description/urdf/selfbalance.urdf`
- `balancing_robot_description/launch/self_balancing.launch.py`
- `balancing_robot_description/rviz/self_balancing.rviz`
- `balancing_robot_description/meshes/*.stl`
- `balancing_robot_control/src/balance_controller_node.cpp`

## Build

```bash
cd "/home/bhuvanesh/ai robot/cad_ws"
source /opt/ros/humble/setup.bash
colcon build --packages-select balancing_robot_description balancing_robot_control
source install/setup.bash
```

## Regenerate FreeCAD meshes (if geometry/colors change)

```bash
cd "/home/bhuvanesh/ai robot/cad_ws/src/balancing_robot_description"
freecadcmd scripts/generate_balancing_robot_freecad.py
cd "/home/bhuvanesh/ai robot/cad_ws"
colcon build --packages-select balancing_robot_description
source install/setup.bash
```

## Launch

Kill any old Gazebo first:
```bash
pkill -9 -x gzserver; pkill -9 -x gzclient
```

Terminal 1 — Gazebo + RViz:
```bash
cd "/home/bhuvanesh/ai robot/cad_ws"
source install/setup.bash
ros2 launch balancing_robot_description self_balancing.launch.py
```

Terminal 2 — keyboard teleop (click this terminal before keys):
```bash
source "/home/bhuvanesh/ai robot/cad_ws/install/setup.bash"
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Keys: `i` forward, `,` back, `j`/`l` turn, `k` stop, `q`/`z` speed.

## Reference image used for look

`/home/bhuvanesh/Pictures/Screenshots/Screenshot from 2026-08-03 14-31-38.png`

## Next (not done this session)

- Real IMU-based balancing PID in `balancing_robot_control`
- Optional: restore ears/visor or recolor again via FreeCAD script constants / URDF materials
