cmake_minimum_required(VERSION 3.8)
project(mobile_manipulator_demos)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Install launch files
install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}
)

# Install demo scripts
install(PROGRAMS
  scripts/demo_01_joint_control.py
  scripts/demo_02_gripper_control.py
  scripts/demo_03_camera_tf.py
  scripts/demo_04_object_detection.py
  scripts/demo_05_static_pick_place.py
  scripts/demo_06_mobile_pick_place.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install breaker scripts
install(PROGRAMS
  scripts/breakers/break_camera_tf.py
  scripts/breakers/break_grasp_frame.py
  scripts/breakers/break_controller.py
  scripts/breakers/break_ik.py
  scripts/breakers/break_vision.py
  DESTINATION lib/${PROJECT_NAME}/breakers
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
