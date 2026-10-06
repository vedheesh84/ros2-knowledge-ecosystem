## SOC 02: 2-DOF PAN/TILT KINEMATICS, ACTIVE GAZE & SACCADIC MOTION

*Purpose: Master robotic head kinematics and active gaze tracking. Formulate spherical Pan/Tilt coordinate transformations, derive smooth pursuit visual tracking controllers, and implement biological saccadic eye micro-movements.*

### Must Answer
- How do 2-DOF Pan (Yaw: $q_1$) and Tilt (Pitch: $q_2$) spherical kinematics orient the camera optical axis toward a 3D target point?
- What is Smooth Pursuit Tracking, and how do proportional-derivative (PD) gaze controllers eliminate tracking lag?
- What are Saccades, and why do biological eyes execute ballistic $400^\circ/\text{s}$ micro-jumps rather than static staring?
- What is the Vestibulo-Ocular Reflex (VOR), and how does counter-rotating gaze stabilize images during chassis motion?
- How does the Gaze Controller prevent unnatural mechanical jerk via minimum-jerk trajectory generation?

### Key Insight
A robot that stares unblinkingly at a fixed coordinate looks dead or broken; injecting biological saccadic micro-movements and smooth pursuit gaze turns a mechanical pan/tilt unit into an attentive, living social companion.

---

### 1. 2-DOF Pan/Tilt Spherical Kinematics

Let a target face be detected at 3D camera coordinates $\mathbf{p}_{\text{target}} = [x_c, y_c, z_c]^T$ in `camera_color_optical_frame`.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PAN/TILT GAZE GEOMETRY                            │
│                                                                             │
│                                    Target Face (x, y, z)                    │
│                                              o                              │
│                                             /                               │
│                                            / Line of Sight                  │
│                                           / (Distance d)                    │
│             Tilt Axis (q_tilt) ──────────o                                  │
│                                          │                                  │
│                                          │ Neck Height h                    │
│                                          │                                  │
│             Pan Axis (q_pan) ────────────o                                  │
│                                          │                                  │
│                                     [Base Mount]                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Analytical Gaze Angle Formulas:
$$q_{\text{pan, error}} = \text{atan2}(x_c, z_c)$$
$$q_{\text{tilt, error}} = \text{atan2}(-y_c, \sqrt{x_c^2 + z_c^2})$$

---

### 2. Saccades vs. Smooth Pursuit Gaze

1. **Smooth Pursuit ($< 30^\circ/\text{s}$)**: Closed-loop visual feedback keeping a moving human's face centered in the camera frame ($e_x \approx 0, e_y \approx 0$).
2. **Saccadic Motion ($200^\circ - 500^\circ/\text{s}$)**: Rapid, open-loop ballistic gaze shifts executed when attention switches to a new auditory or visual event.
3. **Biological Gaze Jitter**: Periodic tiny micro-saccades ($\pm 0.5^\circ$ at $2 - 4\text{ Hz}$) that prevent optical fixation fatigue and signal attention to the human partner.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Gaze Controller Source Code:
- Gaze Controller: [`ros2_companion_head_kit/src/companion_head_control/companion_head_control/gaze_controller.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_control/companion_head_control/gaze_controller.py)
- Run Demo 02: `ros2 run companion_head_demos demo_02_servo_control`
- Physical Microcontroller Firmware: [`ros2_companion_head_kit/arduino/companion_head_controller/companion_head_controller.ino`](../../Ros2%20learning%20kits/ros2_companion_head_kit/arduino/companion_head_controller/companion_head_controller.ino)
- Desktop Pseudo-Hardware Emulator: [`ros2_companion_head_kit/scripts/pseudo_companion_head_emulator.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/scripts/pseudo_companion_head_emulator.py)
- Hardware Interface Plugin: [`ros2_companion_head_kit/src/companion_head_hardware/`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_hardware/)
- Automated Verification Suite: [`ros2_companion_head_kit/scripts/test_companion_head_kit.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/scripts/test_companion_head_kit.py)
