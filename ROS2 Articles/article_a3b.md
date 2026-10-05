## A3b: FROM PACKAGE STRUCTURE TO RUNNING NODE

*Purpose: Bridge theory (A3) to practice. Show how to actually create a package and run a node.*

### Must Answer
- How do you create a new package from scratch?
- What goes in package.xml and CMakeLists.txt?
- How do dependencies work?
- How do you verify your package compiles?

### Key Insight
Creating a package is straightforward: folder + package.xml + CMakeLists.txt + code. Colcon handles the rest.

---

### The Minimal Package

A working package needs only three things:

```
my_package/
├── package.xml          ← Metadata
├── CMakeLists.txt       ← Build instructions  
└── src/
    └── main.cpp         ← Your code
```

That's it. Colcon can build this.

---

### Step 1: Create the Folder Structure

```bash
$ cd my_robot_ws/src
$ mkdir my_package
$ cd my_package
$ mkdir src include
```

Now you have:
```
my_robot_ws/src/my_package/
├── src/
└── include/
```

---

### Step 2: Write package.xml

```xml
<?xml version="1.0"?>
<package format="3">
  <name>my_package</name>
  <version>0.0.1</version>
  <description>My first ROS2 package</description>
  <maintainer email="you@example.com">Your Name</maintainer>
  <license>Apache-2.0</license>
  
  <depend>rclcpp</depend>
  <depend>std_msgs</depend>
</package>
```

What each line does:
- `<name>`: Package name (must match folder name)
- `<version>`: Version (0.0.1 for first version)
- `<description>`: One-line description
- `<maintainer>`: Who maintains it
- `<license>`: License type (Apache-2.0 is standard)
- `<depend>`: Dependencies (rclcpp = ROS2 C++ library, std_msgs = standard message types)

**Common Dependencies:**
- `rclcpp` — ROS2 C++ library
- `rclpy` — ROS2 Python library
- `std_msgs` — Standard message types
- `sensor_msgs` — Sensor messages (images, scans)
- `geometry_msgs` — Geometry messages (poses, velocities)

---

### Step 3: Write CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.5)
project(my_package)

# Find dependencies
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# Build executable
add_executable(my_node src/main.cpp)
ament_target_dependencies(my_node rclcpp std_msgs)

# Install executable
install(TARGETS my_node DESTINATION lib/${PROJECT_NAME})
```

What each section does:
1. **cmake_minimum_required** — Minimum CMake version
2. **project** — Project name (matches package.xml)
3. **find_package** — Find required libraries
4. **add_executable** — Build an executable from source files
5. **ament_target_dependencies** — Link dependencies to executable
6. **install** — Install executable to `/install`

**Key Points:**
- `add_executable(my_node src/main.cpp)` → builds `my_node` from `src/main.cpp`
- If you have multiple source files: `add_executable(my_node src/main.cpp src/helper.cpp)`
- If you add dependencies, add them to both `find_package` AND `ament_target_dependencies`

---

### Step 4: Write Your Code

Create `src/main.cpp`:

```cpp
#include "rclcpp/rclcpp.hpp"

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::create_node("my_node");
  RCLCPP_INFO(node->get_logger(), "Hello from ROS2!");
  rclcpp::shutdown();
  return 0;
}
```

This is the minimal ROS2 node:
- Creates a ROS2 node named "my_node"
- Prints "Hello from ROS2!"
- Shuts down gracefully

---

### Step 5: Build the Package

```bash
$ cd my_robot_ws
$ colcon build
```

Colcon discovers your package, reads package.xml, follows CMakeLists.txt, compiles.

Output:
```
Starting >>> my_package
Finished >>> my_package [1.2s]
Summary: 1 package built in 1.2s
```

If there's an error:
```
Finished >>> my_package [0.1s]
Summary: 1 package failed in 0.1s
```

Check the error message. Likely causes:
- Typo in package.xml or CMakeLists.txt
- Missing dependency (add to both package.xml and CMakeLists.txt)
- Missing source file

---

### Step 6: Source and Run

```bash
$ source install/setup.bash
$ ros2 run my_package my_node
```

Output:
```
[INFO] [my_node]: Hello from ROS2!
```

Success! Your first node runs.

---

### Common Mistakes and Fixes

**Mistake 1: Package name doesn't match folder name**

```
Folder: my_robot/
package.xml: <name>my_package</name>
```

Error: Package not found.

Fix: Match them exactly.

**Mistake 2: Forgot to add dependency to CMakeLists.txt**

You add `sensor_msgs` to package.xml but forget CMakeLists.txt:

```cmake
find_package(sensor_msgs REQUIRED)  ← Missing!
```

Error: Compiler can't find sensor_msgs headers.

Fix: Add to both package.xml AND CMakeLists.txt.

**Mistake 3: Forgot to source setup.bash**

```bash
$ ros2 run my_package my_node
Error: Package 'my_package' not found
```

Fix:
```bash
$ source install/setup.bash
$ ros2 run my_package my_node
```

---

### Verifying Your Package

Check if package is found:

```bash
$ ros2 pkg list | grep my_package
```

Should print: `my_package`

Check package metadata:

```bash
$ ros2 pkg prefix my_package
```

Should print path to install directory.

---

### Real Example: Camera Driver Package

```
camera_driver/
├── package.xml
├── CMakeLists.txt
├── src/
│   └── camera_driver_node.cpp
└── include/
    └── camera_driver.h
