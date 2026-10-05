## ARM 05: ANALYTICAL INVERSE KINEMATICS: GEOMETRIC DECOUPLING & LAW OF COSINES

*Purpose: Step-by-step mathematical derivation of the closed-form analytical Inverse Kinematics algorithm for the 5-DOF articulated robot arm. Learn geometric kinematic decoupling, wrist center projection, Law of Cosines triangle solving, and configuration branch selection.*

### Must Answer
- How does Pieper's Criterion allow 6-DOF and 5-DOF arms to be solved analytically in closed-form?
- What is kinematic decoupling, and how do we isolate the base yaw angle $q_1$ from the arm pitching joints?
- How do we calculate the intermediate Wrist Center $(r_w, z_w)$ by subtracting the tool vector?
- How does the Law of Cosines yield exact algebraic solutions for the elbow joint $q_3$?
- How do we calculate the shoulder joint $q_2$ and wrist pitch $q_4$, and how do we choose between Elbow-Up and Elbow-Down configurations?

### Key Insight
By projecting the end-effector backward along the gripper axis to find the wrist center position, the 3D Inverse Kinematics problem collapses into a simple 2D triangle that is solved in two trigonometric operations.

---

### 1. Kinematic Decoupling: Pieper's Criterion

In 1968, Donald Pieper proved that a 6-DOF manipulator has a closed-form analytical IK solution if:
1. Three consecutive joint axes intersect at a single point (e.g. a spherical wrist), OR
2. Three consecutive joint axes are parallel.

Our 5-DOF arm satisfies condition (2): Joints 2 (shoulder), 3 (elbow), and 4 (wrist pitch) are **all parallel**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     GEOMETRIC DECOUPLING DECOMPOSITION                      │
│                                                                             │
│             Z                                                               │
│             ▲                        (Elbow / Joint 3)                      │
│             │                               o                               │
│             │                              / \                              │
│             │                    Link 2   /   \   Link 3                    │
│             │                     (a_2)  /     \   (a_3)                    │
│             │                           /       \                           │
│             │              (Shoulder)  o         o Wrist Center (r_w, z_w)  │
│             │                          │          \                         │
│             │                   Link 1 │           \ Link 4 (d_5)           │
│             │                    (d_1) │            \                       │
│             │                          │             ▼ TCP (x, y, z)        │
│             └──────────────────────────┴─────────────────────────► r        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Step-by-Step Analytical Derivation

#### Step 1: Base Joint Angle ($q_1$)
The base joint $q_1$ controls the azimuth (yaw) of the vertical arm plane. It is calculated directly using the 2-argument arctangent:
$$q_1 = \text{atan2}(y, x)$$

#### Step 2: Wrist Center Projection $(r_w, z_w)$
Given the target TCP position $(x, y, z)$ and the target pitch angle $\theta_{\text{pitch}}$:
1. Compute the total radial distance in the horizontal plane: $r = \sqrt{x^2 + y^2}$.
2. Subtract the tool length vector ($d_5$) rotated at angle $\theta_{\text{pitch}}$:
   $$r_w = r - d_5 \cos(\theta_{\text{pitch}})$$
   $$z_w = (z - d_1) - d_5 \sin(\theta_{\text{pitch}})$$

The coordinate $(r_w, z_w)$ is the position of Joint 4 (wrist axis) relative to Joint 2 (shoulder axis).

#### Step 3: Elbow Joint Angle ($q_3$) via Law of Cosines
Consider the planar triangle formed by Shoulder (origin), Elbow, and Wrist Center:
- Side 1: $a_2 = 0.120\text{ m}$ (Upper arm)
- Side 2: $a_3 = 0.085\text{ m}$ (Forearm)
- Side 3: $D = \sqrt{r_w^2 + z_w^2}$ (Distance from shoulder to wrist)

By the Law of Cosines:
$$D^2 = a_2^2 + a_3^2 - 2 a_2 a_3 \cos(\pi - q_3) = a_2^2 + a_3^2 + 2 a_2 a_3 \cos(q_3)$$

Solving for $\cos(q_3)$:
$$\cos(q_3) = \frac{r_w^2 + z_w^2 - a_2^2 - a_3^2}{2 a_2 a_3}$$

> [!IMPORTANT]
> **Reachability Check**: If $|\cos(q_3)| > 1.0$, the target point is geometrically unreachable (the triangle cannot close).

The two physical solutions are:
- **Elbow-Up**: $q_3 = -\arccos(\cos(q_3))$ (Standard natural arm posture)
- **Elbow-Down**: $q_3 = +\arccos(\cos(q_3))$ (Reaching upward from beneath)

#### Step 4: Shoulder Joint Angle ($q_2$)
The shoulder angle is the difference between the angle to the wrist center ($\alpha$) and the internal triangle angle ($\beta$):
$$\alpha = \text{atan2}(z_w, r_w)$$
$$\beta = \text{atan2}(a_3 \sin(q_3), a_2 + a_3 \cos(q_3))$$
$$q_2 = \alpha - \beta$$

#### Step 5: Wrist Pitch Joint Angle ($q_4$)
Because $\theta_{\text{pitch}} = q_2 + q_3 + q_4$, we isolate $q_4$:
$$q_4 = \theta_{\text{pitch}} - (q_2 + q_3)$$

---

### 3. Production Python Implementation in `arm_kinematics`

```python
import math
from typing import Optional, Tuple

class InverseKinematics:
    def __init__(self, d1=0.096, a2=0.120, a3=0.085, d5=0.120):
        self.d1 = d1
        self.a2 = a2
        self.a3 = a3
        self.d5 = d5

    def solve(self, x: float, y: float, z: float, pitch: float, elbow_up: bool = True) -> Optional[Tuple[float, float, float, float]]:
        # Step 1: Base yaw
        q1 = math.atan2(y, x)

        # Step 2: Wrist center
        r = math.sqrt(x**2 + y**2)
        rw = r - self.d5 * math.cos(pitch)
        zw = (z - self.d1) - self.d5 * math.sin(pitch)

        # Step 3: Elbow angle via Law of Cosines
        d_sq = rw**2 + zw**2
        cos_q3 = (d_sq - self.a2**2 - self.a3**2) / (2.0 * self.a2 * self.a3)

        if abs(cos_q3) > 1.0:
            return None # Target unreachable

        sin_q3 = math.sqrt(max(0.0, 1.0 - cos_q3**2))
        q3 = -math.atan2(sin_q3, cos_q3) if elbow_up else math.atan2(sin_q3, cos_q3)

        # Step 4: Shoulder angle
        alpha = math.atan2(zw, rw)
        beta = math.atan2(self.a3 * math.sin(q3), self.a2 + self.a3 * math.cos(q3))
        q2 = alpha - beta

        # Step 5: Wrist pitch
        q4 = pitch - (q2 + q3)

        return q1, q2, q3, q4
```

---

### 4. Hands-On Lab & Practical Code References

#### 1. Executing Cartesian Goal Reaching:
```bash
# Test Cartesian IK goal seeking in simulation
ros2 run arm_demos demo_03_inverse_kinematics
```

#### 2. Source Code Reference:
- [`ros2_arm_kit/src/arm_kinematics/arm_kinematics/inverse_kinematics.py`](../../Ros2%20learning%20kits/ros2_arm_kit/src/arm_kinematics/arm_kinematics/inverse_kinematics.py)


