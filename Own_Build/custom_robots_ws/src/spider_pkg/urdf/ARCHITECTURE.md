# Model Architecture

```text
base_footprint → base_link → body/head/abdomen
                         ├── six legs: coxa → femur → tibia → tarsus
                         └── lidar_link → ray-sensor plugin → /scan
```

The final Gazebo plugin section loads `libspider_gazebo_gait_plugin.so`. The model therefore joins visual geometry, physics, sensor definition, and the package-built movement plugin in one description.
