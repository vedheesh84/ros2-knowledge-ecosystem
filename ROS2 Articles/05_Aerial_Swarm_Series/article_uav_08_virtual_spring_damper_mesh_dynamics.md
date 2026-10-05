## UAV 08: VIRTUAL SPRING-DAMPER MESHES & ARTIFICIAL POTENTIAL FIELDS

*Purpose: Model robot swarms as continuous physical meta-materials. Formulate virtual spring-damper dynamics between neighboring drones, tune Lennard-Jones and Morse interaction potentials, and prevent oscillatory resonance.*

### Must Answer
- How does a virtual spring-damper mesh treat a multi-drone swarm as a flexible elastic body?
- What is the Lennard-Jones Potential ($U(r) = \epsilon [(\frac{r_0}{r})^{12} - 2(\frac{r_0}{r})^6]$), and how does it balance attraction and repulsion?
- How does virtual damping ($D_{\text{virtual}} (\mathbf{v}_j - \mathbf{v}_i)$) dissipate kinetic energy to prevent infinite swarm ringing?
- How do artificial potential fields guide swarms through complex 3D obstacle corridors?
- How do gyroscopic forces and rotational curl fields escape local potential minima traps?

### Key Insight
By connecting neighboring drones with mathematical virtual springs and dampers, the swarm behaves as a macroscopic viscoelastic fluid: it compresses to squeeze through obstacles and expands automatically once clear.

---

### 1. The Virtual Spring-Damper Interaction Law

For any pair of connected drones $i$ and $j$ separated by distance vector $\mathbf{r}_{ij} = \mathbf{p}_j - \mathbf{p}_i$:

$$\mathbf{F}_{ij} = \underbrace{K_{\text{spring}} (\|\mathbf{r}_{ij}\| - d_{\text{nominal}}) \frac{\mathbf{r}_{ij}}{\|\mathbf{r}_{ij}\|}}_{\text{Elastic Potential Force}} + \underbrace{D_{\text{damper}} (\mathbf{v}_j - \mathbf{v}_i)}_{\text{Viscous Energy Dissipation}}$$

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VIRTUAL SPRING-DAMPER MESH                            │
│                                                                             │
│              [Drone 1] ═══════\/\/\/\/\/\─────── [Drone 2]                  │
│                  ║            (K_spring, D)            ║                    │
│                  ║                                     ║                    │
│             \/\/\/\/\/\                           \/\/\/\/\/\               │
│                  ║                                     ║                    │
│                  ║                                     ║                    │
│              [Drone 4] ═══════\/\/\/\/\/\─────── [Drone 3]                  │
│                                                                             │
│   • Repulsive if dist < d_nominal; Attractive if dist > d_nominal.          │
│   • Damping dissipates kinetic energy to eliminate resonant ringing.        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Hands-On Lab & Practical Code References

#### 1. Testing Swarm Collision Avoidance:
```bash
# Run Demo 05: Swarm collision avoidance under repulsive potential fields
ros2 run swarm_demos demo_05_collision_avoidance
```
