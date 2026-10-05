## SOC 10: SOCIAL BEHAVIOR STATE MACHINES & BEHAVIOR TREES

*Purpose: Orchestrate high-level social autonomy. Build hierarchical social state machines and Behavior Trees coordinating Idle scanning, Orienting, Greeting, Listening, Conversing, and Confused recovery behaviors.*

### Must Answer
- What are the core states of an interactive companion robot?
- How does the robot transition from `IDLE` $\to$ `ATTENDING` when a person enters the room?
- How does the `GREETING` sequence coordinate mutual eye contact, a cheerful chirp sound, and a warm smile?
- How does the state machine handle the `CONFUSED` state when ASR fails or audio is unintelligible?
- How do Behavior Trees manage concurrent social tasks (such as maintaining eye contact while listening)?

### Key Insight
Social interaction is an orchestrated dance of timing; interrupting a human mid-sentence destroys rapport, while waiting 2 seconds to acknowledge a greeting feels awkward and broken.

---

### 1. The Hierarchical Social State Machine

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPANION SOCIAL STATE MACHINE                       │
│                                                                             │
│         [IDLE / SLEEP] ──(Face / Voice Detected)──▶ [ORIENTING / ATTENDING] │
│               ▲                                              │              │
│               │ (Timeout)                        (Person Looks)             │
│               │                                              ▼              │
│         [GOODBYE / EXIT] ◀──(Person Leaves)─────── [GREETING PROTOCOL]      │
│               ▲                                              │              │
│               │                                              ▼              │
│         [CONVERSING] ◀───────────────────────────── [ACTIVE LISTENING]      │
│               │                                              │              │
│               └──(ASR Unclear > 2x)──▶ [CONFUSED / CLARIFY] ─┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Hands-On Lab & Practical Code References

#### 1. Behavior Controller Source Code:
- Behavior Controller: [`ros2_companion_head_kit/src/companion_head_behaviors/companion_head_behaviors/behavior_controller.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_behaviors/companion_head_behaviors/behavior_controller.py)
- Run Demo 07: `ros2 run companion_head_demos demo_07_full_companion.py`
