## ARM 02: KINEMATIC MODELING: DENAVIT-HARTENBERG (DH) PARAMETERS VS. URDF TREE

*Purpose: Master the two primary ways robots are described mathematically and computationally. Contrast classical analytical Denavit-Hartenberg (DH) parameters with modern computational URDF/Xacro kinematic trees, understand joint constraints, link offsets, and kinematic loop closures.*

### Must Answer
- What is the Denavit-Hartenberg (DH) convention, and how does it reduce a complex 6-DOF 3D transformation into exactly 4 geometric parameters?
- What are the four DH parameters ($a_i, \alpha_i, d_i, \theta_i$), and what is the strict coordinate axis assignment algorithm?
- How does URDF (Unified Robot Description Format) differ from DH modeling, and why does ROS2 use tree-structured graphs instead of linear DH chains?
- What are the physical joint types (revolute, continuous, prismatic, fixed, planar, floating), and how do joint limits prevent motor destruction?
- How do we translate between a CAD model, a DH table, and a production ROS2 Xacro file?

### Key Insight
DH parameters are an optimized minimal mathematical abstraction for closed-form kinematics calculations; URDF is an extensible computational scene graph that binds collision geometry, visual meshes, inertial tensors, and sensor frames into a single tree.

---

### 1. The Denavit-Hartenberg (DH) Convention: Minimalist Kinematic Modeling

In 1955, Jacques Denavit and Richard Hartenberg proved that any spatial relationship between two rigid bodies connected by a single revolute or prismatic joint can be completely defined by **4 parameters** instead of 6 (3 rotations + 3 translations).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DENAVIT-HARTENBERG GEOMETRY                        │
│                                                                             │
│               Z_{i-1} (Joint i Axis)             Z_i (Joint i+1 Axis)       │
│                  ▲                                  ▲                       │
│                  │                                  │                       │
│                  │ ◄─────────── a_i ───────────────►│ (Common Normal)       │
│                  │                                  │                       │
│       Origin_{i-1} ─────── d_i ───────► (Intersection) ──── X_i             │
│                                                     │                       │
│                 (Angle \theta_i around Z_{i-1})     (Angle \alpha_i around X_i)
└─────────────────────────────────────────────────────────────────────────────┘
```

#### The Four DH Parameters:
1. **$a_i$ (Link Length)**: Distance along $X_i$ from $Z_{i-1}$ to $Z_i$ (length of the common normal).
2. **$\alpha_i$ (Link Twist)**: Angle around $X_i$ from $Z_{i-1}$ to $Z_i$ (tilt between joint axes).
3. **$d_i$ (Link Offset)**: Distance along $Z_{i-1}$ from $X_{i-1}$ to $X_i$ (variable in prismatic joints).
4. **$\theta_i$ (Joint Angle)**: Angle around $Z_{i-1}$ from $X_{i-1}$ to $X_i$ (variable in revolute joints).

---

### 2. The Standard DH Homogeneous Transformation Matrix

The transformation from frame $i-1$ to frame $i$ is the product of four basic spatial operations:

$${}^{i-1} A_i = \text{Rot}_z(\theta_i) \cdot \text{Trans}_z(d_i) \cdot \text{Trans}_x(a_i) \cdot \text{Rot}_x(\alpha_i)$$

Multiplying these matrices yields the canonical **DH Transformation Matrix**:

$${}^{i-1} A_i = \begin{bmatrix}
\cos\theta_i & -\sin\theta_i \cos\alpha_i &  \sin\theta_i \sin\alpha_i & a_i \cos\theta_i \\
\sin\theta_i &  \cos\theta_i \cos\alpha_i & -\cos\theta_i \sin\alpha_i & a_i \sin\theta_i \\
0            &  \sin\alpha_i              &  \cos\alpha_i              & d_i \\
0            &  0                         &  0                         & 1
\end{bmatrix}$$

---

### 3. DH Modeling for the 5-DOF Articulated Robotic Arm

For our 5-DOF tabletop arm (`ros2_arm_kit`), the physical link lengths are:
- $d_1 = 0.096\text{ m}$ (Base mount to shoulder axis)
- $a_2 = 0.120\text{ m}$ (Upper arm length)
- $a_3 = 0.085\text{ m}$ (Forearm length)
- $d_5 = 0.120\text{ m}$ (Wrist to Tool Center Point)

#### The Canonical DH Table:

| Link $i$ | Joint Type | $\theta_i$ (Variable) | $d_i$ (m) | $a_i$ (m) | $\alpha_i$ (rad) | Home Offset |
|---|---|---|---|---|---|---|
| **1** (Base Yaw) | Revolute | $q_1$ | $d_1 = 0.096$ | 0 | $+\pi/2$ | $0$ |
| **2** (Shoulder Pitch) | Revolute | $q_2$ | 0 | $a_2 = 0.120$ | 0 | $0$ |
| **3** (Elbow Pitch) | Revolute | $q_3$ | 0 | $a_3 = 0.085$ | 0 | $0$ |
| **4** (Wrist Pitch) | Revolute | $q_4$ | 0 | 0 | $-\pi/2$ | $0$ |
| **5** (Wrist Roll / TCP) | Revolute | $q_5$ | $d_5 = 0.120$ | 0 | 0 | $0$ |

---

### 4. URDF & Xacro: Modern Computational Kinematic Trees

While DH parameters are powerful for mathematical solvers, they have serious real-world limitations:
1. **Tree Topologies**: DH parameters only model linear chains ($1 \rightarrow 2 \rightarrow 3$). They cannot represent branched kinematic trees (e.g. dual-arm robots, parallel-jaw grippers with mimic joints).
2. **Arbitrary Reference Frames**: DH forces coordinate frames to lie on joint axes and common normals, which rarely aligns with CAD origin center-of-mass or sensor mounting planes.

#### URDF Joint Types:
- `revolute`: Rotational motion with explicit upper/lower angular limits ($\text{rad}$).
- `continuous`: Continuous $360^\circ$ rotation without limits (e.g. wheels, continuous wrist roll).
- `prismatic`: Linear sliding motion along an axis with distance limits ($\text{m}$).
- `fixed`: Rigid non-moving connection (e.g., sensor brackets, camera mounts).
- `floating`: 6-DOF unconstrained connection (used for legged/aerial floating bases).

#### URDF Xacro Snippet from `ros2_arm_kit`:
```xml
<!-- Upper Arm Link 2 connected to Shoulder Link 1 -->
<joint name="joint_2" type="revolute">
  <parent link="link_1"/>
  <child link="link_2"/>
  <origin xyz="0 0 0.096" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>
  <limit lower="-1.57" upper="1.57" effort="5.0" velocity="2.0"/>
