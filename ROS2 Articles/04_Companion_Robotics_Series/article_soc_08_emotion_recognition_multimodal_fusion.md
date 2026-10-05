## SOC 08: MULTIMODAL EMOTION RECOGNITION: FACS & ACOUSTIC PROSODY

*Purpose: Perceive human emotional states through visual and auditory cues. Master Paul Ekman's Facial Action Coding System (FACS), extract facial Action Units (AUs), analyze acoustic pitch/prosody, and fuse multimodal emotional evidence.*

### Must Answer
- What is Paul Ekman's Facial Action Coding System (FACS), and what are Action Units (AUs)?
- Which Action Units define the Duchenne Smile (AU6 Cheek Raiser + AU12 Lip Corner Puller)?
- How do acoustic features (Fundamental frequency $F_0$, pitch contour, energy envelope) convey emotional arousal in human speech?
- Why is single-modality emotion recognition unreliable (e.g. a sarcastic smile or calm monotone anger)?
- How does Bayesian Multimodal Fusion combine vision and audio probabilities to estimate user mood?

### Key Insight
Visual expressions convey emotional Valence (happy vs unhappy), while vocal pitch variance and speech rate convey emotional Arousal (calm vs agitated); fusing both modalities yields a complete estimate of user state.

---

### 1. Facial Action Units (FACS)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FACIAL ACTION UNITS (FACS)                         │
│                                                                             │
│   • AU 01: Inner Brow Raiser    ──▶ Sadness / Surprise                      │
│   • AU 04: Brow Lowerer (Furrow)──▶ Anger / Confusion                       │
│   • AU 06: Cheek Raiser         ──▶ Genuine Duchenne Smile                  │
│   • AU 12: Lip Corner Puller    ──▶ Smile / Joy                             │
│   • AU 15: Lip Corner Depressor ──▶ Sadness / Frown                         │
│   • AU 26: Jaw Drop             ──▶ Surprise                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Acoustic Prosody & Pitch Analysis

1. **Fundamental Frequency ($F_0$) Extraction**: Autocorrelation or YIN algorithm on audio frames.
   - High $F_0$ mean + high variance $\implies$ Excitement / Panic.
   - Low $F_0$ mean + low variance $\implies$ Sadness / Monotone.
2. **Speaking Rate & Energy**:
   - Fast cadence + high RMS energy $\implies$ High Arousal ($a > +0.5$).

---

### 3. Hands-On Lab & Practical Code References

#### 1. Testing Multimodal Emotion Recognition:
```bash
# Echo emotion detection topic in ROS2
ros2 topic echo /companion/perceived_emotion
```
- Message Definition: [`ros2_companion_head_kit/src/companion_head_msgs/msg/EmotionDetection.msg`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_msgs/msg/EmotionDetection.msg)
