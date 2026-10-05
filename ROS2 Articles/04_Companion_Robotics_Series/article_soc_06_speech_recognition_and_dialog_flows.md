## SOC 06: SPEECH RECOGNITION, WAKE WORDS & CONVERSATIONAL TURN-TAKING

*Purpose: Build fluid conversational interaction. Master local Automatic Speech Recognition (ASR / Whisper), wake-word spotting (Porcupine / OpenWakeWord), conversational turn-taking, and latency management.*

### Must Answer
- How does Wake-Word Spotting maintain continuous low-power listening without overwhelming SBC CPU?
- How does Automatic Speech Recognition (ASR) transcribe streaming audio into text?
- What is Conversational Turn-Taking, and how do silence timeouts and VAD trailing buffers detect when a person finishes talking?
- What causes conversational latency, and why is an end-to-end response time $< 800\text{ ms}$ critical for natural human interaction?
- How does the companion show visual "thinking" feedback on its display face while speech models process queries?

### Key Insight
In human-robot interaction, silence is ambiguous; if the robot takes 1.5 seconds to process a query without visual cues, the human assumes it crashed. Displaying an animated thinking eye state maintains the social connection during computational latency.

---

### 1. The Conversational Turn-Taking Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CONVERSATIONAL TURN-TAKING FLOW                        │
│                                                                             │
│   [Standby State] ──▶ [Wake Word: "Hey Companion"]                          │
│                              │                                              │
│                              ▼                                              │
│   [Listening State] ──▶ [VAD Speech Buffer (Accumulate Audio)]              │
│                              │ (Silence Detected > 600 ms)                  │
│                              ▼                                              │
│   [Thinking State] ───▶ [ASR Transcription (Whisper)]                       │
│    (Display Eyes Spin)       │                                              │
│                              ▼                                              │
│   [Speaking State] ◀─── [Dialogue Engine / LLM Response]                    │
│    (Viseme Lip Sync)         │                                              │
│                              ▼                                              │
│   [Listening State] ◀── (Wait for User Reply / Next Turn)                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Conversational Latency Budget ($< 800\text{ ms}$)

| Pipeline Stage | Subsystem | Latency Budget | Engineering Optimization |
|---|---|---|---|
| **Wake Word** | MicroWakeWord / Porcupine | $50\text{ ms}$ | Small quantized neural net running on 1 core |
| **Silence Detection** | Silero VAD | $150\text{ ms}$ | Trailing silence window before turn boundary |
| **ASR Transcription**| Whisper Tiny / Base (INT8)| $250\text{ ms}$ | GPU / NPU acceleration |
| **Dialogue Response**| Rule Engine / Local SLM | $200\text{ ms}$ | Streaming token generation |
| **TTS Audio Playback**| Piper TTS / Kokoro | $150\text{ ms}$ | Chunked audio streaming |
| **Total Turn Time** | | **$800\text{ ms}$** | **Feels immediate and natural to humans!** |

---

### 3. Hands-On Lab & Practical Code References

#### 1. Testing Speech & Multimodal Interactions:
```bash
# Run Demo 06: Multimodal speech and vision interaction
ros2 run companion_head_demos demo_06_multimodal.py
```
