## SOC 11: ACTIVE ATTENTION, MULTI-PARTY ARBITRATION & SALIENCE MAPS

*Purpose: Solve the social attention problem in crowded environments. Build multi-modal Salience Maps (combining visual motion, face proximity, and acoustic direction), arbitrate gaze between multiple people, and manage natural conversational turn-taking.*

### Must Answer
- How does a robot decide where to look when multiple people are speaking or moving in the room?
- What is a Spatial Salience Map ($S(\theta, \phi)$), and how does it integrate visual and acoustic cues?
- How does the Gaze Arbiter balance looking at the primary speaker (70% time) with glancing at other listeners (30% time)?
- What is Social Gaze Aversion, and why does constantly staring into a human's eyes for $> 5\text{ seconds}$ feel aggressive?
- How does the robot smoothly transfer gaze when a second person starts speaking?

### Key Insight
In human social etiquette, unblinking 100% eye contact is perceived as intimidating or psychotic; a natural social robot maintains $\sim 65\%$ eye contact, periodically glancing away briefly during cognitive pauses.

---

### 1. Multimodal Spatial Salience Maps

The 2D spherical salience map $S(\theta, \phi)$ combines:

$$S(\theta, \phi) = w_{\text{audio}} S_{\text{DoA}}(\theta) + w_{\text{face}} S_{\text{face}}(\theta, \phi) + w_{\text{motion}} S_{\text{motion}}(\theta, \phi)$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SPATIAL SALIENCE ARBITRATION                       │
│                                                                             │
│   [Audio DoA Peak at +45 deg] ──┐                                           │
│   [Face 1 at 0 deg (Speaking)]  ├──▶ [Salience Map S(\theta)] ──▶ Gaze Goal │
│   [Face 2 at -30 deg (Silent)]  │                               (\theta*, \phi*)
│   [Movement in Background] ─────┘                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Social Gaze Allocation Heuristic

When conversing with Person A:
- **Speaking State**: Robot maintains $50 - 60\%$ mutual gaze, looking away during sentence planning.
- **Listening State**: Robot maintains $70 - 80\%$ mutual gaze with occasional nods.
- **Multi-Party Glances**: Every $8 - 12\text{ seconds}$, robot glances at Person B for $1.5\text{ seconds}$ to include them in the social circle before returning gaze to Person A.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Gaze Controller & Gesture Generator:
- Gaze Controller: [`ros2_companion_head_kit/src/companion_head_control/companion_head_control/gaze_controller.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_control/companion_head_control/gaze_controller.py)
