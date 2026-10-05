cmake_minimum_required(VERSION 3.8)
project(cex_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(action_msgs REQUIRED)

# Define action files
set(action_files "action/MoveTurtle.action")

# Generate interfaces from custom message, service, and action definitions
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/NumPair.msg"
  "srv/AddTwoInt.srv"
  ${action_files}
  DEPENDENCIES builtin_interfaces action_msgs std_msgs
)

# Install Python scripts
file(GLOB PYTHON_SCRIPTS "script/*.py")
install(
  PROGRAMS ${PYTHON_SCRIPTS}
  DESTINATION lib/${PROJECT_NAME}
)

# Install service definitions
install(
  DIRECTORY srv
  DESTINATION share/${PROJECT_NAME}
)

# Install action definitions
install(
  DIRECTORY action
  DESTINATION share/${PROJECT_NAME}
)

# Install message definitions
install(
  DIRECTORY msg
  DESTINATION share/${PROJECT_NAME}
)

# Install URDF files
install(
  DIRECTORY urdf
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_export_dependencies(rosidl_default_runtime)
ament_package()
