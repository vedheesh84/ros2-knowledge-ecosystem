# Assessment — `drone_pkg`

**Score: 68/100 — thoughtful interactive demonstration, but not a flight-control simulator.**

## What is present

`drone_pkg` supplies FreeCAD assets, a URDF, Gazebo/RViz launch paths, a C++ `manual_drone_controller`, and a Python propeller animator. The controller receives `/cmd_vel` and calls Gazebo’s `SetEntityState`; the spinner publishes propeller `JointState` messages. The documentation correctly warns that it is not PX4/MAVLink/aerodynamic flight control.

## Strengths

- The separate C++ controller and Python visual animator are readable and parameterised.
- Command timeouts, speed limits, a minimum altitude, entity name, and service/topic parameters are good defensive design choices.
- The documentation explicitly names the `/cmd_vel` mapping and distinguishes this from a real flight stack.
- URDF/mesh packaging is consistent, and the launch exposes useful arguments.

## Verified issues and feedback

| Priority | Finding | Why it matters | Required action |
|---|---|---|---|
| High | Motion is achieved by repeatedly teleporting Gazebo link/entity state with `SetEntityState`; it does not model thrust, gravity response, attitude, drag, actuator dynamics, or control-loop stability. | It cannot support claims about drone dynamics, flight control, or realistic autonomy. | Label it strictly as kinematic visual control, or integrate a real simulator plugin/flight stack and evaluate it. |
| High | `manual_drone_controller` and the propeller spinner use wall/clock timing differently from Gazebo, while the launch enables simulation time. | Paused/slow simulation can desynchronise command, pose, and propeller animation. | Use a consistent ROS/simulation clock and test pause, reset, and real-time factor changes. |
| Medium | The launch writes to a fixed `/tmp/drone_pkg_gazebo.urdf`; entity/TF naming mixes `drone::base_link` (Gazebo scoped name) with unscoped `base_link` TF. | Multiple instances and TF debugging become brittle. | Generate unique files or avoid files; namespace TF/topics and test two simultaneous drones. |
| Medium | Each update sends five async service requests (base plus four propellers) at up to 40 Hz without back-pressure. | Slow Gazebo services can accumulate requests and produce lag. | Control only the base with a proper plugin; animate joints through one joint-state path or rate-limit/coalesce requests. |
| Medium | No unit, integration, or scenario tests demonstrate bounds, timeout behaviour, or service failure handling. | The defensive code is not verified. | Add unit tests for mapping/clamping and a Gazebo launch test for command response. |

## PG-level improvement path

1. Choose a defensible scope: visual kinematic demonstrator **or** flight-control research.
2. For the former, add deterministic trajectory tests and two-drone namespace support.
3. For the latter, integrate PX4 SITL/Gazebo (or a validated dynamics plugin), IMU/GPS/barometer sensors, and an attitude/position controller.
4. Report step response, altitude error, yaw error, settling time, and disturbance recovery.

## Assessment conclusion

This is a good software prototype with more custom logic than a static robot model. Its key limitation is conceptual: visual pose updates are not flight simulation. Honest scoping plus tests would make it a solid PG software-engineering component; real dynamics would make it a robotics-control project.
