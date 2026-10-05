# RViz Architecture

```text
robot_state_publisher ──> /tf ──> RobotModel display
Gazebo / controllers ──> joint states ──> robot pose
LiDAR / SLAM / Nav2 ──> /scan, /map, paths ──> sensor and map displays
```

RViz observes ROS data; it never drives the simulated robot or produces a map itself.
