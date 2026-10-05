cmake_minimum_required(VERSION 3.8)
project(mobile_manipulator_hardware)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(hardware_interface REQUIRED)
find_package(pluginlib REQUIRED)

# Include directories
include_directories(include)

# ============================================
# BASE HARDWARE INTERFACE LIBRARY
# ============================================
add_library(base_hardware_interface SHARED
  src/base_hardware_interface.cpp
  src/serial_port.cpp
)
target_include_directories(base_hardware_interface PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(base_hardware_interface
  rclcpp
  rclcpp_lifecycle
  hardware_interface
  pluginlib
)

# ============================================
# ARM HARDWARE INTERFACE LIBRARY
# ============================================
add_library(arm_hardware_interface SHARED
  src/arm_hardware_interface.cpp
  src/serial_port.cpp
)
target_include_directories(arm_hardware_interface PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(arm_hardware_interface
  rclcpp
  rclcpp_lifecycle
  hardware_interface
  pluginlib
)

# ============================================
# PLUGIN EXPORTS
# ============================================
pluginlib_export_plugin_description_file(hardware_interface mobile_manipulator_hardware.xml)

# ============================================
# INSTALL
# ============================================
install(
  TARGETS base_hardware_interface arm_hardware_interface
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(
  DIRECTORY include/
  DESTINATION include
)

install(
  DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

ament_export_include_directories(include)
ament_export_libraries(base_hardware_interface arm_hardware_interface)
ament_export_targets(export_${PROJECT_NAME})
ament_export_dependencies(
  rclcpp
  rclcpp_lifecycle
  hardware_interface
  pluginlib
)

ament_package()
