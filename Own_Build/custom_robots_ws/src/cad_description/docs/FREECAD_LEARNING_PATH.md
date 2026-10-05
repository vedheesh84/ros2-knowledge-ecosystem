# FreeCAD Learning Path — CAD Mobile Manipulator Robot

Step-by-step manual design guide for building the robot from your reference image using FreeCAD, then integrating with the ROS 2 `cad_description` package.

**Reference image:** `/home/bhuvanesh/Downloads/ChatGPT Image Jul 1, 2026, 02_35_22 PM.png`

**ROS package:** `cad_ws/src/cad_description/`

**STL output folder:** `cad_ws/src/cad_description/meshes/`

---

## Division of work

| Task | Who |
|------|-----|
| FreeCAD modeling (all 14 parts) | **You** |
| STL export to `meshes/` | **You** |
| RViz preview after each part | **You** |
| URDF / launch / Gazebo setup | Already done (agent) |
| URDF joint tuning after your CAD | Agent (when you say "execute the plan") |

---

## Step 0 — FreeCAD setup

1. Install FreeCAD: `sudo apt install freecad`
2. Open FreeCAD → **Edit → Preferences → General → Units** → `MKS (m/kg/s/degree)`
3. **View → Standard views → Isometric**
4. Enable workbenches: **Part** (primary), **Part Design** (optional), **Mesh** (for export)
5. Save project as: `cad_robot.FCStd`
6. Read the coordinate rules below before creating geometry

---

## Learning milestones (check off as you go)

- [ ] Lesson A: Create a box and set Placement (`base_link`)
- [ ] Lesson B: Create cylinder + fuse shapes (`wheel`, `lidar`)
- [ ] Lesson C: Use Array/pattern for treads (wheel detail)
- [ ] Lesson D: Build a multi-body assembly in one file
- [ ] Lesson E: Export one STL and preview in RViz
- [ ] Lesson F: Export all 14 STLs and replace `meshes/`

---

## Coordinate system (read first)

URDF frame for the robot:

```
        Z (up)
        |
        |   X (forward / front of robot)
        |  /
        | /
        +-------- Y (left)
```

- **base_link origin:** Center of chassis on the ground
- **Wheel origin:** Center of the axle (rotates around Y-axis)
- **Arm joints:** Arm extends along +Z for each link segment
- **Export rule:** Each STL's joint must sit at FreeCAD (0,0,0) when exported alone

**Set origin in FreeCAD:**
1. Model the part, then adjust **Data → Placement → Position**
2. Or build centered on origin using half-dimension offsets from the start

---

## Part list and modeling order

| # | STL filename | Size (m) | Origin location |
|---|--------------|----------|-----------------|
| 1 | `base_link.stl` | 0.75 × 0.55 × 0.30 | Center of bottom face |
| 2 | `wheel.stl` | R=0.14, W=0.10 | Axle center |
| 3 | `suspension.stl` | H=0.12 | Top mount on chassis |
| 4 | `lidar.stl` | R=0.055, H=0.07 | Bottom of base plate |
| 5 | `camera.stl` | 0.10 × 0.04 × 0.05 | Back mounting face |
| 6 | `led_strip.stl` | 0.18 × 0.015 × 0.008 | Center of strip |
| 7 | `arm_base.stl` | R=0.07, H=0.06 | Bottom of pedestal |
| 8 | `shoulder_link.stl` | 0.10 × 0.12 × 0.14 | Base center (pan joint) |
| 9 | `upper_arm_link.stl` | L=0.28 | Bottom center |
| 10 | `forearm_link.stl` | L=0.22 | Bottom center |
| 11 | `wrist_link.stl` | ~0.06 | Bottom center |
| 12 | `gripper_base.stl` | 0.08 × 0.05 × 0.04 | Wrist mount |
| 13 | `gripper_finger.stl` | L=0.10 | Base of finger |
| 14 | `arm_camera.stl` | 0.05 × 0.03 × 0.03 | Mount face center |

**Order:** 1 → 2 → 3 → … → 14

---

## Part 1: `base_link.stl` — Main chassis

**Goal:** Black box body with panel lines.

1. Switch to **Part** workbench
2. **Part → Primitives → Cube** — Length=`0.75`, Width=`0.55`, Height=`0.30`
3. **Placement** → Position: X=`0`, Y=`0`, Z=`0.15` (bottom at Z=0)
4. Rename: `base_main`
5. Add top panel: Cube `0.68 × 0.48 × 0.04`, Position Z=`0.32` → rename `base_top_panel`
6. Add front lip: Cube `0.72 × 0.02 × 0.22`, Position Z=`0.11`, Y=`0.265`
7. Select all → **Part → Boolean → Union (Fuse)**
8. Rename: `base_link`
9. Export (see Export section below)

**Learn:** Primitives, Placement, Boolean Fuse

---

## Part 2: `wheel.stl` — Off-road tire

1. Hide `base_link`
2. **Cylinder** Radius=`0.14`, Height=`0.10`, Rotation=`90°` on **Y** axis
3. Rename: `wheel_tire`
4. **Cube** tread: `0.02 × 0.018 × 0.015` at X=`0.14`, Y=`-0.009`
5. **Polar Array** — 24 copies, axis Y, 360°
6. Fuse tire + treads → rename `wheel`
7. Axle center at origin (0,0,0)

**Learn:** Cylinder rotation, polar array

---

## Part 3: `suspension.stl` — Red coil spring

1. Top mount cube: `0.06 × 0.04 × 0.04`, Z=`0.08`
2. Bottom mount cube: `0.08 × 0.06 × 0.03`, Z=`-0.06`
3. Spring: small cylinders in a ring (R=`0.028`) or one helix sweep
4. Fuse → rename `suspension`
5. Origin at top mount center

