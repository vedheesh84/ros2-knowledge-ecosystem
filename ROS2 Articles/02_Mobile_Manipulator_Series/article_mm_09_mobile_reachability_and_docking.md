## MM 09: MOBILE REACHABILITY ENVELOPES & PRECISION BASE DOCKING

*Purpose: Master the spatial interplay between base navigation and arm manipulation. Analyze the mobile reachability envelope, understand why stopping tolerances in Nav2 dictate arm success, and design optimal base docking approach vectors.*

### Must Answer
- What is the Mobile Reachability Envelope, and why is the optimal grasping zone an annular ring in front of the base?
- What happens when a mobile base stops too far ($> 0.35\text{ m}$) or too close ($< 0.15\text{ m}$) to the target?
- How do we calculate the optimal Nav2 base docking goal from a detected 3D object position?
- What are navigation goal tolerances (`xy_goal_tolerance`, `yaw_goal_tolerance`), and how do they impact arm IK feasibility?
- How do pre-docking alignment maneuvers ensure the object enters the arm's peak manipulability sweet spot?

### Key Insight
Nav2 navigates the robot across meters of warehouse floor; precision docking places the robot within the exact 5-centimeter window where arm manipulability is maximized and joint limits are safely avoided.

---

### 1. The Mobile Reachability Sweet Spot

An articulated arm mounted on a mobile chassis has physical workspace limits:
- **Outer Reach Limit ($R_{\max} = 0.325\text{ m}$)**: Arm is fully outstretched; approaching a boundary singularity ($w(\mathbf{q}) \to 0$).
- **Inner Self-Collision Limit ($R_{\min} = 0.120\text{ m}$)**: Arm cannot descend without colliding with chassis bumper or front wheels.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MOBILE REACHABILITY ZONES                           │
│                                                                             │
│                    /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\                               │
│                   /  OUT-OF-REACH ZONE       \                              │
│                  /  ┌─────────────────────┐   \                             │
│                 /   │ OPTIMAL SWEET SPOT  │    \                            │
│                |    │  (r = 0.20 - 0.28m) │     |                           │
│                |    │  w(q) is MAXIMIZED  │     |                           │
│                |    │  ┌───────────────┐  │     |                           │
│                 \   │  │ SELF-COLLISION│  │    /                            │
│                  \  │  │  (r < 0.15m)  │  │   /                             │
│                   \ └──┴───────┬───────┴──┘  /                              │
│                    \___________│____________/                               │
│                            ┌───┴───┐                                        │
│                            │ Base  │                                        │
│                            └───────┘                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Computing the Optimal Nav2 Docking Pose

Given a detected object at global map coordinates $\mathbf{p}_{\text{obj}} = [x_{\text{obj}}, y_{\text{obj}}]^T$ and desired approach distance $d_{\text{optimal}} = 0.24\text{ m}$:

1. **Calculate Approach Heading ($\theta_{\text{base}}$)**:
   $$\theta_{\text{base}} = \text{atan2}(y_{\text{obj}} - y_{\text{robot}}, x_{\text{obj}} - x_{\text{robot}})$$
2. **Compute Base Target Coordinate**:
   $$x_{\text{goal}} = x_{\text{obj}} - d_{\text{optimal}} \cos(\theta_{\text{base}})$$
   $$y_{\text{goal}} = y_{\text{obj}} - d_{\text{optimal}} \sin(\theta_{\text{base}})$$
3. **Assemble `geometry_msgs/msg/PoseStamped` Goal** with yaw orientation quaternion $q_z = \sin(\theta_{\text{base}}/2), q_w = \cos(\theta_{\text{base}}/2)$.

---

### 3. Nav2 Goal Tolerances vs. Arm IK Feasibility

Standard Nav2 navigation defaults to:
- `xy_goal_tolerance: 0.15` ($\pm 15\text{ cm}$)
- `yaw_goal_tolerance: 0.25` ($\pm 14.3^\circ$)

For mobile manipulation, a $15\text{ cm}$ positioning error exceeds the entire dextrous sweet spot of the arm!
**Solution**: Configure precision controller profiles in Nav2 (`xy_goal_tolerance: 0.03`, `yaw_goal_tolerance: 0.05`) for final docking waypoints.

---

### 4. Hands-On Lab & Practical Code References

#### 1. Executing Mobile Pick-and-Place Demo:
```bash
# Run Demo 06: Coordinated navigation docking + arm manipulation
ros2 run mobile_manipulator_demos demo_06_mobile_pick_place.py
```
- Source: [`ros2_mobile_manipulator_kit/src/mobile_manipulator_demos/scripts/demo_06_mobile_pick_place.py`](file:///e:/Intelligent%20Systems%20Knowledge%20Ecosystem/02%20—%20Domains/ROS2/Ros2%20learning%20kits/ros2_mobile_manipulator_kit/src/mobile_manipulator_demos/scripts/demo_06_mobile_pick_place.py)
