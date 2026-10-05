cmake_minimum_required(VERSION 3.8)
project(drone_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(gazebo_msgs REQUIRED)
find_package(tf2_ros REQUIRED)

add_executable(manual_drone_controller src/manual_drone_controller.cpp)
ament_target_dependencies(manual_drone_controller
  rclcpp
  geometry_msgs
  gazebo_msgs
  tf2_ros
)

install(TARGETS manual_drone_controller
  DESTINATION lib/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/generate_drone_freecad.py
  scripts/propeller_spinner.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch meshes rviz urdf docs worlds
  DESTINATION share/${PROJECT_NAME}
)

install(FILES resource/${PROJECT_NAME}
  DESTINATION share/ament_index/resource_index/packages
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
