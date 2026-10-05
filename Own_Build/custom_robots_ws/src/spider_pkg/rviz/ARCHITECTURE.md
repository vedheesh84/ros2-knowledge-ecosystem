# RViz Architecture

The display configuration subscribes to TF and joint states to draw the spider. In mapping mode it also visualises the LiDAR and occupancy map. A missing display normally indicates an absent topic or transform upstream, not a problem in the `.rviz` file.
