cmake_minimum_required(VERSION 3.8)
project(quadruped_bringup)

find_package(ament_cmake REQUIRED)

# Install launch files and config
install(DIRECTORY
  launch
  config
  rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
