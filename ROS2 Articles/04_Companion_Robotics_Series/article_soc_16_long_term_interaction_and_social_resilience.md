## SOC 16: LONG-TERM INTERACTION, SOCIAL RESILIENCE & FAILURE RECOVERY

*Purpose: Build lasting human-robot companionship. Master long-term interaction dynamics, handle user habituation, design graceful conversational failure recoveries, and manage social etiquette.*

### Must Answer
- What is User Habituation, and why do people lose interest in static companion robots after 3 days?
- How do dynamic mood evolution, memory of past interactions, and episodic learning maintain long-term engagement?
- What are Social Failure Recoveries (what does the robot do when it misinterprets a command or fails ASR)?
- How does admitting fallibility with an apologetic head tilt and a self-deprecating chime repair human trust?
- What is the 10-point Social Hardware & Software Diagnostic Checklist?

### Key Insight
When a robot fails to understand a command, pretending nothing happened infuriates users; acknowledging confusion with a puzzled eye expression and asking for clarification strengthens social rapport.

---

### 1. Graceful Social Failure Recovery Protocol

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SOCIAL FAILURE RECOVERY PROTOCOL                       │
│                                                                             │
│   [Speech Unintelligible / ASR Confidence < 0.40]                           │
│          │                                                                  │
│          ▼                                                                  │
│   [Step 1: Express Non-Verbal Confusion]                                    │
│   • Eyelids tilt in diagonal puzzlement; head tilts 12 deg.                 │
│                                                                             │
│   ▼                                                                         │
│   [Step 2: Play Inquisitive Earcon Sound]                                   │
│   • Soft rising two-tone chime ("Hmm?").                                    │
│                                                                             │
│   ▼                                                                         │
│   [Step 3: Polite Clarification Prompt]                                     │
│   • "I'm sorry, I didn't catch that. Could you say that again?"             │
│                                                                             │
│   ▼                                                                         │
│   [Step 4: Re-open VAD Listening Window]                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. The 10-Point Companion Diagnostic Checklist

1. **Display Refresh**: Verify OLED/LCD runs at stable $60\text{ FPS}$ without frame stutter.
2. **Servo Noise**: Ensure servos operate quietly with smooth minimum-jerk filtering.
3. **Camera Exposure**: Verify face landmarks track under low-light evening conditions.
4. **VAD Sensitivity**: Check voice detection does not trigger on robot's own motor noise.
5. **AEC (Acoustic Echo Cancellation)**: Ensure robot does not transcribe its own TTS voice!
6. **Mutual Gaze Accuracy**: Verify head centers directly on user's eye level.
7. **Mood Stability**: Check mood engine does not oscillate into erratic emotional swings.
8. **Breathing Pulse**: Verify idle breathing oscillation runs continuously.
9. **SBC CPU Temperature**: Ensure multi-modal pipeline leaves $> 30\%$ CPU headroom.
10. **E-Stop & Mute**: Verify physical privacy mute button immediately cuts microphone.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Running Failure Breakers:
```bash
# Test display recovery
ros2 run companion_head_demos break_display.py

# Test camera tracking recovery
ros2 run companion_head_demos break_camera.py

# Test servo recovery
ros2 run companion_head_demos break_servo.py
```
