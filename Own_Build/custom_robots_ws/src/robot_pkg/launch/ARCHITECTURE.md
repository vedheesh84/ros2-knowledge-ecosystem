# Launch Architecture

Launch files orchestrate existing components; they do not define robot geometry. Most start `robot_state_publisher`, then either RViz or Gazebo plus `spawn_entity.py`. Navy mapping adds `slam_toolbox`; Navy navigation includes Nav2 and uses the saved map. Several Gazebo launches execute a cleanup command before starting, so avoid running them concurrently.

When troubleshooting, first run the RViz/display launch, then Gazebo, then mapping/navigation. This isolates description, simulation, and autonomy failures.
