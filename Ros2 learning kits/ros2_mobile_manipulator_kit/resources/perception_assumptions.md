# Perception Assumptions

**Critical:** Detection does NOT give you a pose.
Detection gives you pixels. You must compute the pose.

This document makes the 2D→3D conversion explicit.

---

## What Detection Actually Produces

```
Camera Image (2D)
       │
       ▼
┌─────────────────────────────┐
│  Color/Shape Detection      │
│  (OpenCV)                   │
│                             │
│  Output:                    │
│  - center_x (pixels)        │
│  - center_y (pixels)        │
│  - width (pixels)           │
│  - height (pixels)          │
│  - contour                  │
└─────────────────────────────┘
       │
       │  This is NOT a 3D pose
       ▼
┌─────────────────────────────┐
│  Pose Estimation            │
│  (Geometry + Assumptions)   │
│                             │
│  Requires:                  │
│  - Camera intrinsics        │
│  - Known object size   ◄────── ASSUMPTION
│  - Frame transform          │
│                             │
│  Output:                    │
│  - x, y, z (meters)         │
│  - frame_id                 │
└─────────────────────────────┘
```

---

## The Key Assumption: Known Object Size

Without depth sensing, we estimate depth using **similar triangles**:

```
Real Object Width (W_real)      Pixel Width (W_pixels)
         │                              │
         │                              │
         └──────────────┬───────────────┘
                        │
                        ▼
              Estimated Depth (Z)

Formula:
  Z = (W_real × focal_length) / W_pixels
```

**This only works if:**
- Object width is known and consistent
- Object is roughly parallel to image plane
- No significant lens distortion at edges

---

## Assumptions Made by This Kit

### 1. Known Object Width
```python
# perception_params.yaml
object_width: 0.05  # 5cm cube
```

**If wrong:** Depth estimate will be wrong proportionally.

### 2. Flat Surface (Table)

Objects are assumed to be resting on a known surface.

**If violated:**
- Objects in hand → wrong height
- Stacked objects → wrong pose

### 3. Fixed Camera Extrinsics

Camera position/orientation relative to robot is fixed and calibrated.

**If wrong (common!):**
- Systematic offset in all detections
- Use `break_camera_tf.py` to experience this

### 4. Camera Intrinsics Known

Focal length and principal point from calibration.

**If using defaults:**
```python
# Assumed 60° FOV webcam
fx = width / (2 * tan(60° / 2))
fy = fx  # Square pixels
cx = width / 2
cy = height / 2
```

**For accuracy:** Calibrate your actual camera.

### 5. Top-Down Grasp Orientation

We assume objects can be grasped from directly above.

**If violated:**
- Tall objects may need side grasp
- Irregular shapes may need orientation detection

---

## What Happens Without Each Assumption

| Assumption Violated | Effect | Detection |
|---------------------|--------|-----------|
| Wrong object size | Z scaled wrong | Grasp too high/low |
| Not on table | Z completely wrong | Arm hits table or air |
| Camera moved | Systematic offset | Consistent miss |
| Wrong intrinsics | Radial distortion | Edge detections wrong |
| Object tilted | Orientation wrong | Grasp slips |

---

## Frame Output: camera_link_optical

Detection outputs are in `camera_link_optical`:

```
camera_link_optical frame:
    Y (down in image)
    │
    │
    └───X (right in image)
       ╱
      Z (depth, into scene)
```

**This is OpenCV convention, not ROS convention.**

Must transform to `arm_base_link` before sending to MoveIt.

---

## Improving Accuracy

### Option 1: Better Camera Calibration
```bash
ros2 run camera_calibration cameracalibrator --size 8x6 --square 0.025
```

### Option 2: Depth Camera
Replace pinhole estimation with actual depth readings.
Removes "known object size" assumption.

### Option 3: Marker-Based Pose
Use ArUco/AprilTags for 6-DOF pose.
Works for any object with marker.

### Option 4: Multiple Viewpoints
Triangulate from two cameras.
Removes single-view ambiguity.

---

## Debugging Pose Estimation

### Symptom: Arm reaches too high
- Object size overestimated, or
- Table height assumption wrong

### Symptom: Arm reaches to the side
- Camera extrinsics wrong, or
- Wrong frame used (camera_link vs camera_link_optical)

### Symptom: Inconsistent poses
- Detection jitter (try averaging), or
- Object moving during detection

### Verification Command
```bash
# Watch detected poses
ros2 topic echo /perception/object_pose

# Visualize in RViz
# Add PoseStamped display → Topic: /perception/object_pose
```

---

## Honest Limitations

This perception system:

| Can Do | Cannot Do |
|--------|-----------|
| Detect colored objects | Recognize object types |
| Estimate position | Estimate orientation |
| Work in controlled lighting | Handle shadows/reflections |
| Process single objects | Handle occlusion |
| 10+ Hz detection | Real-time tracking |

**This is a teaching system, not a production vision pipeline.**

The goal is understanding the geometry, not solving perception.
