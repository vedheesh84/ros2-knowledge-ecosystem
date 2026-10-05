# `balancing_robot_description`

This is an ament-Python description package for a two-wheel, self-balancing-style robot. It provides meshes, a URDF, an RViz view, and a single launch file that can run the display with or without Gazebo.

## Generate meshes

```bash
cd "/home/bhuvanesh/ai robot/cad_ws/src/balancing_robot_description"
freecadcmd scripts/generate_balancing_robot_freecad.py
```

## Launch Gazebo + RViz

```bash
cd "/home/bhuvanesh/ai robot/cad_ws"
colcon build --packages-select balancing_robot_description
source install/setup.bash
ros2 launch balancing_robot_description self_balancing.launch.py
```

Terminal 2 (click it, then press keys):

```bash
source "/home/bhuvanesh/ai robot/cad_ws/install/setup.bash"
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Keys: `i` forward, `,` back, `j`/`l` turn, `k` stop, `q`/`z` speed.

## Files

- `urdf/selfbalance.urdf`
- `launch/self_balancing.launch.py`
- `rviz/self_balancing.rviz`
- `meshes/*.stl`

The launch accepts `use_sim_time`, `use_rviz`, `use_gazebo`, `world`, and `spawn_z` arguments. For example, use `use_gazebo:=false` to inspect only the model. See `ARCHITECTURE.md` for topic and component flow.
