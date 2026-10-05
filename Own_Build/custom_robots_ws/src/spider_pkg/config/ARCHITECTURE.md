# Configuration Architecture

`spider_mapping.launch.py` supplies this YAML to `slam_toolbox`. The node combines `/scan` with the TF/odometry chain emitted by the simulator and produces `/map`. A topic or frame-name mismatch breaks mapping even if Gazebo renders normally.
