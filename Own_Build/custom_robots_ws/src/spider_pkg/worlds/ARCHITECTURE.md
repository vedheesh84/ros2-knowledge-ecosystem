# World Architecture

Gazebo loads a world before it spawns the spider. The world determines collision geometry that the LiDAR ray sensor detects. In the mapping workflow those scans feed SLAM Toolbox, so `spider_map.world` is part of the map-generation pipeline.
