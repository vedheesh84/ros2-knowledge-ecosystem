# Spider Xacro Model

`spider.urdf.xacro` defines the mechanical body, six repeated leg chains, LiDAR link, joint limits, collision/inertial properties, and Gazebo-specific plugins. Xacro macros avoid duplicating the same leg structure six times.

Edit joint names carefully: `spider_gait_node.cpp` publishes the names declared here, and the Gazebo plugin is loaded from the model's `<gazebo>` section.
