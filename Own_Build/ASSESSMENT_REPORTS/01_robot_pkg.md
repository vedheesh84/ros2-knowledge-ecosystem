# Assessment — `robot_pkg`

**Score: 56/100 — exploratory collection, not yet a coherent PG project.**

## What is present

The package includes a useful range of learning and demonstration artefacts: numbered URDF exercises; vehicles; a humanoid with `ros2_control`; a Navy mobile manipulator with LiDAR, mapping, and Nav2 launch paths; Gazebo worlds; maps; RViz profiles; and configuration for SLAM, Nav2, and controllers. The Navy sequence (`navy_launch`, `navy_mapping_launch`, `navy_nav_launch`) is the clearest candidate for a real project narrative.

## Strengths

- Broad ROS 2 exposure is visible in the package manifest and launch stack: state publishing, Gazebo spawning, sensors, SLAM Toolbox, Nav2, RViz, and controllers.
- The staged Navy workflow reflects a sound conceptual progression from simulation to mapping to navigation.
- The separate maps, worlds, RViz files, and YAML parameters show awareness that robotics systems need more than one source file.
- The incremental URDF files are useful teaching artefacts and can support a reflective learning narrative.

## Verified issues and feedback

| Priority | Finding | Why it matters | Required action |
|---|---|---|---|
| High | The package combines unrelated robot exercises, camera-server code, and a podcast reel agent. `dual_cam_server.py` imports a local `usb_camera` module from a user home path; `podcast_clip_agent.py` imports files that are not in this package. | The project boundary is unclear and those scripts are non-reproducible. A PG assessor cannot identify the claimed contribution or run the package cleanly. | Move non-ROS media/camera applications into separate repositories. Keep only the selected robotics contribution. |
| High | `package.xml` still says `TODO` for description and licence. | This is unfinished release metadata and undermines ownership, reuse, and professional presentation. | Write a specific description, add the real licence text/file, and update the maintainer details. |
| High | There are no automated tests or recorded runtime results. | SLAM/Nav2 claims need evidence of TF, scan, odometry, localisation, and goal completion—not just launch files. | Add a smoke-test matrix and record build/test output plus mapping/navigation results. |
| Medium | Several launch files use fixed delays and cleanup commands. The Navy launches use `pkill`; timing assumptions are machine-dependent. | This can terminate unrelated processes and makes startup fragile. | Remove broad `pkill`; use launch event handlers and unique namespaces/entity names. |
| Medium | The project has many models but no stated requirements, chosen use case, or comparison criteria. | Breadth is not a research contribution by itself. | Make Navy the main system and frame a question, e.g. mapping/navigation robustness in the warehouse world. |
| Medium | Root Python scripts are not installed by `CMakeLists.txt` and are not launched by the ROS package. | Their relationship to the package is accidental, confusing users and assessors. | Remove them or package them correctly in a separate package with declared dependencies. |

## PG-level improvement path

1. Split this into `robot_description_examples` (teaching material) and `navy_navigation` (assessed project).
2. State functional requirements: drive in simulation, publish LiDAR/odom/TF, build a map, localise on a saved map, and reach N goals without collision.
3. Build a launch-test that checks `/scan`, `/odom`, TF `map→odom→base_link`, and Nav2 action-server availability.
4. Evaluate three maps/world layouts or parameter variants. Report success rate, path length, completion time, and failure diagnosis.
5. Finish metadata, licensing, dependency list, and a reproducible setup guide.

## Assessment conclusion

There is strong evidence of hands-on learning, especially in the Navy pipeline. However, the present repository is an accumulation of experiments rather than a defendable PG software project. Focus and validation would raise it substantially.
