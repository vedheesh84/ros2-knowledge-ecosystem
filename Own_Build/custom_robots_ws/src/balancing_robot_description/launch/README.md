# Launch

`self_balancing.launch.py` is the single entry point. It declares simulation/RViz/world/spawn-height arguments, reads the URDF, starts state publishing, conditionally includes Gazebo, spawns the robot, and conditionally opens RViz.
