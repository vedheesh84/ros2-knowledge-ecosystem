# ydlidar_ros2 (SDK Support Files)

This directory contains YDLiDAR SDK support files used by the `ydlidar_ros2_driver` package.

---

## Important Note

**This is NOT a ROS2 package.** It contains only SDK support files and configuration.

The actual ROS2 driver is located at: [ydlidar_ros2_driver](../ydlidar_ros2_driver/README.md)

---

## Contents

```
ydlidar_ros2/
├── sdk/        # YDLiDAR C++ SDK library source
└── params/     # LiDAR model-specific configuration files
```

### SDK Directory

Contains the YDLiDAR SDK library which provides:
- Serial communication with LiDAR hardware
- Scan data parsing and processing
- Device configuration and control

### Params Directory

Model-specific parameter configurations for various YDLiDAR models.

---

## Usage

These files are automatically used by the `ydlidar_ros2_driver` package. No direct interaction is typically required.

To use the LiDAR driver, see [ydlidar_ros2_driver documentation](../ydlidar_ros2_driver/README.md).

---

## Related Packages

- [ydlidar_ros2_driver](../ydlidar_ros2_driver/README.md) - ROS2 driver for YDLiDAR sensors
- [lidar_bringup](../sensors/lidar_bringup/README.md) - LiDAR launch wrapper
