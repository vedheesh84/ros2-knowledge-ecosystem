## SOC 13: MULTIMODAL EXPRESSION SYNCHRONIZATION: FACE, SOUND & MOTION

*Purpose: Master multimodal expressive synchronization. Learn how to trigger visual eye shapes, earcon audio chimes, head nod gestures, and synthesized speech with millisecond alignment to create cohesive, believable social actions.*

### Must Answer
- Why does a temporal mismatch between mouth visemes, head nod, and audio speech feel jarring and artificial?
- What is an Earcon, and how do non-verbal procedural sound chimes communicate emotional state faster than words?
- How does the Expression Coordinator synchronize 4 independent output modalities (Display, Audio, Servos, Speech)?
- What is the Master Expression Message (`companion_head_msgs/msg/Expression.msg`)?
- How do we handle race conditions when a user interrupts the robot mid-expression?

### Key Insight
Human communication is deeply multimodal: a smile without head movement feels frozen; speech without eye movement feels robotic. True social expression requires synchronized orchestration across eyes, voice, motion, and sound.

---

### 1. The Multimodal Synchronization Timeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MULTIMODAL EXPRESSION TIMELINE                         │
│                                                                             │
│   t = 0 ms:     [Trigger: GREETING ACTION]                                  │
│                 │                                                           │
│   t = 20 ms:    ├──▶ [DISPLAY]: Eyes morph from Neutral ──▶ Happy (60 FPS)  │
│                 │                                                           │
│   t = 40 ms:    ├──▶ [SERVOS]: Head tilts down 10 deg (Nod Gesture)         │
│                 │                                                           │
│   t = 60 ms:    ├──▶ [AUDIO]: Play cheerful two-tone earcon chime (120 ms)  │
│                 │                                                           │
│   t = 200 ms:   └──▶ [SPEECH]: Begin TTS audio stream with lip visemes      │
│                                                                             │
│   • Millisecond-level alignment produces organic, lifelike behavior!        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The Master Expression Message Schema

From `companion_head_msgs/msg/Expression.msg`:
- `string expression_name` (`HAPPY`, `CURIOUS`, `CONFUSED`, `SURPRISED`, `SLEEPY`)
- `float32 intensity` ($0.0 \to 1.0$)
- `float32 duration` (seconds)
- `bool play_audio_chime`
- `string speech_text` (optional)

---

### 3. Hands-On Lab & Practical Code References

#### 1. Running Multimodal Expression Demo:
```bash
# Run Demo 06: Multimodal synchronized expression
ros2 run companion_head_demos demo_06_multimodal.py
```
- Message Definition: [`ros2_companion_head_kit/src/companion_head_msgs/msg/Expression.msg`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_msgs/msg/Expression.msg)
