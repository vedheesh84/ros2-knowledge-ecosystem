cmake_minimum_required(VERSION 3.8)
project(robot_pkg)

# Find necessary dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(robot_state_publisher REQUIRED)
find_package(xacro REQUIRED)

# Install launch, urdf, and world files
install(DIRECTORY
  launch
  config
  maps
  meshes
  rviz
  urdf
  worlds
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
