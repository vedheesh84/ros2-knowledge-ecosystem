# Arm Kinematics Derivation

**Analytical Kinematic Modeling for 5-DOF Articulated Arm**

---

## 1. Physical Parameters & Link Lengths

The arm consists of a rotating base ($q_1$), shoulder pitch ($q_2$), elbow pitch ($q_3$), wrist pitch ($q_4$), and wrist roll / gripper base ($q_5$):

| Parameter | Symbol | Value (m) | Description |
|---|---|---|---|
| Base Height | $d_1$ | 0.096 | Height from table mount to shoulder axis |
| Upper Arm | $a_2$ | 0.120 | Shoulder to elbow link length |
| Forearm | $a_3$ | 0.085 | Elbow to wrist pitch link length |
| End-Effector | $d_5$ | 0.120 | Wrist pitch axis to tool center point (TCP) |

---

## 2. Forward Kinematics (FK)

Given joint angles $\mathbf{q} = [q_1, q_2, q_3, q_4]^T$:

### Radial Distance in Arm Plane ($r$):
$$r = a_2 \cos(q_2) + a_3 \cos(q_2 + q_3) + d_5 \cos(q_2 + q_3 + q_4)$$

### Height above Table ($z$):
$$z = d_1 + a_2 \sin(q_2) + a_3 \sin(q_2 + q_3) + d_5 \sin(q_2 + q_3 + q_4)$$

### 3D Cartesian Coordinates:
$$x = r \cos(q_1)$$
$$y = r \sin(q_1)$$
$$\theta_{\text{pitch}} = q_2 + q_3 + q_4$$

---

## 3. Inverse Kinematics (IK)

Given target end-effector coordinates $(x, y, z)$ and pitch $\theta_{\text{pitch}}$:

### Step 1: Base Joint ($q_1$)
$$q_1 = \text{atan2}(y, x)$$

### Step 2: Wrist Center Position $(r_w, z_w)$
Subtract the tool length vector:
$$r_w = \sqrt{x^2 + y^2} - d_5 \cos(\theta_{\text{pitch}})$$
$$z_w = z - d_1 - d_5 \sin(\theta_{\text{pitch}})$$

### Step 3: Elbow Joint ($q_3$)
Using the Law of Cosines on triangle $(0, 0) \rightarrow (a_2) \rightarrow (r_w, z_w)$:
$$\cos(q_3) = \frac{r_w^2 + z_w^2 - a_2^2 - a_3^2}{2 a_2 a_3}$$

- **Elbow-Up Solution:** $q_3 = -\arccos(\cos(q_3))$
- **Elbow-Down Solution:** $q_3 = +\arccos(\cos(q_3))$

### Step 4: Shoulder Joint ($q_2$)
$$\alpha = \text{atan2}(z_w, r_w)$$
$$\beta = \text{atan2}(a_3 \sin(q_3), a_2 + a_3 \cos(q_3))$$
$$q_2 = \alpha - \beta$$

### Step 5: Wrist Pitch ($q_4$)
$$q_4 = \theta_{\text{pitch}} - (q_2 + q_3)$$

---

## 4. Differential Kinematics & Singularities

The planar Jacobian $J(\mathbf{q})$ relates joint angular velocities to end-effector velocity:

$$\begin{bmatrix} \dot{r} \\ \dot{z} \end{bmatrix} = J \begin{bmatrix} \dot{q}_2 \\ \dot{q}_3 \\ \dot{q}_4 \end{bmatrix}$$

### Boundary Singularity (Full Extension):
Occurs when $q_3 = 0$. The arm is fully stretched to its maximum radius ($a_2 + a_3 + d_5$), losing 1 degree of freedom (cannot move radially outward).
