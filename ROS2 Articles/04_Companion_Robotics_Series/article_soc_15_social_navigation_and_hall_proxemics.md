## SOC 15: MOBILE COMPANION EMBODIMENT & SOCIAL NAVIGATION (PROXEMICS)

*Purpose: Transform stationary companion interaction into mobile social autonomy. Mount the companion head atop a mobile robot chassis (TurtleBot / AMR), implement Edward T. Hall's Proxemics zones (Intimate, Personal, Social, Public), and master social approach trajectories.*

### Must Answer
- What happens when a companion head is mounted on a mobile base?
- What are Edward T. Hall's 4 Interpersonal Proxemics Zones (Intimate, Personal, Social, Public)?
- How does the robot plan socially compliant navigation trajectories that respect human personal space ($0.45\text{ m} - 1.2\text{ m}$)?
- What is Social Gaze Navigation, and how does the head turn toward a human while the base drives around an obstacle?
- How does the robot decide when to approach a person vs. when to maintain polite distance?

### Key Insight
A mobile companion cannot navigate like an industrial forklift; driving straight into a human's intimate space ($< 45\text{ cm}$) causes discomfort. Social navigation plans smooth curved approaches that signal benign intent and stop at the polite edge of the Personal Zone.

---

### 1. Edward T. Hall's Proxemics Zones

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EDWARD T. HALL'S PROXEMICS ZONES                    │
│                                                                             │
│                         /‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\                       │
│                        /   PUBLIC ZONE (> 3.6 m)     \                      │
│                       /  ┌─────────────────────────┐  \                     │
│                      /   │ SOCIAL ZONE (1.2-3.6 m) │   \                    │
│                     |    │  ┌───────────────────┐  │    |                   │
│                     |    │  │ PERSONAL (0.45m)  │  │    |                   │
│                     |    │  │  ┌─────────────┐  │  │    |                   │
│                     |    │  │  │ INTIMATE    │  │  │    |                   │
│                     |    │  │  │ (< 0.45 m)  │  │  │    |                   │
│                     |    │  │  │    HUMAN    │  │  │    |                   │
│                     |    │  │  │      o      │  │  │    |                   │
│                     |    │  │  └─────────────┘  │  │    |                   │
│                     |    │  │  (NEVER ENTER!)   │  │    |                   │
│                      \   │  └───────────────────┘  │   /                    │
│                       \  │ (Optimal Interaction)   │  /                     │
│                        \ └─────────────────────────┘ /                      │
│                         \___________________________/                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Social Navigation Approach Vector

When approaching a seated or standing user:
1. **Never approach directly from behind**: Always navigate to enter the human's forward field of view ($120^\circ$ cone).
2. **Maintain Gaze Alignment**: While the mobile chassis turns to follow the Nav2 path, the Pan/Tilt head counter-rotates to maintain continuous eye contact.
3. **Decelerate Smoothly**: Slow from $0.4\text{ m/s} \to 0.05\text{ m/s}$ as the robot crosses from Social Zone ($1.8\text{ m}$) into Personal Zone ($0.9\text{ m}$), coming to a stop at $d_{\text{stop}} = 0.85\text{ m}$.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Social Mobile Embodiment Bringup:
- Full System Launch: [`ros2_companion_head_kit/src/companion_head_bringup/launch/full_system.launch.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_bringup/launch/full_system.launch.py)
