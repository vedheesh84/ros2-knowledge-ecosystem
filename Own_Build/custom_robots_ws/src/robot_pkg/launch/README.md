# Launch Files

Each file is a ROS 2 Python launch recipe. Select it by model and goal; all are installed with the package.

| File | Scenario |
|---|---|
| `display_robot`, `demo_launch`, `rviz` | RViz-focused description demonstrations. |
| `gazebo`, `gazebo_rviz`, `test_gazebo` | General vehicle Gazebo tests. |
| `cat_gazebo`, `fusion_car`, `gaja_launch` | Named model demonstrations. |
| `human_gazebo` | Humanoid plus ros2_control controllers. |
| `navy_launch`, `navy_mapping_launch`, `navy_nav_launch` | Navy base simulation, mapping, and navigation. |
| `teleop` | Keyboard velocity publisher. |

Run one with `ros2 launch robot_pkg <file>.py` after building and sourcing the workspace.
