# ros2_companion_head_kit

**Social & Affective Robotics Learning Kit**

A systems learning platform for human-robot interaction, pan-tilt gaze tracking, emotion synthesis, and behavior state machines in ROS2.

---

## 1. Identity & Purpose

This is the social and affective robotics kit in the Intelligent Ecosystem series, focusing on multi-modal human-robot interaction (HRI):

| Kit / Prerequisite | Focus | Core Skills Mastered | Link |
|---|---|---|---|
| **ROS2_kits_ws** | Fundamentals | Lifecycle, topics, services, actions | [README](../ROS2_kits_ws/README.md) |
| **turtlebot3_ws** | AMR Foundation | SLAM, Nav2, EKF state estimation | [README](../../AMR_ws/turtlebot3_ws/README.md) |
| **ros2_arm_kit** | Kinematics Foundation | Analytical FK/IK, trajectory generation | [README](../ros2_arm_kit/README.md) |
| **ros2_mobile_manipulator_kit** | Systems Integration | Coordinated perception & manipulation | [README](../ros2_mobile_manipulator_kit/README.md) |
| **ros2_companion_head_kit** | Interaction Intelligence | Gaze tracking, emotion models, FSM, face display | Primary Workspace |

**Prerequisites:** Familiarity with ROS2 communications, ros2_control, and launch file composition.

---

## Modular Embodiment Architecture

> [!NOTE]
> **Dual-Mode Deployment: Desktop vs. Mobile Companion**
> The Companion Head is engineered with a modular mechanical and computational interface:
> 1. **Standalone Desktop Agent**: Sits on a desk for conversational AI, gaze tracking, and facial emotion display.
> 2. **Mobile Social Robot**: Mounts directly onto the mobile manipulator / AMR chassis, turning the mobile base into an expressive autonomous service robot.

---

## 2. Workspace Structure

```text
ros2_companion_head_kit/
├── SYSTEM_ARCHITECTURE.md                # Detailed system & ontological analysis
├── README.md                             # Primary entry point
└── src/
    ├── companion_head_msgs/              # Message definitions (emotions, mood, gestures)
    ├── companion_head_description/       # Pan-tilt URDF, ros2_control configuration
    ├── companion_head_gazebo/            # Gazebo simulation world & models
    ├── companion_head_bringup/           # Master orchestration launch files
    ├── companion_head_sensors/           # Vision (face detector) & audio processing
    ├── companion_head_control/           # Gaze controller & gesture generator
    ├── companion_head_expression/        # 30 FPS virtual face expression renderer
    ├── companion_head_behaviors/         # Continuous mood engine & behavior FSM
    └── companion_head_demos/             # Progressive learning demos & breakers
```

---

## 3. Quick Start

```bash
# Build
cd ros2_companion_head_kit
colcon build --symlink-install
source install/setup.bash

# Visualize Head URDF (no simulation)
ros2 launch companion_head_description display.launch.py

# Launch Full Simulated Companion Head System
ros2 launch companion_head_bringup full_system.launch.py
```

---

## 4. Architecture & Data Flow

Detailed system architecture and agent-based design are documented in [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md).

```text
  /camera/image_raw ──▶ [face_detector] ──▶ /gaze/target ──▶ [gaze_controller]
                              │                                     │
                              ▼                                     ▼
                      /faces/detections                  /joint_trajectory
                              │                                     ▲
                              ▼                                     │
   /audio/tone ───────▶ [mood_engine]                    [gesture_generator]
                              │                                     ▲
                              ▼                                     │
                     /expression/target ──▶ [behavior_controller] ──┘
                              │
                              ▼
                    [expression_renderer] ──▶ /face/display (30 FPS)
```

---

## 5. Learning Demos & Failure Injection

| Demo | Focus | What You Learn |
|------|-------|----------------|
| **01** | Pan-Tilt Gaze | Inverse kinematics & trajectory smoothing for eye-contact |
| **02** | Face Detection | 2D bbox to 3D spatial target estimation |
| **03** | Expression Rendering | Vector-based facial animation on virtual LCD display |
| **04** | Mood Dynamics | Valence-Arousal-Engagement continuous decay model |
| **05** | Behavior State Machine | Coordinated gestures, speech responses, and sleep states |

---

## 6. Social & Companion Robotics Learning Curriculum (16 Articles)

This kit is accompanied by the comprehensive 16-article **[Social & Companion Robotics Series](../../ROS2%20Articles/COMPLETE_INDEX.md#vertical-4-social--companion-robotics-series-16-articles)**:

- **Module 1 (Embodiment & Face Display)**: [Embodied Social Intelligence (SOC 01)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_01_embodied_social_intelligence.md) | [2-DOF Pan/Tilt Gaze Kinematics (SOC 02)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_02_2dof_pan_tilt_kinematics_and_gaze.md) | [Display Embodiment & Vector Faces (SOC 03)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_03_display_embodiment_and_procedural_faces.md)
- **Module 2 (Multimodal Social Perception)**: [Face Detection & 68 Landmarks (SOC 04)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_04_face_detection_landmarks_and_gaze.md) | [Audio VAD, Beamforming & DoA (SOC 05)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_05_audio_vad_beamforming_and_ssl.md) | [Speech Recognition & Turn-Taking (SOC 06)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_06_speech_recognition_and_dialog_flows.md)
- **Module 3 (Affective State Modeling)**: [Affective Computing & Circumplex Model (SOC 07)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_07_affective_computing_and_circumplex_model.md) | [Multimodal Emotion Recognition (SOC 08)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_08_emotion_recognition_multimodal_fusion.md) | [Mood Engine & Homeostatic Drives (SOC 09)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_09_mood_engine_and_homeostatic_drives.md)
- **Module 4 (Social Behavior & Attention)**: [Social Behavior State Machines & BT (SOC 10)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_10_social_behavior_state_machines_and_bt.md) | [Active Attention & Salience Maps (SOC 11)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_11_active_attention_and_salience_arbitration.md) | [Non-Verbal Gestures & Body Language (SOC 12)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_12_non_verbal_gestures_and_body_language.md)
- **Module 5 (Multimodal Expression)**: [Multimodal Synchronization (SOC 13)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_13_multimodal_expression_synchronization.md) | [Speech Synthesis & Prosody (SOC 14)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_14_speech_synthesis_and_emotional_prosody.md)
- **Module 6 (Mobile Embodiment & Resilience)**: [Mobile Embodiment & Hall's Proxemics (SOC 15)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_15_social_navigation_and_hall_proxemics.md) | [Long-Term Interaction & Resilience (SOC 16)](../../ROS2%20Articles/04_Companion_Robotics_Series/article_soc_16_long_term_interaction_and_social_resilience.md)

---

## 7. License

MIT License. Learn freely, share widely.
