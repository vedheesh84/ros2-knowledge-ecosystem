# Launch Architecture

The launch layer locates package files, sets Gazebo resource/plugin paths, runs the simulator, supplies the Xacro model to `robot_state_publisher`, and spawns it. Mapping variants additionally load `config/slam_toolbox.yaml`. The C++ executables are built into `lib/spider_pkg`; the Gazebo plugin is installed as a shared library in `lib` so Gazebo can load it by filename.
