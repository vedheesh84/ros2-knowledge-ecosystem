# =============================================================================
# CMakeLists.txt for learning_comms
# =============================================================================
#
# This package uses ament_cmake because we define custom interfaces (actions).
# Even though our nodes are in Python, the action definition requires CMake.
#
# LEARNING OBJECTIVE:
# -------------------
# Understand why some Python packages use ament_cmake:
# - Custom message/service/action definitions need code generation
# - Code generation requires CMake toolchain
# - Python nodes can still be installed alongside generated interfaces
#
# =============================================================================

cmake_minimum_required(VERSION 3.8)
project(learning_comms)

# Default to C++17 (required for some ROS2 features)
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

# Compiler warnings (good practice)
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# =============================================================================
# FIND DEPENDENCIES
# =============================================================================
# find_package() locates installed ROS2 packages

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)  # For action generation
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)

# =============================================================================
# GENERATE INTERFACES (ACTIONS)
# =============================================================================
# rosidl_generate_interfaces() creates Python/C++ bindings for our action
#
# After generation, you can import:
#   from learning_comms.action import CountToNumber

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/CountToNumber.action"
)

# =============================================================================
# INSTALL PYTHON NODES
# =============================================================================
# Since we're using ament_cmake (not ament_python), we install Python
# scripts manually. They go to lib/<package_name>/ to be executable.

install(PROGRAMS
  learning_comms/talker_node.py
  learning_comms/listener_node.py
  learning_comms/service_server_node.py
  learning_comms/service_client_node.py
  learning_comms/action_server_node.py
  learning_comms/action_client_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# =============================================================================
# INSTALL LAUNCH FILES
# =============================================================================

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

# =============================================================================
# INSTALL CONFIG FILES
# =============================================================================

install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}
)

# =============================================================================
# TESTING (optional)
# =============================================================================

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

# =============================================================================
# FINALIZE
# =============================================================================

ament_package()