</joint>

<link name="link_2">
  <visual>
    <geometry><mesh filename="package://arm_description/meshes/link2.stl"/></geometry>
  </visual>
  <collision>
    <geometry><mesh filename="package://arm_description/meshes/link2.stl"/></geometry>
  </collision>
  <inertial>
    <mass value="0.250"/>
    <inertia ixx="0.001" ixy="0" ixz="0" iyy="0.001" iyz="0" izz="0.0005"/>
  </inertial>
</link>
```

---

### 5. Hands-On Lab & Practical Code References

#### 1. Inspecting the Kinematic Tree in RViz:
```bash
# Launch robot_state_publisher with Joint State GUI
ros2 launch arm_description display.launch.py
```
Move the sliders in `joint_state_publisher_gui` and observe how each frame updates relative to the base pedestal.

#### 2. Auditing the URDF Source:
- URDF Path: [`ros2_arm_kit/src/arm_description/urdf/arm.urdf.xacro`](../../Ros2%20learning%20kits/ros2_arm_kit/src/arm_description/urdf/arm.urdf.xacro)
- RViz Config: [`ros2_arm_kit/src/arm_description/launch/display.launch.py`](../../Ros2%20learning%20kits/ros2_arm_kit/src/arm_description/launch/display.launch.py)

#### 3. Failure Mode: Unchecked Joint Limit Saturation
- Node: `ros2 run arm_demos break_joint_limits`
- Injected Fault: Commands joint angles beyond physical mechanical limits ($q_2 > +90^\circ$).
- Architectural Fix: Enforce parameter clamping inside the ros2_control hardware interface layer.



