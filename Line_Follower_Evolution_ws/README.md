# Line Follower Evolution Workspace (`Line_Follower_Evolution_ws`)

**A Grounded Pedagogical Journey Through 4 Discrete Robotic Intelligence Evolutions**

This workspace implements the progressive evolutionary roadmap of autonomous ground robotics, demonstrating how physical limitations drive mathematical control, symbolic graph reasoning, and spatial mapping autonomy.

---

## 1. The 4 Evolutionary Generations

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             THE 4 GENERATIONS OF ROBOTIC EVOLUTION                               │
├──────────────────────┬────────────────────────┬─────────────────────────┬────────────────────────┤
│ GENERATION 1 (V1)    │ GENERATION 2 (V2–V3)   │ GENERATION 3 (V4–V5)    │ GENERATION 4 (V6)      │
│ Reactive Baseline    │ Physical Intelligence  │ Symbolic Intelligence   │ Spatial Intelligence   │
├──────────────────────┼────────────────────────┼─────────────────────────┼────────────────────────┤
│ • 2 IR Thresholds    │ • 8-Channel IR Array   │ • Topological Graph     │ • 2D 360° LiDAR        │
│ • Bang-Bang PWM      │ • Weighted Centroid    │ • AprilTag Visual Nodes │ • SLAM Toolbox Mapping │
│ • Exposes Overshoot  │ • Inner Velocity PID   │ • Edge State Machine    │ • Nav2 Costmaps        │
│ • No State Memory    │ • Gyro Damping (IMU)   │ • Rollback Recovery     │ • Frontier Exploration │
└──────────────────────┴────────────────────────┴─────────────────────────┴────────────────────────┘
```

---

## 2. Package Overview

| Package | Generation | Core Focus & Capabilities | Key Nodes |
|---|---|---|---|
| **`line_follower_v1_reactive`** | V1 | Baseline 2-sensor reactive threshold tracker | `reactive_threshold_node`, `simulated_track_sensor` |
| **`line_follower_v2_v3_stabilized`** | V2–V3 | Physical intelligence: dynamics, IMU damping, 8-IR array | `sensor_array_processor`, `stabilized_motion_controller` |
| **`line_follower_v4_v5_topological`** | V4–V5 | Symbolic intelligence: graph navigation & node recovery | `topological_navigator_node`, `tag_detector_node` |
| **`line_follower_v6_exploratory`** | V6 | Spatial intelligence: unconstrained LiDAR SLAM & Nav2 | `frontier_explorer_node` |
| **`line_follower_evolution_bringup`** | Master | Unified multi-world simulation launcher | `master_evolution_selector.launch.py` |

---

## 3. Quick Start & Execution Recipes

### Build Workspace
```bash
cd "02 — Domains/ROS2/Line_Follower_Evolution_ws"
colcon build --symlink-install
source install/setup.bash
```

### Launch Individual Evolutionary Generations
```bash
# Generation 1 (V1 Reactive Baseline):
ros2 launch line_follower_v1_reactive v1_reactive_simulation.launch.py

# Generation 2 (V2-V3 Physical Dynamics & Stabilization):
ros2 launch line_follower_v2_v3_stabilized v2_v3_stabilized_simulation.launch.py

# Generation 3 (V4-V5 Symbolic Graph Navigation):
ros2 launch line_follower_v4_v5_topological v4_v5_topological_simulation.launch.py

# Generation 4 (V6 Exploratory Autonomous SLAM):
ros2 launch line_follower_v6_exploratory v6_exploratory_simulation.launch.py
```

### Universal Master Selector
```bash
ros2 launch line_follower_evolution_bringup master_evolution_selector.launch.py version:=v2_v3
```

---

## 4. Master Learning Series Curriculum

For comprehensive theory, physics proofs, and code walkthroughs, read the [Line Follower Evolution Learning Series](../ROS2%20Articles/07_Line_Follower_Evolution_Series/article_lfe_01_evolutionary_intelligence_framework.md).
