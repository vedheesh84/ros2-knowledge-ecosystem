# package_test

Minimal test package template for ROS2 package development and build system testing.

## Table of Contents

- [Overview](#overview)
- [Package Structure](#package-structure)
- [Usage](#usage)

---

## Overview

This is a minimal ROS2 package used for:

- **Build System Testing** - Verify colcon build works correctly
- **Package Template** - Starting point for new packages
- **CI/CD Validation** - Ensure workspace builds cleanly

---

## Package Structure

```
package_test/
├── CMakeLists.txt    # Minimal CMake configuration
└── package.xml       # Package manifest
```

---

## Usage

### As a Build Test

```bash
# Build only this package
colcon build --packages-select package_test

# Verify successful build
colcon build --packages-up-to package_test
```

### As a Template

1. Copy this directory
2. Rename to your package name
3. Update `package.xml`:
   - `<name>` - Your package name
   - `<description>` - Package description
   - `<maintainer>` - Your information
   - `<license>` - Your license choice
4. Update `CMakeLists.txt`:
   - `project(your_package_name)`
5. Add your source files

---

## Package.xml Template

```xml
<?xml version="1.0"?>
<package format="3">
  <name>your_package_name</name>
  <version>0.0.1</version>
  <description>Your package description</description>
  <maintainer email="you@email.com">Your Name</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <!-- Add your dependencies here -->
  <depend>rclpy</depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

---

## CMakeLists.txt Template

```cmake
cmake_minimum_required(VERSION 3.8)
project(your_package_name)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
# find_package(rclcpp REQUIRED)
# find_package(rclpy REQUIRED)

# Add your targets here
# add_executable(my_node src/my_node.cpp)
# ament_target_dependencies(my_node rclcpp)

# Install targets
# install(TARGETS my_node DESTINATION lib/${PROJECT_NAME})
# install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

---

## Dependencies

- `ament_cmake` - Build tool
- `ament_lint_auto` - Linting (test)
- `ament_lint_common` - Common linters (test)
