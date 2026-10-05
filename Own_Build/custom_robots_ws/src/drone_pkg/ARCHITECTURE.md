# `drone_pkg` Architecture

```text
drone.urdf + STL meshes ──> robot_state_publisher ──> TF ──> RViz
           └──> Gazebo spawn (entity: drone by default)
                   ▲                  │
/cmd_vel ──> manual_drone_controller ─┴── SetEntityState service
    └──> propeller_spinner.py ──> /joint_states ──> visible rotor spin
```

`drone_gazebo.launch.py` starts Gazebo, publishes the robot description, spawns the entity, and can start the controller and RViz. `drone_rviz.launch.py` is the lighter display path. `manual_drone_controller.cpp` converts linear X/Y/Z and angular Z commands into pose updates through Gazebo's `SetEntityState` service. `propeller_spinner.py` independently publishes rotating propeller joint states; it accelerates when command traffic arrives.

The URDF supplies the visual/collision geometry and Gazebo joint trajectory plugin. `worlds/` holds the simulation environment. The `docs/USAGE.md` document is the command reference; `scripts/` regenerates meshes or runs the animation helper.
