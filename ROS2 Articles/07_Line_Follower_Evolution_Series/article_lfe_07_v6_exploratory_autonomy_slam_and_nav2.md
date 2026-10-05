# Article LFE-07: V6 — Exploratory Autonomy: Removing Line Constraints with LiDAR SLAM

**Pedagogical Layer:** Spatial Intelligence & Unconstrained Mobile Autonomy  
**Focus Area:** 2D LiDAR SLAM, Nav2 Costmaps, Frontier Exploration, and Environmental Freedom  
**Associated Package:** `line_follower_v6_exploratory`

---

## 1. Removing Environmental Scaffolding

In V1–V5, the robot required lines and tags on the floor.
In **V6**, all environmental constraints are removed:
- **Perception**: 2D 360-degree LiDAR + Wheel Encoders + IMU.
- **Mapping**: `slam_toolbox` generates a real-time 2D occupancy grid of walls and obstacles.
- **Planning**: Nav2 global and local costmaps compute collision-free trajectories in free space.

---

## 2. Frontier Exploration Search Algorithm

Frontier cells are defined as free-space grid cells ($P(\text{occ}) = 0$) directly adjacent to unknown grid cells ($P(\text{occ}) = -1$):

$$\mathcal{F} = \left\{ \mathbf{p} \in \text{FreeSpace} \;\Big|\; \exists \mathbf{q} \in \text{Neighbors}(\mathbf{p}), \; \text{Map}(\mathbf{q}) = -1 \right\}$$

The exploration node clusters contiguous frontier cells, computes their information gain, and commands Nav2 to navigate to the nearest unmapped frontier centroid.

---

## 3. Summary & Lessons Learned

V6 completes the evolution: the robot has graduated from a reactive line tracker to a fully autonomous explorer. In [Article LFE-08](article_lfe_08_capstone_evolutionary_synthesis.md), we synthesize the entire architectural journey.
