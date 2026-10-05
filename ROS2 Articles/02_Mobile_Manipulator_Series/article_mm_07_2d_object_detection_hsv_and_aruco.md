## MM 07: 2D OBJECT DETECTION: HSV COLOR FILTERING, CONTOURS & ARUCO MARKERS

*Purpose: Master 2D perception pipelines for robotic grasping. Learn HSV color space thresholding, morphological noise filtering, contour boundary extraction, bounding box estimation, and sub-pixel ArUco/AprilTag fiducial marker tracking.*

### Must Answer
- Why does RGB color space fail under real-world lighting changes, and why is HSV (Hue, Saturation, Value) robust to shadows?
- What are Morphological Operations (Erosion, Dilation, Opening, Closing), and how do they eliminate sensory noise?
- How do Image Moments calculate the exact centroid $(c_x, c_y)$ and principal orientation angle of a segmented object?
- What are Fiducial Markers (ArUco / AprilTags / QR codes), and why do they provide high-precision 6-DOF ground truth?
- How does `cv_bridge` convert between ROS2 `sensor_msgs/msg/Image` and OpenCV `cv::Mat` without memory copy overhead?

### Key Insight
Robust visual detection starts with invariant feature representations; isolating Hue from illumination intensity prevents ambient shadows from corrupting object masks.

---

### 1. The HSV Color Space Advantage

In RGB space, an orange block under sunlight has completely different values ($[255, 140, 0]$) than under indoor shade ($[130, 70, 0]$); thresholding in RGB creates massive segmentation gaps.

**HSV separates chromaticity from intensity**:
- **Hue ($H \in [0^\circ, 360^\circ]$ or $[0, 179]$ in OpenCV)**: The pure color wavelength (Orange is always $H \approx 10 - 25$).
- **Saturation ($S \in [0, 255]$)**: Color purity (vibrant vs. washed out).
- **Value ($V \in [0, 255]$)**: Brightness/illumination.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HSV COLOR CYLINDER SPACE                           │
│                                                                             │
│               Value (Brightness)                                            │
│                    ▲                                                        │
│                    │   /‾‾‾‾\  Hue (Color Angle 0-360)                      │
│                    │  |  *   | ◄── Saturation (Radius from Center)          │
│                    │   \____/                                               │
│                    └────────────────►                                       │
│                                                                             │
│   • Shadows only reduce Value (V); Hue (H) remains invariant!               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Morphological Filtering & Contour Moments

1. **Thresholding**: Produces a raw binary mask: $M(x, y) \in \{0, 1\}$.
2. **Morphological Opening ($\text{Erode} \to \text{Dilate}$)**: Removes small isolated speckle noise (salt-and-pepper noise).
3. **Morphological Closing ($\text{Dilate} \to \text{Erode}$)**: Fills small internal holes within the detected object.
4. **Contour Extraction & Spatial Centroid**:
   Using spatial moments $M_{pq} = \sum_{x} \sum_{y} x^p y^q M(x, y)$:
   $$c_x = \frac{M_{10}}{M_{00}}, \quad c_y = \frac{M_{01}}{M_{00}}$$

---

### 3. Fiducial Markers: Sub-Pixel ArUco / AprilTag Detection

When manipulating untextured objects or routing in factories, **ArUco / AprilTag markers** encode binary IDs with built-in Hamming error correction:
- Detect black/white quad boundaries.
- Extract 4 sub-pixel corner coordinates $[p_1, p_2, p_3, p_4]$.
- Decode binary bit payload.
- Solve exact 6-DOF pose via PnP in $< 1.0\text{ ms}$.

---

### 4. Hands-On Lab & Practical Code References

#### 1. Running 2D Object Detection Demo:
```bash
# Run Demo 04: OpenCV object detector and contour tracker
ros2 run mobile_manipulator_demos demo_04_object_detection.py
```

#### 2. Source Code Reference:
- Object Detector Node: [`ros2_mobile_manipulator_kit/src/mobile_manipulator_perception/mobile_manipulator_perception/object_detector.py`](file:///e:/Intelligent%20Systems%20Knowledge%20Ecosystem/02%20—%20Domains/ROS2/Ros2%20learning%20kits/ros2_mobile_manipulator_kit/src/mobile_manipulator_perception/mobile_manipulator_perception/object_detector.py)
- Breaker Test: `ros2 run mobile_manipulator_demos break_vision.py`
