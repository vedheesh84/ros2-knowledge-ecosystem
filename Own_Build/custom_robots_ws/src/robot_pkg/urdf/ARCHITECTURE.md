# Description Architecture

Every robot is a tree of **links** (rigid bodies) connected by **joints** (fixed, continuous, revolute, or prismatic). `robot_state_publisher` turns that tree plus joint states into TF transforms. Gazebo-specific `<gazebo>` blocks add collision/visual material and plugins such as differential drive, LiDAR, planar movement, or ros2_control.

The launch file chooses the exact description file. Do not assume a configuration for one model works with another: joint names, sensors, and plugin topics differ.
