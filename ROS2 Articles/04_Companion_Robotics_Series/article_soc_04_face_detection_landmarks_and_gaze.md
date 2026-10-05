## SOC 04: FACE DETECTION, 68 LANDMARKS & GAZE ESTIMATION

*Purpose: Give the companion visual social awareness. Master real-time face detection, 68-point facial landmark regression (MediaPipe / Dlib), 3D head pose estimation ($[R | \mathbf{t}]$ via PnP), and mutual eye contact detection.*

### Must Answer
- How does the robot detect human faces in live camera feeds in $< 15\text{ ms}$?
- What are 68-point Facial Landmarks, and how do they capture eyelid opening, eyebrow raise, and lip curvature?
- How is 3D Head Pose ($Yaw, Pitch, Roll$) estimated from 2D facial landmarks using the Perspective-n-Point (PnP) solver?
- What is Mutual Eye Contact, and how does the robot know if a person is looking directly at it?
- How does the Face Tracking Node publish structured ROS2 messages (`companion_head_msgs/msg/FaceDetectionArray`)?

### Key Insight
A human face is rich in non-verbal social signals; tracking 3D head orientation and eyebrow raises allows the robot to distinguish between someone casually passing by and someone actively engaging it in conversation.

---

### 1. 68-Point Facial Landmark Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         68-POINT FACIAL LANDMARKS                           │
│                                                                             │
│           [Eyebrows: 17-26]              [Eyebrows: 22-26]                  │
│             o---o---o---o                  o---o---o---o                    │
│                 [Eye: 36-41]                    [Eye: 42-47]                │
│                 o===o                           o===o                       │
│                  \o/                             \o/                        │
│                                [Nose: 27-35]                                │
│                                      o                                      │
│                                     / \                                     │
│                                    o-o-o                                    │
│                              [Outer Lip: 48-59]                             │
│                                 .---------.                                 │
│                                (   MOUTH   )                                │
│                                 '---------'                                 │
│                              [Chin Contour: 0-16]                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Estimating 3D Head Pose via PnP

By pairing 6 key 2D facial landmarks (Nose tip #30, Chin #8, Left eye corner #36, Right eye corner #45, Left mouth corner #48, Right mouth corner #54) with a standardized 3D anthropometric face model:
$$s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = K \left( R_{\text{head}} \mathbf{P}_{\text{model}} + \mathbf{t}_{\text{head}} \right)$$

Using `cv2.solvePnP`, the robot extracts the 3D rotation matrix $R_{\text{head}}$, decomposing it into $(Yaw, Pitch, Roll)$:
- **$|Yaw| < 15^\circ$ AND $|Pitch| < 12^\circ$**: Person is looking directly at the robot (**Mutual Eye Contact Confirmed**).
- **$|Yaw| > 35^\circ$**: Person is looking away (Disengaged).

---

### 3. Hands-On Lab & Practical Code References

#### 1. Face Detector Source Code:
- Detector Node: [`ros2_companion_head_kit/src/companion_head_sensors/companion_head_sensors/face_detector.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_sensors/companion_head_sensors/face_detector.py)
- Run Demo 03: `ros2 run companion_head_demos demo_03_vision.py`
