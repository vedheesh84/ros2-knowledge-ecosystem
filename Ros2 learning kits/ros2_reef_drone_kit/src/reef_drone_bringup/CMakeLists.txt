cmake_minimum_required(VERSION 3.8)
project(reef_drone_bringup)

find_package(ament_cmake REQUIRED)

# Install directories
install(DIRECTORY
  launch
  config
  rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
