# Assessment — `cad_description`

**Score: 65/100 — strong CAD/description work; incomplete robot-control project.**

## What is present

This ament-CMake package models a four-wheel mobile manipulator. `cad.urdf` ties together chassis, wheels, LiDAR, camera, LED bars, arm, wrist camera, and prismatic gripper fingers using STL assets. It includes Gazebo drive, LiDAR, camera, and joint-state plugins, plus RViz and teleop launches. A detailed FreeCAD learning path is a valuable teaching resource.

## Strengths

- The link/joint decomposition is substantial and appropriate for a mobile-manipulator model.
- Sensor definitions and Gazebo plugins demonstrate useful system integration beyond visual CAD.
- The FreeCAD guide gives a novice a concrete modelling sequence, part dimensions, and coordinate-frame guidance.
- Build metadata and asset installation are relatively clean.

## Verified issues and feedback

| Priority | Finding | Why it matters | Required action |
|---|---|---|---|
| High | The robot has a multi-joint arm and gripper but no ros2_control hardware interface, controllers, MoveIt configuration, or manipulation launch path. | The primary manipulation capability is present only as geometry; the system cannot demonstrate manipulation. | Add ros2_control transmissions/controllers and a MoveIt 2 configuration, then demonstrate a repeatable pick/place task. |
| High | The Gazebo launch uses global `pkill -9` cleanup and a fixed `/tmp/cad_robot_gazebo.urdf`. | This is unsafe and breaks parallel/reproducible runs. | Replace both with scoped, event-driven launch design. |
| Medium | No test suite or measured sensor/navigation/manipulation evidence exists. | The model’s behaviours must be verified rather than inferred from XML. | Add URDF and launch smoke tests; benchmark LiDAR/camera topics, drive odometry, and arm joint limits. |
| Medium | The CAD learning document references a local image path and a presumed user workspace. | Other students cannot access the reference or reproduce the guide exactly. | Put a licensable reference image in `docs/assets` or remove it; use package-relative paths. |
| Low | `cad_teleop.launch.py` only addresses base velocity. | It under-represents the arm/gripper capability. | Add named arm/gripper command examples and controller documentation. |

## PG-level improvement path

1. Define a task: autonomous indoor inspection or mobile pick-and-place.
2. Add actuated arm/gripper control with joint limits, trajectories, and collision checking.
3. Calibrate coordinate conventions for CAD exports; verify mesh origins and inertia assumptions.
4. Build an experiment: detect a visual target, navigate to a pose, plan an arm motion, and report success rate/error.
5. Include an architecture figure, test protocol, datasets/logs, and limitations.

## Assessment conclusion

The description work is credible and more detailed than a simple model package. To meet PG expectations, transform it from a CAD showcase into an evaluated mobile-manipulation system.
