# Launch Architecture

The launch file is the coordinator; `urdf/` owns the model and `rviz/` owns the view. `use_gazebo:=false` removes physics/spawning while retaining the model-publishing route.
