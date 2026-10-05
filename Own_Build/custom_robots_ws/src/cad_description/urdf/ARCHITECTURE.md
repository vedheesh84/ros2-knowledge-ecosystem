# URDF Architecture

The URDF owns the robot's link/joint tree and connects each link to a mesh. Its Gazebo blocks add drive, LiDAR, camera, and joint-state behaviour, while `robot_state_publisher` uses the same tree to publish TF.
