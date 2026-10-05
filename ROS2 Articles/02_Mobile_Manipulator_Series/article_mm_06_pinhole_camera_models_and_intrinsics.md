## MM 06: PINHOLE CAMERA MODELS, INTRINSICS & DISTORTION CALIBRATION

*Purpose: Master computer vision geometry for robotics. Formulate the projective Pinhole Camera Model, derive the Camera Intrinsic Matrix $K$, understand radial and tangential lens distortion ($k_1, k_2, p_1, p_2$), and project 2D pixel coordinates into 3D unit optical rays.*

### Must Answer
- How does a 3D physical point $(X, Y, Z)$ project onto a 2D digital image sensor $(u, v)$?
- What is the Camera Intrinsic Matrix $K$, and what do focal lengths $(f_x, f_y)$ and principal point $(c_x, c_y)$ represent physically?
- What causes Barrel and Pincushion lens distortion, and how do radial/tangential distortion models correct warped images?
- How do we calculate a 3D spatial unit ray vector from a 2D pixel coordinate?
- How is camera calibration metadata published and consumed in ROS2 using `sensor_msgs/msg/CameraInfo`?

### Key Insight
A 2D pixel coordinate $(u, v)$ is not a 3D position—it is a 1-dimensional ray passing from the camera focal center through 3D space; depth information ($Z$) is required to resolve the full 3D spatial position.

---

### 1. The Pinhole Camera Geometry

Let a 3D point in the camera optical frame be $\mathbf{P} = [X, Y, Z]^T$ with $Z > 0$.
The pinhole projection maps $\mathbf{P}$ to normalized image plane coordinates $(x_n, y_n)$:

$$x_n = \frac{X}{Z}, \quad y_n = \frac{Y}{Z}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PINHOLE CAMERA PROJECTION                          │
│                                                                             │
│                                           Point P = [X, Y, Z]^T             │
│                                                   o                         │
│                                                  /                          │
│                         Image Sensor Plane      /                           │
│                              ┌──────────────┐  /                            │
│                              │   Pixel (u,v)│ /                             │
│                              │       o      │/                              │
│                              │              /                               │
│       Focal Center (0,0,0) ──┴─────────────/────────────────────────► Z     │
│                              ◄────── f ────► (Focal Length)                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Camera Intrinsic Matrix $K$

Converting normalized coordinates $(x_n, y_n)$ into discrete pixel coordinates $(u, v)$ (measured in pixels from top-left origin):

$$\begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} X / Z \\ Y / Z \\ 1 \end{bmatrix} = \frac{1}{Z} K \mathbf{P}$$

- $f_x, f_y$: Focal lengths in pixel units ($f_x = \frac{f_{\text{mm}}}{\text{pixel\_size}_x}$).
- $c_x, c_y$: Principal point (intersection of the optical axis with the sensor, typically near image center: $W/2, H/2$).

---

### 3. Lens Distortion & Unwarping Models

Real optical lenses bend light rays, introducing non-linear geometric distortion:
1. **Radial Distortion** (Barrel / Pincushion):
   $$x_{\text{distorted}} = x_n (1 + k_1 r^2 + k_2 r^4 + k_3 r^6)$$
   $$y_{\text{distorted}} = y_n (1 + k_1 r^2 + k_2 r^4 + k_3 r^6)$$
   where $r^2 = x_n^2 + y_n^2$.
2. **Tangential Distortion** (Lens not perfectly parallel to sensor):
   $$x_{\text{distorted}} += [2 p_1 x_n y_n + p_2 (r^2 + 2 x_n^2)]$$
   $$y_{\text{distorted}} += [p_1 (r^2 + 2 y_n^2) + 2 p_2 x_n y_n]$$

In ROS2, `image_proc` or `cv2.undistort` takes raw camera images and the $D = [k_1, k_2, p_1, p_2, k_3]$ vector to produce rectified, geometrically linear images.

---

### 4. 2D Pixel to 3D Ray Back-Projection

Given a detected pixel $(u, v)$ and a known depth measurement $Z$ (from an RGB-D sensor or known table height):

$$X = \frac{(u - c_x) \cdot Z}{f_x}$$
$$Y = \frac{(v - c_y) \cdot Z}{f_y}$$
$$Z = Z$$

---

### 5. Hands-On Lab & Practical Code References

#### 1. Inspecting `CameraInfo` Metadata in ROS2:
```bash
# Launch camera simulation
ros2 launch mobile_manipulator_bringup full_mobile_manipulation.launch.py

# Echo camera intrinsic parameters
ros2 topic echo /camera/camera_info --once
```

#### 2. Source Code Reference:
- Pose Estimator: [`ros2_mobile_manipulator_kit/src/mobile_manipulator_perception/mobile_manipulator_perception/pose_estimator.py`](file:///e:/Intelligent%20Systems%20Knowledge%20Ecosystem/02%20—%20Domains/ROS2/Ros2%20learning%20kits/ros2_mobile_manipulator_kit/src/mobile_manipulator_perception/mobile_manipulator_perception/pose_estimator.py)
