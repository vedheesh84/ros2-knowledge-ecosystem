cmake_minimum_required(VERSION 3.8)
project(spider_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(gazebo_dev REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(tf2_ros REQUIRED)

add_executable(spider_gait_node src/spider_gait_node.cpp)
ament_target_dependencies(spider_gait_node rclcpp sensor_msgs geometry_msgs)

add_library(spider_gazebo_gait_plugin SHARED src/spider_gazebo_gait_plugin.cpp)
target_include_directories(spider_gazebo_gait_plugin PUBLIC ${GAZEBO_INCLUDE_DIRS})
target_link_libraries(spider_gazebo_gait_plugin ${GAZEBO_LIBRARIES})
ament_target_dependencies(spider_gazebo_gait_plugin rclcpp geometry_msgs nav_msgs sensor_msgs tf2_ros)

install(TARGETS
  spider_gait_node
  DESTINATION lib/${PROJECT_NAME}
)

install(TARGETS
  spider_gazebo_gait_plugin
  DESTINATION lib
)

install(DIRECTORY
  launch
  rviz
  urdf
  worlds
  config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
