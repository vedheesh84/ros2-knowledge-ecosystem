# Postgraduate Assessment Pack — ROS 2 Robot Projects

**Assessment basis:** static review of the extracted source code, package metadata, launch files, robot descriptions, configuration, and supplied documentation on 27 August 2026. XML and Python syntax were validated. ROS 2/Gazebo were not installed in this Windows review environment, so no claim is made that a full `colcon build` or simulation run passed.

## Executive judgement

This is a credible **prototype portfolio**, not yet a postgraduate-ready robotics software submission. It demonstrates broad practical exposure to ROS 2, URDF/Xacro, Gazebo, RViz, controllers, sensors, SLAM, Nav2, C++, and CAD assets. The strongest evidence is the custom spider gait node and Gazebo plugin. The main gap is engineering maturity: reproducibility, testing, clean project boundaries, launch reliability, and evidence-based evaluation are incomplete.

| Project | Score | Position now |
|---|---:|---|
| `robot_pkg` | 56/100 | Broad exploratory work; needs consolidation into one validated system. |
| `balancing_robot_description` | 62/100 | Polished visual/simulation prototype; “self-balancing” claim is not demonstrated. |
| `cad_description` | 65/100 | Strong robot description and sensors; control/autonomy layer is incomplete. |
| `drone_pkg` | 68/100 | Good interactive visual prototype; it is pose control, not flight simulation. |
| `spider_pkg` | 72/100 | Best original engineering; needs physical validity, tests, and cleaner lifecycle handling. |
| **Portfolio overall** | **65/100** | **Passable prototype standard; below a strong PG project standard.** |

Scores weight technical correctness (30%), system design (25%), reproducibility/testing (25%), and documentation/professional practice (20%). A score does not penalise an educational scope; it penalises claims that exceed the implementation or cannot be reproduced.

## Common priority actions

1. Create a Ubuntu/ROS 2 Humble (or declared target) installation guide with exact dependencies, version pins, `rosdep` command, and one verified clean-build log per package.
2. Replace fixed `TimerAction` delays and process-killing launch commands with event-driven launch sequencing and scoped process management.
3. Add automated checks: `ament_lint_auto`, `colcon test`, URDF/Xacro validation, launch smoke tests, and topic/TF assertions.
4. Treat each package as a focused contribution with a stated problem, requirements, architecture, experiment, result, limitation, and next step.
5. Record runtime evidence: screenshots/video, `ros2 topic hz`, `ros2 run tf2_tools view_frames`, map quality metrics, and a table of tested scenarios.

Read the individual reports for project-specific evidence and a practical improvement plan.
