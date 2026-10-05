## LEG 17: ADAPTIVE TERRAIN LOCOMOTION: SLOPES, STAIRS & BLIND PUSH RECOVERY

*Purpose: Master real-world adaptive locomotion across challenging environments. Implement chassis pitch adaptation on slopes, staircase climbing reflexes, early-contact and late-contact swing extensions, and aggressive push recovery.*

### Must Answer
- How does the robot adapt its chassis roll and pitch to align with the average slope of the terrain?
- How do Early-Contact and Late-Contact (stepping into a ditch) swing reflexes operate?
- What are Staircase Climbing reflexes (high knee retraction, toe-clearance offsets)?
- How does the robot recover when hit by an aggressive lateral kick or external collision?
- What is a Fallen Robot Self-Righting behavior, and how does the state machine re-orient the body from upside down?

### Key Insight
Terrain adaptation combines feedforward vision (stepping on high stones) with reflexive feedback (instantly locking a leg into stance if it hits the ground earlier than expected).

---

### 1. Reflexive Swing Contact Adaptations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       REFLEXIVE CONTACT ADAPTATIONS                         │
│                                                                             │
│   1. EARLY TOUCHDOWN REFLEX (Obstacle / Step Up):                           │
│   • Foot strikes ground at s = 0.70 (expected s = 1.00).                    │
│   • Reflex: IMMEDIATELY terminate swing phase, declare STANCE, and notify   │
│     MPC to begin generating supportive ground reaction force.               │
│                                                                             │
│   2. LATE TOUCHDOWN REFLEX (Ditch / Step Down):                             │
│   • Swing phase reaches s = 1.00 but foot switch senses NO contact.         │
│   • Reflex: Extend leg downwards at v_z = -0.3 m/s until ground is found;   │
│     delay body weight transfer until contact is confirmed!                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Slope Pitch Adaptation

When traversing a hill of inclination $\alpha$:
- Align the body trunk pitch angle with the terrain slope ($\theta_{\text{trunk}} = \alpha$) to maintain symmetrical leg reachability.
- Adjust the gravity feedforward vector in MPC: $\mathbf{g}_{\text{local}} = R^T \mathbf{g}_{\text{world}}$.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Testing Terrain Adaptation Breakers:
```bash
# Test terrain obstacle adaptation
ros2 run quadruped_demos demo_06_terrain_adaptation

# Test push recovery breaker
ros2 run quadruped_demos break_gait.py
```

