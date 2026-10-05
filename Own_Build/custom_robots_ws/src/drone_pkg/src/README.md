# C++ Controller

`manual_drone_controller.cpp` implements the `manual_drone_controller` node. It listens for `geometry_msgs/Twist` commands on `/cmd_vel` and asks Gazebo to update the named drone entity's position and yaw.
