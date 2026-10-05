# `balancing_robot_description` Architecture

```text
meshes/*.stl + urdf/selfbalance.urdf
            ├──> robot_state_publisher ──> TF ──> RViz
            └──> Gazebo spawn
                    └── differential-drive plugin <── /cmd_vel
                                             ├── wheel motion
                                             ├── joint states
                                             └── odometry
```

`self_balancing.launch.py` resolves the package paths, reads the URDF, starts state publishing, and conditionally includes Gazebo and RViz. The model contains Gazebo material, collision, joint-state publisher, and differential-drive plugin sections. Therefore it behaves as a wheel-driven simulation; it does not implement a true balance-control algorithm.

`setup.py` is the installation map: it places the mesh, URDF, launch, RViz, and FreeCAD generator into the installed package. If you add a new asset directory, also add it there or ROS will not find it after `colcon build`.
