## MM 10: NAV2 COSTMAP CONFIGURATION & DYNAMIC FOOTPRINT INFLATION

*Purpose: Master navigation safety for mobile manipulators. Understand 2D costmaps, inflation layers, clearing zones for pick-and-place tables, and dynamic footprint inflation between stowed and extended arm states.*

### Must Answer
- How do Nav2 Global and Local Costmaps prevent mobile manipulator collisions with surrounding obstacles?
- What is Dynamic Footprint Inflation, and why does an extended arm require a different 2D collision footprint than a stowed arm?
- How do costmap clearing zones prevent pick-and-place tables from being treated as impassable walls?
- What are Costmap Layers (Obstacle Layer, Voxel Layer, Inflation Layer), and how are they tuned?
- How do we update robot footprints dynamically over `/footprint` or via parameter callbacks?

### Key Insight
If the robot drives with its arm outstretched, its effective footprint expands by 30 cm; driving into a narrow doorway in this state will rip the arm off unless the costmap inflates dynamically to reflect arm posture.

---

### 1. The Costmap Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          NAV2 COSTMAP LAYER STACK                           │
│                                                                             │
│   [Static Map Layer]   ──▶ Global occupancy grid from SLAM (0 - 100)        │
│          │                                                                  │
│   [Obstacle Layer]     ──▶ Real-time 2D LiDAR points / LaserScan            │
│          │                                                                  │
│   [Voxel 3D Layer]     ──▶ 3D RGB-D point cloud obstacle voxelization       │
│          │                                                                  │
│   [Inflation Layer]    ──▶ Inscribes robot footprint buffer around obstacles│
│          ▼                                                                  │
│   [Master Costmap]     ──▶ Output cost grid consumed by Nav2 Planners       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Dynamic Footprint Switching: Stowed vs. Deployed

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DYNAMIC FOOTPRINT GEOMETRIES                        │
│                                                                             │
│   STOWED ARM CONFIGURATION (High-Speed Transit):                            │
│   Footprint: Compact rectangle [-0.15, -0.12] to [0.15, 0.12]               │
│   • Robot easily maneuvers through narrow 60cm doorways and tight aisles.   │
│                                                                             │
│   DEPLOYED ARM CONFIGURATION (Manipulation / Reaching):                     │
│   Footprint: Asymmetric expanded polygon [-0.15, -0.12] to [0.45, 0.12]     │
│   • Costmap expands to protect extended forearm and gripper from side walls.│
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Updating the Footprint in Real-Time:
The state machine publishes updated polygon points to `/global_costmap/footprint` and `/local_costmap/footprint`:
```python
from geometry_msgs.msg import Polygon, Point32

footprint_msg = Polygon()
# Add expanded 4-point polygon coordinates when arm deploys
footprint_pub.publish(footprint_msg)
```

---

### 3. Pick-and-Place Table Clearing Filters

When docking at a table, 2D LiDAR beams scan the table edge at $z = 0.20\text{ m}$. Nav2 marks the table as a lethal obstacle ($254$), preventing the robot from driving close enough to reach the object.

#### The Clearing Solution:
1. Use a **Range-Bounded Obstacle Layer**: Only mark obstacles between $z = 0.05\text{ m}$ (floor) and $z = 0.18\text{ m}$ (table clearance).
2. Configure **Approach Costmap Filters**: Temporarily mask out the target workstation zone during the final precision docking phase.

---

### 4. Hands-On Lab & Practical Code References

#### 1. Auditing Nav2 Configs:
- Nav2 Parameters: [`ros2_mobile_manipulator_kit/src/mobile_manipulator_bringup/config/simulation.rviz`](file:///e:/Intelligent%20Systems%20Knowledge%20Ecosystem/02%20—%20Domains/ROS2/Ros2%20learning%20kits/ros2_mobile_manipulator_kit/src/mobile_manipulator_bringup/rviz/simulation.rviz)
