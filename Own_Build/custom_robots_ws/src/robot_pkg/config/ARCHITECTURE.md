# Configuration Architecture

```text
launch/*.launch.py ──> parameter YAML ──> ROS node
navy_mapping_launch ──> navy_mapper_params.yaml ──> slam_toolbox
navy_nav_launch     ──> navy_nav2_params.yaml   ──> Nav2 servers
human_gazebo        ──> human_controllers.yaml  ──> controller_manager
```

Change parameters here rather than hard-coding values in launch files. A YAML key must match the target node name and `ros__parameters` block or ROS 2 will silently leave the intended value at its default.
