# `spider_pkg` Architecture

```text
spider.urdf.xacro ──> robot_state_publisher ──> TF ──> RViz
       │                         ▲
       └── Gazebo spawn           │ /joint_states
               │                  │
               ├── spider_gazebo_gait_plugin <── /cmd_vel
               │       ├── moves model in Gazebo
               │       └── publishes /odom
               ├── LiDAR Gazebo plugin ──> /scan
               └── spider_gait_node <── /cmd_vel ──> /joint_states
                                           (animated leg joints)
                                          
/scan + /odom + TF ──> SLAM Toolbox ──> /map (mapping launches only)
```

## Runtime components

- `spider_gait_node.cpp` creates the visible walking cycle. It listens to `cmd_vel` and publishes `sensor_msgs/JointState` for the leg joints.
- `spider_gazebo_gait_plugin.cpp` is a shared Gazebo plugin. It receives `cmd_vel`, changes the simulated model pose, and publishes `nav_msgs/Odometry` on `odom`.
- `spider.urdf.xacro` defines the body, six parameterised legs, LiDAR, contact/friction settings, and loads the Gazebo plugin.
- `slam_toolbox.yaml` configures online asynchronous mapping with `/scan` as input.

## Launch roles

`display.launch.py` is the lightest option (RViz + gait node). `gazebo.launch.py` is the configurable full simulation. `spider_launch.launch.py` starts the normal Gazebo scenario, and `spider_mapping.launch.py` adds SLAM Toolbox for map creation. `worlds/` supplies an empty arena and a mapping world.

## Integration caution

The animation node and the Gazebo plugin both react to the global `cmd_vel` topic. This is intentional for the demo, but it means a second robot using the same topic will also move unless namespaced.
