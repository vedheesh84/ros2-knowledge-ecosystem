# Assessment — `spider_pkg`

**Score: 72/100 — strongest original ROS 2 implementation; physical and experimental depth still needed.**

## What is present

This ament-CMake package uses a parameterised Xacro model with eight legs, LiDAR, Gazebo physics settings, and a custom model plugin. `spider_gait_node.cpp` subscribes to `cmd_vel` and generates leg joint states. `spider_gazebo_gait_plugin.cpp` independently consumes `cmd_vel`, applies an animated gait, moves the model pose, and publishes odometry/TF. Mapping launches add SLAM Toolbox using `/scan`.

## Strengths

- The custom C++ ROS node and Gazebo plugin are substantial original work, with configurable gait parameters, command timeout, mutex protection, and ROS/Gazebo integration.
- Xacro use is appropriate: one reusable leg macro constructs the eight leg chains, reducing duplication.
- The package has a coherent progression from RViz gait display to Gazebo movement to LiDAR-based mapping.
- Topic/TF intentions are understandable: `/cmd_vel` drives behaviour, `/joint_states` drives articulation, and the plugin publishes `odom → base_footprint`.

## Verified issues and feedback

| Priority | Finding | Why it matters | Required action |
|---|---|---|---|
| High | The plugin disables gravity, fixes height at `Z=0.04`, and directly overwrites world pose/joint position on every update. | This is kinematic animation, not a physically valid legged-robot simulation; terrain, contact, slip, and stability are bypassed. | State this limitation clearly, or use joint torque/position controllers with contact dynamics and evaluate locomotion. |
| High | Documentation calls it a “hexapod-style” spider, but the Xacro and C++ arrays define eight legs. | This factual inconsistency weakens technical credibility. | Correct all references to octopod/eight-legged spider, or reduce the model to six legs. |
| Medium | Both the standalone gait node and Gazebo plugin act on `cmd_vel`; the plugin drives joints directly while the node publishes the same joint states. | Ownership of the joint state is ambiguous and may create conflicting visual/simulation behaviour. | Pick one authoritative gait/controller path in Gazebo; make the other RViz-only or namespace/remap it. |
| Medium | The plugin may initialise/shut down global `rclcpp` from a Gazebo library and spins its own executor thread. | Plugin lifecycle and shutdown can become fragile in multi-plugin or multi-robot processes. | Use a documented Gazebo-ROS integration pattern, unique node names/namespaces, and explicit lifecycle tests. |
| Medium | Odometry reports commanded velocities and imposed pose rather than measured physics; no covariance is set. | SLAM results may look valid while concealing unrealistic localisation assumptions. | Label it as ideal odometry; publish realistic noise/covariance and evaluate mapping error. |
| Medium | No gait analysis, terrain tests, or SLAM metrics are included. | PG work needs measured performance and limitations. | Compare gait parameters/worlds; report speed, stability proxy, mapping accuracy, CPU use, and failures. |

## PG-level improvement path

1. Resolve the project identity: eight-legged kinematic mapping demonstrator, or physically simulated legged robot.
2. For a kinematic demonstrator, centralise gait generation in one component and document ideal odometry explicitly.
3. For a physical robot, add actuators/controllers, contact tuning, body stability control, and sensor noise.
4. Design experiments across speed/gait/terrain settings and quantify travel speed, tracking error, map quality, and failure modes.
5. Add C++ unit tests for gait phase/joint-limit outputs and integration tests for command timeout, TF, scan, and map availability.

## Assessment conclusion

This is the strongest project because it has a coherent system architecture and meaningful custom C++ work. It is one careful scope decision and a proper evaluation plan away from a strong PG prototype.
