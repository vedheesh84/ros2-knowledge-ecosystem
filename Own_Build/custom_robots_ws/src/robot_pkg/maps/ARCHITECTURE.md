# Map Architecture

```text
LiDAR /scan + odometry/TF ──> SLAM Toolbox ──> saved .pgm + .yaml
my_map.yaml ──> Nav2 map_server ──> /map ──> planner and costmaps
```

The image contains cells; the YAML gives those cells real-world position and scale. Editing the image without updating its metadata can shift or invert navigation results.
