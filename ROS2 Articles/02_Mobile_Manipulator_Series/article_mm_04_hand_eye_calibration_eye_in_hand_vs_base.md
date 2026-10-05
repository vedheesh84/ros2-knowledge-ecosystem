## MM 04: HAND-EYE CALIBRATION: EYE-IN-HAND VS. EYE-TO-BASE ($AX=XB$)

*Purpose: Master robotic hand-eye calibration. Compare Eye-in-Hand (camera on wrist) and Eye-to-Hand / Eye-to-Base (camera on chassis) topologies, formulate the classical $AX = XB$ matrix equation, and understand calibration algorithms.*

### Must Answer
- What is Hand-Eye Calibration, and why does an inaccurate camera-to-arm extrinsic transform cause missed grasps?
- What are the fundamental trade-offs between Eye-in-Hand (wrist mounted) and Eye-to-Base (chassis mounted)?
- What is the classical $AX = XB$ Sylvester matrix equation, and how does it determine the unknown transformation $X$?
- How do calibration targets (Checkerboards, CharuCo boards, AprilTags) provide ground-truth spatial measurements?
- How do calibration residuals propagate through kinematics to produce end-effector positioning error?

### Key Insight
Even with sub-millimeter visual object detection, a $3^\circ$ extrinsic angular calibration error between the camera mounting bracket and the arm base will displace the grasp target by over $2\text{ cm}$ at a reach distance of $40\text{ cm}$.

---

### 1. Eye-in-Hand vs. Eye-to-Base Topologies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAMERA MOUNTING CONFIGURATIONS                        │
│                                                                             │
│   EYE-IN-HAND (Camera on Wrist / Link 4):                                   │
│   • Camera moves with the end-effector.                                     │
│   • Pros: High close-up resolution during grasping; immune to body shadow.  │
│   • Cons: Limited field of view while stowed; arm cables flex repeatedly.   │
│   • Calibration Target: Find transformation from Tool Flange to Camera.     │
│                                                                             │
│   EYE-TO-BASE (Camera on Mobile Chassis / Mast):                            │
│   • Camera is stationary relative to base_link.                             │
│   • Pros: Wide global field of view; detects objects while driving.         │
│   • Cons: Arm can occlude target during reaching; lower close-up resolution.│
│   • Calibration Target: Find transformation from Base Link to Camera.       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Mathematical Formulation: The $AX = XB$ Calibration Problem

Let a robot arm move through $N$ distinct calibration poses while observing a stationary calibration board (CharuCo / AprilTag):
- Let $A_i = T_{\text{gripper}, i}^{-1} \cdot T_{\text{gripper}, j}$ be the relative transformation between two arm poses.
- Let $B_i = T_{\text{cam\_target}, i} \cdot T_{\text{cam\_target}, j}^{-1}$ be the relative transformation measured by the camera.
- Let $X$ be the unknown static transformation between the camera and the robot frame.

$$A_i X = X B_i$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE AX = XB CLOSED LOOP                            │
│                                                                             │
│           [Arm Pose i] ──────────── A_i ───────────▶ [Arm Pose j]           │
│                │                                          │                 │
│                X (Unknown Extrinsic)                      X (Unknown)       │
│                ▼                                          ▼                 │
│         [Camera Pose i] ─────────── B_i ───────────▶ [Camera Pose j]        │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Solving $AX = XB$:
1. **Tsai-Lenz Algorithm (1989)**: Decouples rotation from translation using angle-axis representations. Solves rotation via linear least squares, then solves translation directly.
2. **Park-Bryan Algorithm (1994)**: Uses Lie Algebra $SO(3)$ matrix logarithms to minimize geometric error on the rotation manifold.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Testing Extrinsic Calibration Errors:
```bash
# Inject calibration offset fault into camera TF
ros2 run mobile_manipulator_demos break_grasp_frame.py
```
Observe how injecting a $0.03\text{ m}$ calibration error causes the gripper to close prematurely in empty air.
