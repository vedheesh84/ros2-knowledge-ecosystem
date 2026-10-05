## SOC 07: AFFECTIVE COMPUTING & RUSSELL'S CIRCUMPLEX MODEL OF AFFECT

*Purpose: Model dynamic emotional states mathematically. Master James Russell's 2D Circumplex Model of Affect (Valence vs. Arousal), formulate emotional decay dynamics, and map continuous affective coordinates to facial expressions.*

### Must Answer
- What is Affective Computing, and why is emotion essential for intuitive human-robot interaction?
- What is James Russell's Circumplex Model of Affect ($2D\ Valence\text{-}Arousal\ Space$)?
- What do Valence ($v \in [-1, 1]$, pleasantness) and Arousal ($a \in [-1, 1]$, physiological activation) represent?
- How do classic discrete emotions (Joy, Surprise, Anger, Sadness, Fear, Boredom) map to points in the $V-A$ plane?
- How do exponential emotional decay differential equations return the robot's mood to neutral homeostasis over time?

### Key Insight
Instead of hard-coding brittle discrete switches between "Happy" and "Sad", the Circumplex Model treats emotion as a continuous 2D coordinate $(v, a)$, enabling smooth mathematical transitions and nuanced blending of expressions.

---

### 1. Russell's 2D Circumplex Model of Affect

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RUSSELL'S CIRCUMPLEX MODEL OF AFFECT                  │
│                                                                             │
│                                HIGH AROUSAL (+1)                            │
│                                       │                                     │
│                     [ANGRY / ALARMED] │ [EXCITED / SURPRISED]               │
│                        (-0.6, +0.7)   │    (+0.6, +0.8)                     │
│                                       │                                     │
│                                       │          [HAPPY / DELIGHTED]        │
│                                       │             (+0.8, +0.4)            │
│   NEGATIVE VALENCE (-1) ──────────────┼────────────── POSITIVE VALENCE (+1) │
│                                       │                                     │
│                     [BORED / SAD]     │          [CALM / RELAXED]           │
│                      (-0.7, -0.5)     │             (+0.5, -0.5)            │
│                                       │                                     │
│                                       │                                     │
│                                LOW AROUSAL (-1)                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Emotional Homeostasis & Exponential Decay Dynamics

When a social stimulus (such as a compliment or sudden loud bang) displaces the robot's internal mood vector $\mathbf{m}(t) = [v(t), a(t)]^T$:

$$\mathbf{\dot{m}}(t) = -\lambda_{\text{decay}} (\mathbf{m}(t) - \mathbf{m}_{\text{homeostasis}}) + \mathbf{s}_{\text{stimulus}}(t)$$

- **$\lambda_{\text{decay}}$**: The rate of emotional return to neutral baseline ($v=0, a=0$).
- If no new stimuli arrive for $10\text{ seconds}$, a startled robot ($a = +0.8$) smoothly relaxes back to calm baseline ($a = 0.0$).

---

### 3. Hands-On Lab & Practical Code References

#### 1. Mood Engine Source Code:
- Mood Engine: [`ros2_companion_head_kit/src/companion_head_behaviors/companion_head_behaviors/mood_engine.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_behaviors/companion_head_behaviors/mood_engine.py)
- Run Demo 05: `ros2 run companion_head_demos demo_05_mood.py`
