# Article LFE-05: V4 — Topological Navigation: Symbolic Graphs & Visual Landmarks

**Pedagogical Layer:** Symbolic Intelligence & Graph Theory  
**Focus Area:** Graph Representation $G=(V, E)$, AprilTag/ArUco Visual Landmarks, and Global Route Planning  
**Associated Package:** `line_follower_v4_v5_topological`

---

## 1. Separating Geometry from Topology

In V1–V3, the robot was a slave to the black line. It had no concept of where it was or where it was going.
In **V4**, we introduce **Symbolic Intelligence**:
- **Edges ($E$)**: The physical lines on the floor provide geometric trajectory constraints.
- **Vertices / Nodes ($V$)**: Discrete physical intersections tagged with unique visual identifiers (AprilTags / ArUco / QR).

```text
   (N1: Dock) ────────────── (N2: Assembly)
       │                           │
       │                           │
   (N3: Inspection) ──────── (N4: Packaging) ─────── (N5: Storage)
```

---

## 2. Topological Graph Representation in JSON

```json
{
  "nodes": {
    "N1": {"label": "Dock", "neighbors": ["N2", "N3"]},
    "N2": {"label": "Assembly", "neighbors": ["N1", "N4"]},
    "N3": {"label": "Inspection", "neighbors": ["N1", "N4"]},
    "N4": {"label": "Packaging", "neighbors": ["N2", "N3", "N5"]},
    "N5": {"label": "Storage", "neighbors": ["N4"]}
  }
}
```

---

## 3. Shortest Path Planning on Topological Graphs

Given start node $N_{\text{start}}$ and goal node $N_{\text{goal}}$, the robot runs Dijkstra's algorithm to compute an ordered sequence of sub-goals:
$$\Pi = [N_1, N_2, N_4, N_5]$$

---

## 4. Summary & Lessons Learned

Topological navigation transforms the robot from a line follower into an autonomous logistics transport vehicle. In [Article LFE-06](article_lfe_06_v5_edge_state_machines_and_rollback.md), we build the edge traversal and rollback state machine.
