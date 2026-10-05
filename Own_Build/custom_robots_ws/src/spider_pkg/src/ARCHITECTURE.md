# Runtime-Code Architecture

```text
/cmd_vel ──> gait node ──> /joint_states ──> robot_state_publisher/RViz
     └────> Gazebo plugin ──> simulated pose + /odom
```

The gait node is responsible for leg appearance, while the plugin is responsible for Gazebo movement and odometry. Keeping these roles separate avoids putting Gazebo headers in the visual animation node, but both must agree on topic and joint/model names.
