## SOC 03: DISPLAY EMBODIMENT & PROCEDURAL VECTOR FACES

*Purpose: Render expressive digital faces. Master procedural 2D vector eye animation, parametric eyelid curves, emotional pupil dilation, natural autonomous blinking schedules, and viseme lip synchronization.*

### Must Answer
- How does the expression rendering engine generate 2D vector facial features without heavy video playback?
- What are Parametric Eye Geometries (roundness, squinch, upper/lower eyelid curvature)?
- How does Poisson-distributed Autonomous Blinking mimic biological eye lubrication cycles ($2 - 6\text{ seconds}$)?
- How do Pupil Dilation ($r_{\text{pupil}}$) and eye glow convey high cognitive arousal vs calm states?
- What are Visemes, and how do phoneme-to-viseme lookup tables achieve real-time lip synchronization during speech?

### Key Insight
Procedural vector graphics allow continuous mathematical interpolation between emotional states (e.g. from Happy $\to$ Surprised $\to$ Curious) in real time at 60 FPS with zero sprite tearing.

---

### 1. Parametric Vector Eye Architecture

Instead of playing static pre-recorded video clips, each eye is rendered dynamically using 2D Bézier spline curves:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PARAMETRIC VECTOR EYE MODEL                         │
│                                                                             │
│                      Upper Eyelid Arc: y_upper(x)                           │
│                     .-------------------------.                             │
│                    /     [Outer Eye White]     \                            │
│                   |          ┌────────┐         |                           │
│                   |          │  PUPIL │         |                           │
│                   |          │   (r)  │         |                           │
│                    \         └────────┘        /                            │
│                     '-------------------------'                             │
│                      Lower Eyelid Arc: y_lower(x)                           │
│                                                                             │
│   • Parameters: [width, height, eyelid_top, eyelid_bot, pupil_x, pupil_y]   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Autonomous Blinking & Viseme Generation

1. **Poisson Blinking Schedule**:
   Interval between blinks: $\Delta t_{\text{blink}} = -\ln(U) \cdot \lambda_{\text{blink}}$ where $U \sim \text{Uniform}(0, 1)$ and $\lambda = 3.5\text{ s}$.
   Blink duration: Fast close ($40\text{ ms}$), fast reopen ($80\text{ ms}$).
2. **Visemes (Visual Phonemes)**:
   Mapping speech sounds to mouth aperture:
   - `/A/, /AA/` $\implies$ Wide open circle.
   - `/O/, /U/` $\implies$ Narrow horizontal ellipse.
   - `/M/, /B/, /P/` $\implies$ Closed flat horizontal line.

---

### 3. Hands-On Lab & Practical Code References

#### 1. Expression Renderer Source:
- Renderer Node: [`ros2_companion_head_kit/src/companion_head_expression/companion_head_expression/expression_renderer.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/src/companion_head_expression/companion_head_expression/expression_renderer.py)
- Run Demo 01: `ros2 run companion_head_demos demo_01_expressions`
- Automated Verification Suite: [`ros2_companion_head_kit/scripts/test_companion_head_kit.py`](../../Ros2%20learning%20kits/ros2_companion_head_kit/scripts/test_companion_head_kit.py)
