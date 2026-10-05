## SOC 05: AUDIO PROCESSING: VAD, BEAMFORMING & DIRECTION OF ARRIVAL (DOA)

*Purpose: Give the companion auditory spatial perception. Master Voice Activity Detection (VAD), Time Difference of Arrival (TDOA), Generalized Cross-Correlation with Phase Transform (GCC-PHAT), and microphone array Sound Source Localization (SSL).*

### Must Answer
- How does Voice Activity Detection (VAD) distinguish human speech from ambient background noise in real time?
- What is Sound Source Localization (SSL), and how does a multi-microphone array estimate speaker azimuth ($\theta_{\text{DoA}}$)?
- What is Time Difference of Arrival (TDOA) between two microphones separated by distance $d$?
- How does the Generalized Cross-Correlation with Phase Transform (GCC-PHAT) algorithm find acoustic arrival peaks?
- How does the robot snap its gaze toward the speaker when a sudden voice is heard in the room?

### Key Insight
When someone speaks from behind or to the side of the robot, the camera cannot see them; Sound Source Localization (SSL) calculates the speaker's angular direction in 20 ms, commanding the neck to spin around and make eye contact.

---

### 1. Direction of Arrival (DoA) via Microphone Arrays

Let two microphones be separated by baseline distance $d$. An acoustic wave from azimuth angle $\theta$ arrives at Mic 2 with time delay $\tau$:

$$\Delta \tau = \frac{d \sin\theta}{c}$$

where $c = 343\text{ m/s}$ is the speed of sound in air.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MICROPHONE ARRAY DOA PHYSICS                       │
│                                                                             │
│                                       Acoustic Wavefront                    │
│                                         /   /   /                           │
│                                        /   /   /                            │
│                                       /   /   /                             │
│                  Mic 1 o ────────────/───o Mic 2 (Distance d)               │
│                        │             │                                      │
│                        ◄─ d \sin\theta ─► (Extra Path Length = c \cdot \tau) │
│                                                                             │
│   • \theta = \arcsin( (c \cdot \tau) / d )                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Generalized Cross-Correlation Phase Transform (GCC-PHAT)

To estimate delay $\tau$ in reverberant rooms with acoustic echoes:

$$R_{\text{GCC-PHAT}}(\tau) = \mathcal{F}^{-1} \left\{ \frac{X_1(\omega) X_2^*(\omega)}{|X_1(\omega) X_2^*(\omega)|} \right\}$$

The peak index of $R(\tau)$ gives the exact physical time difference $\tau^* = \arg\max_\tau R(\tau)$, yielding azimuth angle $\theta_{\text{DoA}}$.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Audio Simulator & Sensor Source:
- Audio Node: [`ros2_companion_head_kit/src/companion_head_sensors/companion_head_sensors/audio_simulator.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_sensors/companion_head_sensors/audio_simulator.py)
- Run Demo 04: `ros2 run companion_head_demos demo_04_audio.py`
