# Robot Descriptions

This directory is the source of robot geometry and joints. Plain `.urdf` files are direct XML; `.xacro` files support reusable properties/macros and are normally expanded by `xacro` when a launch starts.

The numbered files are incremental learning examples. `navy.urdf.xacro` is the main autonomous mobile-manipulator model; `robot*.xacro`, `gazebo_urdf.xacro`, `gaja.urdf`, and `fusion.urdf` are vehicle experiments; `human_robot.urdf` and `cat.urdf` are articulated examples.

Edit geometry here, then validate in RViz before testing Gazebo plugins.
