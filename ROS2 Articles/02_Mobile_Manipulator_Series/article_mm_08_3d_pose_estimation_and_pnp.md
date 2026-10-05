## MM 08: 3D POSE ESTIMATION: PERSPECTIVE-N-POINT (PNP) & POINT CLOUDS

*Purpose: Convert 2D pixel detections into full 6-DOF 3D grasping poses. Master the Perspective-n-Point (PnP) problem, solve $[R | \mathbf{t}]$ from 2D-3D point correspondences, process RGB-D point clouds, and extract object centroids using RANSAC plane segmentation.*

### Must Answer
- What is the Perspective-n-Point (PnP) problem, and how many 2D-3D point correspondences are required to solve 6-DOF pose?
- How does the EPnP (Efficient PnP) algorithm solve rotation $R \in SO(3)$ and translation $\mathbf{t} \in \mathbb{R}^3$ in $O(n)$ time?
- How do RGB-D cameras (RealSense, Astra) generate organized 3D Point Clouds ($X, Y, Z, R, G, B$)?
- How does RANSAC Plane Segmentation separate table surfaces from target objects?
- How does Principal Component Analysis (PCA) determine the optimal gripper approach angle from an object point cloud?

### Key Insight
To grasp an object, the robot needs both position $(X, Y, Z)$ and orientation $(R)$; PnP extracts the full 6-DOF transformation matrix by matching 2D pixel corners against a known 3D CAD model.

---

### 1. The Perspective-n-Point (PnP) Problem

Given:
1. A set of $n$ 3D object points in the object reference frame: $\mathbf{P}_i^{\text{obj}} = [X_i, Y_i, Z_i]^T$.
2. Their corresponding 2D projected pixel locations on the image sensor: $\mathbf{p}_i = [u_i, v_i]^T$.
3. The camera intrinsic matrix $K$.

Find the 6-DOF rigid transformation $[R | \mathbf{t}] \in SE(3)$ such that:
$$s_i \begin{bmatrix} u_i \\ v_i \\ 1 \end{bmatrix} = K \left( R \mathbf{P}_i^{\text{obj}} + \mathbf{t} \right)$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PNP POSE SOLVER PIPELINE                           │
│                                                                             │
│   Known 3D CAD Corners ──▶ [PnP Solver (cv2.solvePnP)] ──▶ Object Pose      │
│   (e.g., 5cm Cube)                  ▲                      [R | t] in Camera │
│                                     │                             │         │
│   Detected 2D Image Pixels ─────────┘                             ▼         │
│   (u_1, v_1) ... (u_4, v_4)                         Publish /detected_object│
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Minimum Required Points:
- **P3P**: Exactly 3 points yield up to 4 ambiguous solutions.
- **P4P / EPnP ($n \ge 4$)**: Resolves ambiguity uniquely using linear least squares + non-linear Levenberg-Marquardt refinement.

---

### 2. RGB-D Point Cloud Processing Pipeline

When using structured-light or Time-of-Flight (ToF) depth cameras:
1. **PassThrough Filter**: Crop point cloud to region of interest ($0.2\text{ m} \le Z \le 1.2\text{ m}$).
2. **VoxelGrid Downsampling**: Reduce $300,000$ points to a uniform $5\text{ mm}$ grid.
3. **RANSAC Plane Fitting**: Model the tabletop plane equation $a x + b y + c z + d = 0$; extract inliers (table) and discard them.
4. **Euclidean Cluster Extraction**: Group remaining outlier points into distinct object clusters.
5. **PCA Axis Alignment**: Compute the covariance matrix of cluster points to extract principal eigenvectors (major and minor object axes) for gripper alignment.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Running 3D Pose Estimation Node:
```bash
# Launch perception pipeline
ros2 launch mobile_manipulator_perception perception.launch.py
```
Inspect the `/detected_object_pose` topic in RViz.
