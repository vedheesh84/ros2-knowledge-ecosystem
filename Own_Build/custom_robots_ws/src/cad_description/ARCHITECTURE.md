# `cad_description` Architecture

```text
STL parts ──> cad.urdf ──> robot_state_publisher ──> TF ──> RViz
                  │
                  └──> Gazebo spawn
                         ├── differential drive <── /cmd_vel
                         ├── LiDAR plugin ──> /scan
                         ├── camera plugin ──> image topic
                         └── joint-state plugin ──> /joint_states
```

`cad.urdf` is the authoritative assembly: it connects chassis, wheels, sensors, six arm joints, and two prismatic gripper fingers. It also contains Gazebo material/collision values and sensor/drive plugins. `cad_launch.py` starts the full simulator route; `cad_teleop.launch.py` starts `teleop_twist_keyboard` for the drive plugin.

`CMakeLists.txt` installs every asset directory and `scripts/generate_meshes.py`, so build failures usually come from missing ROS/Gazebo dependencies rather than compilation. When a mesh is replaced, preserve its filename and local origin or update the matching URDF `<mesh>` path and joint origin.
