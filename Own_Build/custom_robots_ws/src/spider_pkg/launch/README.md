# Launch Files

| File | Purpose |
|---|---|
| `display.launch.py` | RViz model inspection and C++ gait animation, no Gazebo physics. |
| `gazebo.launch.py` | Full configurable Gazebo entry point; can enable GUI, RViz, teleop, SLAM, and choose a world. |
| `spider_launch.launch.py` | Standard Gazebo simulation. |
| `spider_mapping.launch.py` | Gazebo mapping scenario with SLAM Toolbox. |

All files accept or declare runtime values instead of embedding a fixed machine path. Start with `display.launch.py`, then move to Gazebo.
