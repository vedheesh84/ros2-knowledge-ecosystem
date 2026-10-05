## A3: WORKSPACES, PACKAGES, BUILDS — WHY ROS2 IS STRUCTURED THIS WAY

*Purpose: Prevent cargo-cult folder copying. Explain why colcon exists, why overlay workspaces matter, why sourcing changes reality.*

### Must Answer
- Why does ROS2 care about folder structure?
- What is a workspace? What is a package?
- Why do you have to source setup.bash?
- What does colcon actually do?

### Key Insight
ROS2's folder structure isn't arbitrary. It enables parallel development, environment isolation, and automatic build management. Understand the structure, and you understand modularity.

---

### The Mental Model: Nesting Dolls of Organization

Imagine Russian nesting dolls:

```
[Workspace] ← Top level (contains everything for your robot)
  └─ [src] ← Source code directory
      └─ [Package 1] ← A reusable unit (e.g., camera_driver)
          ├─ package.xml ← Metadata (name, dependencies)
          ├─ CMakeLists.txt ← Build instructions
          └─ [src] ← The actual code
      └─ [Package 2] ← Another unit (e.g., obstacle_detector)
  └─ [build] ← Compiled binaries (created by colcon)
  └─ [install] ← Final executables (created by colcon)
```

Why this structure?

1. **Modularity.** Each package is standalone. Can be reused, tested independently, shared.
2. **Scalability.** Add 50 packages? Same structure. Doesn't break.
3. **Environment Isolation.** Your ROS2 code doesn't interfere with system Python or C++.
4. **Build Automation.** Colcon knows how to compile everything without you specifying it.

---

### A Workspace

A **workspace** is a folder containing your robot's entire codebase.

Typical structure:
```
my_robot_ws/
├── src/               ← All source code lives here
├── build/             ← Build artifacts (compiler-generated)
├── install/           ← Final executables
└── log/               ← Build logs
```

Why have a workspace? **Isolation.**

Your workspace is separate from the system's Python, C++, and ROS2 installations. You can work on one robot without affecting another, or affecting your system.

Commands:
```
$ mkdir -p my_robot_ws/src
$ cd my_robot_ws
$ colcon build   ← Builds everything in src/
```

After building, you get `/build` and `/install` directories. `/install` contains the final executables.

---

### A Package

A **package** is a folder containing a single, reusable unit of code.

Example: `camera_driver` package. Contains:
- Code that interfaces with the camera
- Unit tests for camera code
- Documentation
- Dependencies it needs

Typical package structure:
```
camera_driver/
├── package.xml         ← Metadata (name, version, dependencies)
├── CMakeLists.txt      ← Build instructions
├── src/                ← Source code
│   └── camera_driver.cpp
└── include/            ← Header files
    └── camera_driver.h
```

**Why packages?** **Reusability and clarity.**

If you write a camera driver, you want to use it in multiple robots. Package it cleanly, document it, and share it. Another roboticist installs your package, uses your code, doesn't copy-paste.

---

### package.xml: Metadata for Your Package

Every package has a `package.xml` file. Declares:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>camera_driver</name>
  <version>1.0.0</version>
  <description>Publishes images from USB camera</description>
  <maintainer email="you@example.com">You</maintainer>
  <license>Apache-2.0</license>
  
  <depend>rclcpp</depend>      ← Depends on ROS2 C++ library
  <depend>sensor_msgs</depend> ← Depends on sensor message types
</package>
```

Why? So other packages know: "camera_driver needs rclcpp and sensor_msgs. I'll provide them."

When you run `colcon build`, it reads all package.xml files and figures out the build order. Package A depends on Package B? Build B first, then A. Automatic.

---

### CMakeLists.txt: Build Instructions

Tells the compiler how to build your code.

```cmake
cmake_minimum_required(VERSION 3.5)
project(camera_driver)

# Tell CMake where ROS2 is
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

# Build the executable
add_executable(camera_driver_node src/camera_driver.cpp)
ament_target_dependencies(camera_driver_node rclcpp sensor_msgs)

