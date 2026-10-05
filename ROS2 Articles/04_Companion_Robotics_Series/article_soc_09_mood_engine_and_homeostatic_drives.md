## SOC 09: THE MOOD ENGINE, HOMEOSTATIC DRIVES & BOREDOM DYNAMICS

*Purpose: Give companion robots autonomous internal life. Build the Mood Engine, model artificial homeostatic drives (Curiosity, Social Energy, Boredom), and trigger spontaneous lifelike behaviors when idle.*

### Must Answer
- Why does a purely reactive robot (one that only responds when prompted) feel cold and mechanical?
- What are Artificial Homeostatic Drives (Social Need, Boredom, Curiosity)?
- How does the Boredom Timer accumulate over time when no human interacts with the robot?
- What is Social Energy, and how does extended interaction deplete energy, triggering sleepy or resting behaviors?
- How do spontaneous autonomous behaviors (looking around room, stretching neck, yawning) get generated from internal drives?

### Key Insight
Living creatures do not freeze when idle; when humans leave the room, the companion robot's boredom drive accumulates, prompting it to look around, inspect curious objects, or enter an expressive sleep state.

---

### 1. Homeostatic Drive Dynamics

Let internal drives be modeled as continuous state variables:

$$\frac{d(\text{Boredom})}{dt} = +k_{\text{boredom}} \cdot (1 - \text{HumanPresent})$$
$$\frac{d(\text{SocialEnergy})}{dt} = -k_{\text{drain}} \cdot \text{Interacting} + k_{\text{recharge}} \cdot \text{Resting}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INTERNAL DRIVE STATE FLOW                          │
│                                                                             │
│   [No Human Present for 30s] ──▶ Boredom > 0.70                             │
│                                         │                                   │
│                                         ▼                                   │
│                        [Trigger Spontaneous Behavior]                       │
│                        (Scan room, glance at window, sigh)                  │
│                                         │                                   │
│                                         ▼ (If still alone after 3 min)      │
│                        [Transition to SLEEP / REST Mode]                    │
│                        (Eyes close, head tilts down, breathing LED pulses)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Hands-On Lab & Practical Code References

#### 1. Mood Engine Source Code:
- Source: [`ros2_companion_head_kit/src/companion_head_behaviors/companion_head_behaviors/mood_engine.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_behaviors/companion_head_behaviors/mood_engine.py)
