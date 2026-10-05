# Article CPS-07: Reciprocal Collision Avoidance & Dynamic Nav2 Costmaps

**Pedagogical Layer:** Motion Planning & Spatial Safety  
**Focus Area:** Velocity Obstacles (VO), Optimal Reciprocal Collision Avoidance (ORCA), and Nav2 Dynamic Footprint Injection  
**Associated Package:** `cps_coordination/cps_coordination/peer_collision_avoidance.py`

---

## 1. The Multi-Robot Deadlock Problem

When multiple autonomous robots operate in narrow corridors, traditional single-robot Nav2 costmaps treat other robots as static obstacles. This results in **mutual blocking (deadlock)**, where both robots stop and execute oscillation recovery behaviors.

---

## 2. Velocity Obstacle (VO) Geometry

The Velocity Obstacle $VO_{A|B}(\mathbf{v}_B)$ is the set of all relative velocities $\mathbf{v}_A - \mathbf{v}_B$ that will result in a collision between robot $A$ (radius $r_A$) and robot $B$ (radius $r_B$) within time horizon $\tau$:

$$VO_{A|B}(\mathbf{v}_B) = \left\{ \mathbf{v} \;\Big|\; \exists t \in [0, \tau], \; t(\mathbf{v} - \mathbf{v}_B) \in D(\mathbf{p}_B - \mathbf{p}_A, r_A + r_B) \right\}$$

```text
                  Robot B (v_B)
                     ●──▶
                    / \
                   /   \   Velocity Obstacle Cone
                  /     \  (Forbidden Relative Velocities)
                 /       \
                /         \
               ●───────────●
             Robot A (v_A)
```

---

## 3. Optimal Reciprocal Collision Avoidance (ORCA)

ORCA splits the responsibility for avoiding collision equally between both agents: each robot adjusts its velocity by half the minimum avoidance vector $\mathbf{u}$:
$$\Delta \mathbf{v}_A = \frac{1}{2} \mathbf{u}, \qquad \Delta \mathbf{v}_B = -\frac{1}{2} \mathbf{u}$$

---

## 4. Practical Implementation with Nav2 Costmaps

In practice, inject peer robot positions into the local costmap using dynamic cylindrical footprint markers:

```python
marker = Marker()
marker.type = Marker.CYLINDER
marker.pose = peer_robot_pose
marker.scale.x = safety_radius * 2.0
marker.scale.y = safety_radius * 2.0
pub_peer_obstacle.publish(marker)
```

---

## 5. Summary & Key Takeaways

- Reciprocal avoidance prevents oscillation and corridor deadlocks.
- In [Article CPS-08](article_cps_08_observability_foxglove_and_prometheus.md), we build enterprise telemetry and monitoring.
