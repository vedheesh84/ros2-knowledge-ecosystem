## SOC 14: SPEECH SYNTHESIS & EMOTIONAL PROSODY MODULATION

*Purpose: Give companion robots expressive voices. Master neural Text-to-Speech (TTS), SSML markup, dynamic pitch and rate prosody modulation based on emotional state, and non-verbal vocalizations (sighs, gasps, giggles).*

### Must Answer
- What is Emotional Prosody, and why does monotone flat TTS sound unfeeling and boring?
- How does Speech Synthesis Markup Language (SSML) control `<prosody pitch="+15%" rate="1.1">` dynamically?
- How does the Mood Engine's continuous Valence-Arousal coordinate modulate voice pitch ($F_0$) and cadence in real time?
- What are Non-Verbal Vocalizations (chuckles, sighs, inquisitive hums), and how do they enhance conversational flow?
- How do lightweight local neural TTS engines (Piper / Kokoro) run in real-time on edge microcomputers?

### Key Insight
Saying *"Hello, good morning!"* with high pitch and upbeat cadence conveys genuine warmth; saying the same sentence with low pitch and slow rate conveys boredom. Prosody modulation transforms text into emotion.

---

### 1. Emotional Prosody Modulation Equations

Given internal Valence $v \in [-1, 1]$ and Arousal $a \in [-1, 1]$ from the Mood Engine:

$$\text{Pitch Scale} = 1.0 + 0.25 \cdot v + 0.35 \cdot a$$
$$\text{Speaking Rate} = 1.0 + 0.20 \cdot a$$
$$\text{Volume (Gain)} = 1.0 + 0.15 \cdot a$$

- **Excited / Happy ($v=+0.8, a=+0.7$)**: Pitch $+45\%$, Rate $+14\%$ (Brisk, bright tone).
- **Sad / Dejected ($v=-0.6, a=-0.5$)**: Pitch $-32\%$, Rate $-10\%$ (Subdued, slow cadence).

---

### 2. Hands-On Lab & Practical Code References

#### 1. Testing Audio Breakers:
```bash
# Test audio failure recovery
ros2 run companion_head_demos break_audio.py
```
