# C++ Runtime Code

- `spider_gait_node.cpp`: a normal ROS 2 node that listens to `/cmd_vel` and publishes leg `JointState` messages, creating a visible walking cycle.
- `spider_gazebo_gait_plugin.cpp`: a Gazebo shared plugin that listens to `/cmd_vel`, moves the simulated model, and publishes `/odom`.

After changing either file, rebuild `spider_pkg` and source the workspace again. The node executable and plugin library are different targets with different loading paths.
