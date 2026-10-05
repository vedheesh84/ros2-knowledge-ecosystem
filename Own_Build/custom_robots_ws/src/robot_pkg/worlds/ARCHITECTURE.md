# World Architecture

```text
world file ──> Gazebo server
robot URDF ──> spawned entity in that world
robot sensors ──> readings depend on world geometry
```

Changing obstacle placement changes LiDAR scans and consequently SLAM/Nav2 behaviour, without requiring any change to the robot package.
