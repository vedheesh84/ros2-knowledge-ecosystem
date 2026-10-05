# Configuration

This folder holds runtime parameters, not executable code. Launch files pass these YAML files to controllers, SLAM Toolbox, or Nav2.

- `human_controllers.yaml`: controller-manager definitions for the humanoid joints.
- `mapper_params_online_async.yaml`: general online asynchronous SLAM settings.
- `navy_mapper_params.yaml`: SLAM settings selected by the Navy mapping launch.
- `navy_nav2_params.yaml`: Nav2 planner, controller, costmap, localisation, and behaviour-server settings.

Keep topic names consistent with the model: the mapping configurations expect LiDAR on `/scan`, and navigation expects odometry on `/odom`/`odom` as configured.
