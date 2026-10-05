# Article LFE-04: V3 — Robust Line Perception: Arrays, Centroids & Intersection Tagging

**Pedagogical Layer:** Sensor Processing & Continuous Outer-Loop Control  
**Focus Area:** 8–16 Channel IR Arrays, Weighted Centroid Math, PD/PID Line Centering, and Crossbar Detection  
**Associated Package:** `line_follower_v2_v3_stabilized`

---

## 1. From Binary Points to Continuous Spatial Distributions

A 2-sensor setup only knows if the line is left or right. An **8-channel analog IR sensor array** perceives the continuous Gaussian reflectance profile of the line under the robot:

```text
IR Array:  [S1]  [S2]  [S3]  [S4]  [S5]  [S6]  [S7]  [S8]
Spatial x: -35mm -25mm -15mm  -5mm  +5mm +15mm +25mm +35mm
Readings:   0.05  0.10  0.45  0.95  0.40  0.08  0.02  0.01
                         ▲
                  [Line Centroid e]
```

---

## 2. Weighted Centroid Formulation

The lateral tracking error $e$ (in meters) is computed using the center-of-mass formula:
$$e = \frac{\sum_{i=1}^{N} w_i \cdot I_i}{\sum_{i=1}^{N} I_i}$$
where $w_i$ is the physical lateral offset of sensor $i$, and $I_i$ is the calibrated reflectance intensity.

---

## 3. Intersection Detection Without Premature Action

At a crossbar or intersection, all sensors concurrently read high intensity:
$$\text{Intersection Detected} \iff \sum_{i=1}^{N} \mathbb{I}(I_i > \theta_{\text{dark}}) \ge N_{\text{threshold}}$$

> **Engineering Design Choice in V2–V3**: The robot **detects and publishes** the intersection flag to telemetry, but **does not alter its course**. It remains dedicated purely to high-speed line tracking, leaving symbolic decisions to V4–V5.

---

## 4. Summary & Lessons Learned

V2–V3 completes the **Physical Intelligence** stage: the robot is smooth, fast ($>0.65\,\text{m/s}$), and stable. In [Article LFE-05](article_lfe_05_v4_topological_graphs_and_symbolic_nodes.md), we introduce symbolic topological graphs.