**Learn:** Multi-part fuse, spring geometry

---

## Part 4: `lidar.stl` — LiDAR puck

1. Cylinder R=`0.055`, H=`0.04`
2. Cylinder R=`0.048`, H=`0.025`, Z=`0.032`
3. Mount plate cube: `0.08 × 0.08 × 0.015`, Z=`-0.027`
4. Fuse → rename `lidar`
5. Origin at bottom center of plate

---

## Part 5: `camera.stl` — Front camera

1. Body cube: `0.10 × 0.04 × 0.05`
2. Lens housing: `0.06 × 0.02 × 0.04`, X=`0.02`, Z=`0.045`
3. Lens cylinder: R=`0.012`, H=`0.02`, rot 90° X, X=`0.05`, Z=`0.045`
4. Fuse → rename `camera`
5. Origin at back mounting face (X=0)

---

## Part 6: `led_strip.stl` — LED bar

1. Cube: `0.18 × 0.015 × 0.008`, centered at origin
2. Rename: `led_strip` (color set in URDF)

---

## Part 7: `arm_base.stl` — Arm pedestal

1. Cylinder R=`0.07`, H=`0.06`, Z=`0.03`
2. Flange cube: `0.12 × 0.12 × 0.025`, Z=`0.012`
3. Fuse → rename `arm_base`

---

## Part 8: `shoulder_link.stl` — Shoulder housing

1. Body cube: `0.10 × 0.12 × 0.14`, Z=`0.07`
2. Pivot cylinder: R=`0.045`, H=`0.13`, rot 90° X, Z=`0.07`
3. Side mount cube: `0.06³`, X=`0.05`, Y=`0.08`, Z=`0.10`
4. Fuse → rename `shoulder_link`

---

## Part 9: `upper_arm_link.stl` — Upper arm

1. Main cube: `0.09 × 0.09 × 0.28`, Z=`0.14`
2. Ridge cube: `0.04 × 0.04 × 0.30`, Y=`0.05`, Z=`0.14`
3. Fuse → rename `upper_arm_link`

---

## Part 10: `forearm_link.stl` — Forearm

1. Main cube: `0.075 × 0.075 × 0.22`, Z=`0.11`
2. Sensor pod: `0.06 × 0.04 × 0.05`, Y=`-0.06`, Z=`0.12`
3. Fuse → rename `forearm_link`

---

## Part 11: `wrist_link.stl` — Wrist

1. Cylinder R=`0.035`, H=`0.08`, rot 90° X, Z=`0.04`
2. Cube: `0.06 × 0.08 × 0.06`, Z=`0.03`
3. Fuse → rename `wrist_link`

---

## Part 12: `gripper_base.stl` — Gripper body

1. Cube: `0.08 × 0.05 × 0.04`, Z=`0.02`
2. Neck cube: `0.02 × 0.06 × 0.03`, Z=`0.035`
3. Fuse → rename `gripper_base`

---

## Part 13: `gripper_finger.stl` — Finger

1. Base cube: `0.015 × 0.025 × 0.06`, Z=`0.03`
2. Tip cube: `0.012 × 0.018 × 0.04`, Z=`0.08`
3. Fuse → rename `gripper_finger`

---

## Part 14: `arm_camera.stl` — Arm sensor

1. Cube: `0.05 × 0.03 × 0.03`
2. Lens cylinder: R=`0.008`, H=`0.015`, Z=`0.02`
3. Fuse → rename `arm_camera`

---

## STL export (every part)

1. Hide all other parts
2. Select the part
3. **Mesh → Create mesh from shape**
   - Deviation: `0.0005` (wheels/lidar) or `0.001` (boxes)
   - Angular deviation: `0.15`
4. **File → Export** → STL
5. Save to: `cad_ws/src/cad_description/meshes/<exact_name>.stl`
6. Repeat for all 14 files

**Scale:** With MKS units, chassis = 0.75 m long. No URDF scale needed. If you used mm, add `scale="0.001 0.001 0.001"` in `cad.urdf`.

---

## RViz checkpoint (after base + wheels)

```bash
source /opt/ros/humble/setup.bash
cd "/home/bhuvanesh/ai robot/cad_ws"
colcon build --packages-select cad_description
source install/setup.bash
ros2 launch cad_description cad_launch.py use_gazebo:=false
```

Check: robot visible, correct size, wheels at base corners.

---

## When finished

1. All 14 STLs in `meshes/`
2. Rebuild: `colcon build --packages-select cad_description`
3. Tell the agent: **"execute the plan"** for URDF alignment and Gazebo testing

---

## URDF joint reference (for alignment later)

| Joint | Origin xyz (m) | Axis |
|-------|----------------|------|
| `front_left_wheel_joint` | 0.28, 0.30, 0.14 | Y |
| `front_right_wheel_joint` | 0.28, -0.30, 0.14 | Y |
| `rear_left_wheel_joint` | -0.28, 0.30, 0.14 | Y |
| `rear_right_wheel_joint` | -0.28, -0.30, 0.14 | Y |
| `lidar_joint` | 0.12, 0, 0.36 | — |
| `camera_joint` | 0.38, 0, 0.22 | — |
| `arm_base_joint` | -0.18, 0, 0.33 | — |
| `shoulder_pan_joint` | 0, 0, 0.03 | Z |
| `shoulder_lift_joint` | 0, 0, 0.14 | Y |
| `elbow_joint` | 0, 0, 0.28 | Y |
| `wrist_pitch_joint` | 0, 0, 0.22 | Y |
| `wrist_roll_joint` | 0, 0, 0.04 | Z |
