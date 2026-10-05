cmake_minimum_required(VERSION 3.8)
project(reef_drone_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(gazebo_dev REQUIRED)

# Include directories
include_directories(include)

# Buoyancy Plugin
add_library(buoyancy_plugin SHARED
  src/buoyancy_plugin.cpp
)
target_include_directories(buoyancy_plugin PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(buoyancy_plugin
  rclcpp
  gazebo_ros
  gazebo_dev
)

# Hydrodynamics Plugin
add_library(hydrodynamics_plugin SHARED
  src/hydrodynamics_plugin.cpp
)
target_include_directories(hydrodynamics_plugin PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(hydrodynamics_plugin
  rclcpp
  gazebo_ros
  gazebo_dev
)

# Thruster Plugin
add_library(thruster_plugin SHARED
  src/thruster_plugin.cpp
)
target_include_directories(thruster_plugin PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(thruster_plugin
  rclcpp
  gazebo_ros
  gazebo_dev
  std_msgs
)

# Install libraries
install(TARGETS
  buoyancy_plugin
  hydrodynamics_plugin
  thruster_plugin
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

# Install directories
install(DIRECTORY
  include/
  DESTINATION include
)

install(DIRECTORY
  launch
  worlds
  config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
