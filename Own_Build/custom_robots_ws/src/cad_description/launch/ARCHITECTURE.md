# Launch Architecture

The full launch reads `cad.urdf`, starts state publishing, conditionally includes Gazebo, spawns the entity, and opens RViz. The teleop launch is a command producer for the differential-drive plugin.
