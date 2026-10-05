## ARM 03: FORWARD KINEMATICS: GEOMETRIC PROPAGATION FROM BASE TO TCP

*Purpose: Derive the complete forward kinematics equations for the 5-DOF articulated robot arm. Trace geometric projection, link propagation, tool center point (TCP) position and pitch angle from joint angles, and verify against real-time ROS2 TF broadcasts.*

### Must Answer
- What is Forward Kinematics (FK), and why is it a strictly deterministic, single-solution problem?
- How do we calculate the Cartesian coordinates $(x, y, z)$ and end-effector pitch angle $\theta_{\text{pitch}}$ from joint angles $(q_1, q_2, q_3, q_4, q_5)$?
- How does the planar decomposition method simplify 3D spatial calculations?
- How is Forward Kinematics implemented in pure Python within `arm_kinematics`?
- How does `robot_state_publisher` compute and broadcast these transformations at 50 Hz?

### Key Insight
Forward Kinematics maps the joint space $\mathcal{Q} \subset \mathbb{R}^n$ to the operational task space $\mathcal{X} \subset SE(3)$. Given valid joint angles, the end-effector pose is uniquely and instantaneously determined.

---

### 1. The Forward Kinematic Mapping

Let $\mathbf{q} = [q_1, q_2, q_3, q_4]^T \in \mathbb{R}^4$ be the vector of active arm joint angles.
The Forward Kinematics function $f(\mathbf{q})$ maps joint angles to the Cartesian Tool Center Point (TCP) pose $\mathbf{x} = [x, y, z, \theta_{\text{pitch}}]^T$:

$$\mathbf{x} = f(\mathbf{q})$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FORWARD KINEMATICS DECOMPOSITION                      │
│                                                                             │
│             Z                                                               │
│             ▲              (Joint 3 / Elbow)                                │
│             │                  o                                            │
│             │                 / \                                           │
│             │        Link 2  /   \  Link 3                                  │
│             │         (a_2) /     \  (a_3)                                  │
│             │              /       \                                        │
│             │ (Shoulder)  o         o (Wrist / Joint 4)                     │
│             │             │          \  Link 4 (d_5)                        │
│             │      Link 1 │           \                                     │
│             │       (d_1) │            ▼ TCP (Grasp Link)                   │
│             │             │                                                 │
│             └─────────────┴─────────────────────────► r (Radial Plane)      │
│                        (Base Yaw / Joint 1)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Planar Trigonometric Derivation

Because joints 2, 3, and 4 all rotate around parallel horizontal pitch axes, the arm moves entirely within a single vertical planar slice that is rotated by the base yaw angle $q_1$.

#### Step 1: Effective Arm Extension ($r$) in the Vertical Plane
The radial distance from the base rotation axis to the TCP is the sum of horizontal projections:
$$r(q_2, q_3, q_4) = a_2 \cos(q_2) + a_3 \cos(q_2 + q_3) + d_5 \cos(q_2 + q_3 + q_4)$$

#### Step 2: Vertical Height ($z$) above the Table
The height of the TCP above the mounting surface is the sum of vertical projections plus base height:
$$z(q_2, q_3, q_4) = d_1 + a_2 \sin(q_2) + a_3 \sin(q_2 + q_3) + d_5 \sin(q_2 + q_3 + q_4)$$

#### Step 3: End-Effector Pitch Angle ($\theta_{\text{pitch}}$)
The overall pitch of the gripper relative to the horizontal table plane:
$$\theta_{\text{pitch}} = q_2 + q_3 + q_4$$

#### Step 4: 3D Cartesian Coordinates
Projecting the radial plane distance $r$ into the 3D world frame using the base yaw angle $q_1$:
$$x = r \cos(q_1)$$
$$y = r \sin(q_1)$$

---

### 3. Numerical Example & Hand Calculation

Given the physical arm parameters:
$$d_1 = 0.096\text{ m}, \quad a_2 = 0.120\text{ m}, \quad a_3 = 0.085\text{ m}, \quad d_5 = 0.120\text{ m}$$

Let joint angles be:
$$q_1 = 0.0\text{ rad}, \quad q_2 = 0.0\text{ rad}, \quad q_3 = 0.0\text{ rad}, \quad q_4 = 0.0\text{ rad}$$
(Arm fully outstretched horizontally along the X-axis).

#### Calculations:
1. $r = 0.120 \cos(0) + 0.085 \cos(0) + 0.120 \cos(0) = 0.120 + 0.085 + 0.120 = 0.325\text{ m}$ (Maximum radial reach).
2. $z = 0.096 + 0.120 \sin(0) + 0.085 \sin(0) + 0.120 \sin(0) = 0.096\text{ m}$.
3. $\theta_{\text{pitch}} = 0 + 0 + 0 = 0\text{ rad}$.
4. $x = 0.325 \cos(0) = 0.325\text{ m}$, $y = 0.325 \sin(0) = 0.0\text{ m}$.

The calculated TCP pose is $(x=0.325, y=0.0, z=0.096, \theta_{\text{pitch}}=0)$.

---

### 4. Pure Python Implementation in `arm_kinematics`

Below is the production implementation from `ros2_arm_kit/src/arm_kinematics/arm_kinematics/forward_kinematics.py`:

```python
import math
from typing import Tuple

class ForwardKinematics:
    def __init__(self, d1=0.096, a2=0.120, a3=0.085, d5=0.120):
        self.d1 = d1
        self.a2 = a2
        self.a3 = a3
        self.d5 = d5

    def compute(self, q1: float, q2: float, q3: float, q4: float) -> Tuple[float, float, float, float]:
        """
        Computes Cartesian TCP Pose from joint angles.
        Returns: (x, y, z, pitch_angle)
        """
        theta23 = q2 + q3
        theta234 = q2 + q3 + q4

        # Planar radial distance and height
        r = self.a2 * math.cos(q2) + self.a3 * math.cos(theta23) + self.d5 * math.cos(theta234)
        z = self.d1 + self.a2 * math.sin(q2) + self.a3 * math.sin(theta23) + self.d5 * math.sin(theta234)

        # 3D spatial projection
        x = r * math.cos(q1)
        y = r * math.sin(q1)
        pitch = theta234

        return x, y, z, pitch
```

---

### 5. Hands-On Lab & Practical Code References

#### 1. Running the Forward Kinematics Demo Node:
```bash
# Run demo 02 to command joints and print computed vs TF TCP poses
ros2 run arm_demos demo_02_forward_kinematics
```

#### 2. Inspecting the ROS2 Kinematics Service:
- Service Node: [`ros2_arm_kit/src/arm_kinematics/arm_kinematics/kinematics_service_node.py`](../../Ros2%20learning%20kits/ros2_arm_kit/src/arm_kinematics/arm_kinematics/kinematics_service_node.py)
- Call FK Service via CLI:
```bash
ros2 service call /compute_fk custom_interfaces/srv/ComputeFK "{joint_angles: [0.0, 0.5, -0.3, 0.2]}"
```