# Install the executable to /install
install(TARGETS camera_driver_node DESTINATION lib/${PROJECT_NAME})
```

You don't need to understand this deeply. But know: it says "take this C++ code, find ROS2 libraries, compile it, put the executable in install."

---

### Colcon: The Build Orchestrator

**Colcon** is the build system. You tell it to build, and it:

1. **Discovers** all packages in `src/`
2. **Reads** their package.xml files
3. **Determines** build order (respecting dependencies)
4. **Compiles** each in order
5. **Places** executables in `install/`

Command:
```
$ cd my_robot_ws
$ colcon build
```

Colcon reads every package.xml in `src/`, resolves dependencies, and builds. You don't manually compile. It's automatic.

```
$ colcon build
Starting >>> camera_driver
Finished >>> camera_driver [1.2s]
Starting >>> obstacle_detector
Finished >>> obstacle_detector [2.3s]
Starting >>> path_planner
Finished >>> path_planner [1.8s]
Summary: 3 packages built in 5.3s
```

Colcon figures out the order, parallelizes, and reports.

---

### Sourcing: The Magic Line

Before running nodes, you must source `setup.bash`:

```
$ source install/setup.bash
```

What does this do? **It modifies your environment.**

Specifically:
- Adds `install/lib` to your PATH (so you can run executables)
- Sets ROS2 variables (`ROS_DISTRO`, `ROS_PACKAGE_PATH`, etc.)
- Updates library paths so compiled code finds dependencies

Without sourcing, your shell doesn't know where your executables are. With sourcing, everything works.

**Why can't ROS2 just do this automatically?** Because ROS2 supports **overlay workspaces**.

---

### Overlay Workspaces: Stacking Environments

You can have multiple workspaces stacked on top of each other.

```
System ROS2
    ↓
Base workspace (e.g., /opt/ros/humble)
    ↓
Your workspace (e.g., ~/my_robot_ws)
```

When you source your workspace's `setup.bash`, it:
1. Loads the base workspace first
2. Then adds your workspace on top

So you get everything from base, plus your new code.

Why? **Development without breaking anything.**

You can work on a new feature in your workspace without affecting other robots using the base workspace.

---

### Common Mistakes (Understanding Why Structure Matters)

**Mistake 1: Putting Everything in One Folder**

Wrong:
```
my_robot/
├── camera_code.cpp
├── detector_code.cpp
├── planner_code.cpp
```

Why it breaks: No organization. Hard to reuse. Hard to build. Hard to test one component.

Right:
```
my_robot_ws/src/
├── camera_driver/
│   ├── package.xml
│   └── src/camera_code.cpp
├── obstacle_detector/
│   ├── package.xml
│   └── src/detector_code.cpp
```

---

**Mistake 2: Forgetting to Source**

```
$ cd my_robot_ws
$ colcon build
$ ros2 run camera_driver camera_driver_node
Error: Package 'camera_driver' not found
```

Why? You didn't source. Shell doesn't know about your package.

Fix:
```
$ source install/setup.bash
$ ros2 run camera_driver camera_driver_node
```

---

**Mistake 3: Editing Files in `/install`**

The `/install` directory is generated by `colcon`. If you edit files there, colcon overwrites them next build. Always edit in `/src`.

---

### The Development Cycle

1. **Create** a package in `src/`
2. **Write** code
3. **Build** with `colcon build`
4. **Source** with `source install/setup.bash`
5. **Run** with `ros2 run package_name node_name`
6. **Edit** code (back to step 2)

Repeat step 2-6 many times. Build once (or when dependencies change).

---

### Hands-On Lab & Practical Code References

To inspect real-world package manifests, colcon build output, and overlay sourcing:

- **Workspace Path:** [`ROS2_kits_ws/src/ros2_learning_common/learning_core/`](../Ros2%20learning%20kits/ROS2_kits_ws/src/ros2_learning_common/learning_core/README.md)
- **Manifests to Inspect:**
  - `package.xml` — Defines runtime/build dependencies (`rclpy`, `std_msgs`)
  - `setup.py` — Defines entry points in `console_scripts` (`hello_node = learning_core.hello_node:main`)

#### 1. Selective Package Build
```bash
cd ROS2_kits_ws

# Build only the core learning package
colcon build --packages-select learning_core
```

#### 2. Environment Sourcing & Executable Verification
```bash
# Source the newly generated overlay
source install/setup.bash

# Check that the shell locates the executable inside install/
which ros2
ros2 pkg executables learning_core
```

---

### How This Connects Forward

Next: In Article A3b ("From Package Structure to Running Node"), you'll learn how to take this structure and actually create a working package. How do you write the package.xml? The CMakeLists.txt? How do you verify it works?

---

### Learning Outcome Test

After reading this article, you should be able to:

1. **Explain** why ROS2 uses workspaces and packages (not just folders)
2. **Predict** what colcon does given a set of package.xml files
3. **Identify** mistakes in folder structures (wrong nesting, missing files)
4. **Describe** the sourcing process and why it's necessary
5. **Reason** about overlay workspaces: "If I source workspace B on top of A, I get..."

If you can do these, you understand ROS2's structure, not just following commands blindly.

---

*Word Count: 1,900*
*Reading Time: 12 minutes*
*Prerequisites: A0, A1, A2*
*Next: A3b*