```

**package.xml:**
```xml
<package format="3">
  <name>camera_driver</name>
  <description>USB camera driver for ROS2</description>
  <depend>rclcpp</depend>
  <depend>sensor_msgs</depend>
  <depend>opencv</depend>  ← External dependency for image processing
</package>
```

**CMakeLists.txt:**
```cmake
project(camera_driver)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(OpenCV REQUIRED)

add_executable(camera_driver_node src/camera_driver_node.cpp)
ament_target_dependencies(camera_driver_node rclcpp sensor_msgs OpenCV)

install(TARGETS camera_driver_node DESTINATION lib/${PROJECT_NAME})
```

**Use:**
```bash
$ colcon build
$ source install/setup.bash
$ ros2 run camera_driver camera_driver_node
```

---

### Hands-On Lab & Practical Code References

To run a fully parameterized node and dynamically reconfigure it at runtime:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_core/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_core/README.md)
- **Source Code to Inspect:** `learning_core/parameter_echo_node.py`
- **Launch Orchestration:** `launch/all_core.launch.py`

#### 1. Run the Parameter Echo Node
```bash
cd ROS2_kits_ws
source install/setup.bash
ros2 run learning_core parameter_echo_node --ros-args -p echo_prefix:="[ROBOT_CORE]"
```

#### 2. Inspect and Dynamically Reconfigure Parameters
In a second terminal:

```bash
# 1. List active declared parameters
ros2 param list /parameter_echo_node

# 2. Query parameter value and description
ros2 param get /parameter_echo_node echo_prefix

# 3. Dynamically reconfigure without restarting the node process
ros2 param set /parameter_echo_node echo_prefix "[UPDATED_PREFIX]"
```

---

### How This Connects Forward

Next: In Article C1 ("Why Launch Files Are System Design"), you'll learn how to launch multiple packages together. One package (camera driver). Another package (obstacle detector). Another (planner). The launch file orchestrates them all.

---

### Learning Outcome Test

After reading, you should be able to:

1. **Create** a working package from scratch (three commands)
2. **Identify** what goes where (package.xml vs. CMakeLists.txt)
3. **Predict** what happens if a dependency is missing
4. **Fix** common package creation errors
5. **Explain** why package.xml and CMakeLists.txt are separate (metadata vs. build)

If you can create a package that compiles, you're ready for actual node writing.

---

*Word Count: 1,500*
*Reading Time: 10 minutes*
*Prerequisites: A0, A1, A2, A3, B1*
*Next: C1*