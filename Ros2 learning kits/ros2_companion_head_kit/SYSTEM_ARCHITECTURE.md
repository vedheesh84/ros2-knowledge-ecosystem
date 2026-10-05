# ros2_companion_head_kit - System Architecture

## Package Overview

| Package | Layer | Purpose |
|---------|-------|---------|
| `companion_head_msgs` | Interface | Message ontology - defines knowledge structures |
| `companion_head_description` | System | Robot embodiment - URDF, TF, hardware interfaces |
| `companion_head_gazebo` | System | Simulation environment |
| `companion_head_bringup` | System | Launch orchestration |
| `companion_head_sensors` | Perception | Face detection, audio processing |
| `companion_head_control` | Control | Gaze tracking, gesture execution |
| `companion_head_expression` | Control | Face rendering/animation |
| `companion_head_behaviors` | Planning/Decision | Mood engine, behavior state machine |
| `companion_head_demos` | Application | Learning exercises, failure injection |

---

## 1. Package-by-Package Analysis

### companion_head_msgs (Interface Layer)

**Purpose:** Defines the ontological structure - what knowledge exists in this system

**Message Types:**

| Message | Knowledge Encoded | Assumptions |
|---------|-------------------|-------------|
| `FaceDetection` | 2D bbox + 3D position + tracking ID | Depth estimation from face width |
| `FaceDetectionArray` | Multiple faces + primary selection | Largest face = attention target |
| `EmotionDetection` | 7-class discrete emotions | Facial expressions map to emotions |
| `ToneAnalysis` | 7-class vocal tones + prosody | Voice maps to sentiment |
| `MoodState` | Valence-Arousal-Engagement + discrete mood | Internal state persists, decays |
| `Expression` | Display command (name, intensity, modifiers) | Expressions interpolate smoothly |

**Ontological Decisions:**
- Emotions are **discrete categories** (not continuous)
- Internal mood uses **3D continuous space** (V-A-E model)
- Face tracking assumes **single primary target**

---

### companion_head_description (System Layer)

**Purpose:** Physical robot definition and hardware abstraction

**TF Tree:**
```
base_link
└── neck_pan_link [revolute: ±90°]
    └── neck_tilt_link [revolute: -30° to +45°]
        └── head_link
            ├── display_link
            ├── camera_link → camera_optical_link
            └── microphone_link
```

**Hardware Interfaces:**
- `neck_pan_joint/position` - command/state
- `neck_tilt_joint/position` - command/state

**Parameters:**

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `use_sim` | false | Use Gazebo simulation |
| `use_fake_hardware` | false | Use mock hardware |

**Controllers (ros2_controllers.yaml):**
- `joint_state_broadcaster` @ 50Hz
- `joint_trajectory_controller` for pan/tilt

---

### companion_head_sensors (Perception Layer)

#### face_detector node

| Aspect | Details |
|--------|---------|
| **Subscribes** | `/camera/image_raw` (Image) |
| **Publishes** | `/faces/detections` (String/JSON), `/faces/image` (Image), `/gaze/target` (PointStamped) |
| **Parameters** | `scale_factor=1.3`, `min_neighbors=5`, `min_size=30`, `focal_length=500`, `known_face_width=0.15` |
| **State** | `face_id_counter`, `tracked_faces` dict |
| **Decides** | Face identity persistence, primary face selection, depth estimation |
| **Assumes** | Camera at known position, faces are ~15cm wide |

#### audio_simulator node

| Aspect | Details |
|--------|---------|
| **Subscribes** | `/audio/simulate` (String) |
| **Publishes** | `/audio/wake_word` (Bool), `/audio/speech` (String), `/audio/tone` (String) |
| **Parameters** | `wake_word="hey companion"`, `auto_events=true`, `event_interval=10.0` |
| **State** | `is_listening` flag |
| **Decides** | Wake word detection, tone classification |
| **Assumes** | Simulated audio is sufficient for learning |

---

### companion_head_control (Control Layer)

#### gaze_controller node

| Aspect | Details |
|--------|---------|
| **Subscribes** | `/gaze/target` (PointStamped), `/joint_states` (JointState) |
| **Publishes** | `/joint_trajectory_controller/joint_trajectory` (JointTrajectory) |
| **Parameters** | `tracking_gain=2.0`, `max_velocity=1.5`, `smoothing_factor=0.3`, `pan_limits`, `tilt_limits` |
| **State** | `current_pan`, `current_tilt`, `target_pan`, `target_tilt` |
| **Decides** | Pan/tilt IK, motion smoothing, velocity limiting |
| **Assumes** | Target in base_link frame, head at z=0.2m |

#### gesture_generator node

| Aspect | Details |
|--------|---------|
| **Subscribes** | `/gesture/command` (String) |
| **Publishes** | `/joint_trajectory_controller/joint_trajectory` (JointTrajectory) |
| **Parameters** | `gesture_speed=1.0` |
| **State** | `state` (IDLE/EXECUTING), `gesture_index`, `start_time` |
| **Decides** | Gesture sequencing, timing, conflict rejection |
| **Assumes** | No concurrent gesture commands |

**Built-in Gestures:** `nod_yes`, `shake_no`, `curious_tilt`, `attentive`, `acknowledge`, `think`, `greet`, `sad`, `surprised`, `idle_sway`

---

### companion_head_expression (Control Layer)

#### expression_renderer node

| Aspect | Details |
|--------|---------|
| **Subscribes** | `/expression/target` (String) |
| **Publishes** | `/face/display` (Image) @ 30Hz |
| **Parameters** | `width=320`, `height=240`, `fps=30`, `blink_interval=3.0`, `transition_speed=5.0` |
| **State** | 8D expression state (eye_openness, mouth_smile, etc.), blink timer |
| **Decides** | Expression interpolation, autonomous blinking |
| **Assumes** | Display device subscribes to image topic |

**Expression State Vector:**
```
[eye_openness, eye_size, pupil_x, pupil_y,
 eyebrow_angle, eyebrow_height, mouth_smile, mouth_open]
```

**Built-in Expressions:** `neutral`, `happy`, `sad`, `curious`, `excited`, `sleepy`, `surprised`, `angry`, `confused`

---

### companion_head_behaviors (Planning/Decision Layer)

#### mood_engine node

| Aspect | Details |
|--------|---------|
| **Subscribes** | `/audio/tone`, `/faces/detections`, `/audio/wake_word` |
| **Publishes** | `/mood/state` (String/JSON), `/expression/target` (String) |
| **Parameters** | `decay_rate=0.98`, `empathy_weight=0.3`, `interaction_boost=0.1`, `neutral_valence=0.1`, `neutral_arousal=0.3` |
| **State** | `valence` [-1,1], `arousal` [0,1], `engagement` [0,1], `last_interaction` |
| **Decides** | Emotional dynamics, mood classification, expression recommendation |
| **Assumes** | Stimuli arrive continuously, emotions decay to neutral |

**Mood Classification Logic:**
```python
if arousal < 0.2: mood = "sleepy"
elif arousal > 0.8 and valence > 0.5: mood = "excited"
elif valence > 0.3: mood = "happy"
elif valence < -0.3: mood = "sad"
elif engagement < 0.3: mood = "confused"
else: mood = "neutral"
```

#### behavior_controller node

| Aspect | Details |
|--------|---------|
| **Subscribes** | `/faces/detections`, `/audio/wake_word`, `/audio/speech`, `/mood/state` |
| **Publishes** | `/behavior/state`, `/expression/target`, `/gesture/command` |
| **Parameters** | `idle_timeout=60.0`, `greeting_duration=2.0`, `response_duration=3.0` |
| **State** | FSM state, `state_start_time`, `last_activity`, `face_detected`, `current_mood` |
| **Decides** | State transitions, coordinated expression+gesture commands |
| **Assumes** | Single interaction partner, time-based transitions |

**Behavior State Machine:**
```
     ┌──────────────────────────────────────────────────────────┐
     │                                                          │
     ▼                                                          │
  ┌──────┐  face    ┌──────────┐  done   ┌──────────┐          │
  │ IDLE │─────────→│ GREETING │────────→│ TRACKING │──────────┤
  └──────┘          └──────────┘         └──────────┘          │
     │                                        │                 │
     │ timeout                                │ wake_word       │
     ▼                                        ▼                 │
  ┌──────────┐                          ┌───────────┐          │
  │ SLEEPING │                          │ LISTENING │          │
  └──────────┘                          └───────────┘          │
     │                                        │                 │
     │ face                                   │ speech          │
     └────────────────────────────────────────┼─────────────────┤
                                              ▼                 │
                                        ┌────────────┐         │
                                        │ RESPONDING │─────────┘
                                        └────────────┘
```

---

## 2. System Architecture Analysis

### Data Flow Diagram

```
                    PERCEPTION                      WORLD MODEL                 DECISION
                    ─────────                       ───────────                 ────────

  /camera/image_raw ──→ [face_detector] ──→ /faces/detections ──┐
                              │                                  │
                              └──→ /gaze/target                  │
                                        │                        │
                                        ▼                        ▼
                              [gaze_controller]          [mood_engine] ──→ /mood/state
                                        │                        │              │
                                        │                        │              │
  /audio/simulate ──→ [audio_simulator] ──→ /audio/tone ─────────┘              │
                              │                                                  │
                              ├──→ /audio/wake_word ─────────────────────────────┤
                              └──→ /audio/speech ────────────────────────────────┤
                                                                                 │
                                                                                 ▼
                                                                    [behavior_controller]
                                                                           │
                    CONTROL                                                │
                    ───────                                                │
                                                                           │
                    [gesture_generator] ◄──── /gesture/command ────────────┤
                              │                                            │
                              ▼                                            │
         /joint_trajectory ◄──────────────────────────────────────────────┤
                              │                                            │
                              │                                            │
                    [expression_renderer] ◄── /expression/target ──────────┘
                              │
                              ▼
                      /face/display
```

### Control Flow vs Data Flow

| Aspect | Pattern |
|--------|---------|
| **Data Flow** | Uni-directional pub/sub, no feedback loops |
| **Control Flow** | Timer-based state machines, no action servers |
| **Coordination** | Implicit via shared topics, no explicit handshakes |
| **Prioritization** | Last-write-wins on shared topics |

### Abstraction Quality

| Boundary | Clean? | Notes |
|----------|--------|-------|
| Perception → Behaviors | Yes | Clear message interfaces |
| Behaviors → Control | Yes | String commands, decoupled |
| Control → Hardware | Yes | ros2_control abstraction |
| Mood ↔ Behavior | Partial | Both publish `/expression/target` |

### Coupling Hotspots

| Coupling | Type | Risk |
|----------|------|------|
| gaze_controller + gesture_generator | Resource contention | Both write `/joint_trajectory` |
| mood_engine + behavior_controller | Output conflict | Both write `/expression/target` |
| face_detector depth estimation | Assumption coupling | Requires known face width |
| behavior_controller speech handling | Hardcoded responses | Not configurable |

---

## 3. Agent-Based Analysis

### What Each Agent Knows

| Agent | Local Knowledge | Global Knowledge |
|-------|-----------------|------------------|
| face_detector | Image processing, face tracking | None |
| audio_simulator | Wake word, phrase library | None |
| gaze_controller | Joint kinematics, limits | None |
| gesture_generator | Gesture library, timing | None |
| expression_renderer | Expression definitions | None |
| mood_engine | Emotional dynamics model | Aggregate perception |
| behavior_controller | FSM transitions, response templates | Aggregate state |

### What Each Agent Assumes

| Agent | Assumptions |
|-------|-------------|
| face_detector | Camera is calibrated, faces are ~15cm wide |
| audio_simulator | Simulated events are sufficient |
| gaze_controller | Target in base_link frame, head at z=0.2m |
| gesture_generator | No concurrent gestures |
| expression_renderer | 30fps rendering is achievable |
| mood_engine | Emotions decay exponentially |
| behavior_controller | Single user, time-based transitions valid |

### Local vs Delegated Decisions

| Agent | Local Decisions | Relies on Others For |
|-------|-----------------|---------------------|
| face_detector | Face identity, primary selection | Camera images |
| audio_simulator | Tone classification | External trigger |
| gaze_controller | Joint angles, smoothing | Target position |
| gesture_generator | Waypoint sequencing | Gesture selection |
| expression_renderer | Frame rendering, blinking | Expression selection |
| mood_engine | Mood classification | Perception inputs |
| behavior_controller | State transitions | Perception + mood |

### How Coordination Emerges

1. **Implicit via Topics:** No explicit coordination protocol
2. **Priority by Convention:** behavior_controller is "master" for expressions
3. **Time-based Synchronization:** No action servers, relies on elapsed time
4. **No Arbitration:** Joint trajectory conflicts are unhandled

### Where Centralization Exists

| Centralized | Decentralized |
|-------------|---------------|
| behavior_controller (orchestration) | face_detector (tracking) |
| mood_engine (emotional state) | gaze_controller (motion) |
| | gesture_generator (execution) |
| | expression_renderer (rendering) |

---

## 4. Architectural Mapping

### Layer Classification

```
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION                               │
│  companion_head_demos (learning exercises, breakers)            │
├─────────────────────────────────────────────────────────────────┤
│                        INTERFACE                                 │
│  companion_head_msgs (message ontology)                         │
├─────────────────────────────────────────────────────────────────┤
│                        DECISION MAKING                          │
│  behavior_controller (FSM, response selection)                  │
├─────────────────────────────────────────────────────────────────┤
│                        PLANNING                                  │
│  gesture_generator (trajectory sequencing)                      │
├─────────────────────────────────────────────────────────────────┤
│                        WORLD MODELING                           │
│  mood_engine (emotional state), face tracking state             │
├─────────────────────────────────────────────────────────────────┤
│                        PERCEPTION                                │
│  face_detector, audio_simulator                                 │
├─────────────────────────────────────────────────────────────────┤
│                        CONTROL                                   │
│  gaze_controller, expression_renderer                           │
├─────────────────────────────────────────────────────────────────┤
│                        SAFETY                                    │
│  Joint limits (in URDF), velocity limits (in gaze_controller)   │
├─────────────────────────────────────────────────────────────────┤
│                        SYSTEM                                    │
│  companion_head_description, gazebo, bringup                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Reusability Analysis

### Reusable Across Robots

| Component | Reusability | Adaptation Needed |
|-----------|-------------|-------------------|
| **companion_head_msgs** | High | None - generic messages |
| **mood_engine** | High | Parameter tuning only |
| **behavior_controller FSM** | High | State/transition customization |
| **face_detector** | High | Camera topic remapping |
| **audio_simulator** | Medium | Replace with real ASR |
| **expression_renderer** | Medium | Display resolution/style |

### Robot-Specific Components

| Component | Why Specific |
|-----------|--------------|
| **URDF/Xacro** | Physical dimensions, joint structure |
| **gaze_controller** | 2-DOF pan/tilt specific IK |
| **gesture_generator** | Joint-specific motion sequences |
| **ros2_controllers.yaml** | Hardware controller config |
| **companion_room.world** | Test environment |

### Integration Complexity

| Hotspot | Issue | Mitigation |
|---------|-------|------------|
| Joint trajectory conflict | gaze + gesture both write same topic | Add arbitration node |
| Expression command conflict | mood_engine + behavior both publish | Single source |
| Depth estimation accuracy | Pinhole model with assumed face width | Use depth camera |

---

## 6. Topic Summary

| Topic | Publisher | Subscriber(s) | Message Type |
|-------|-----------|---------------|--------------|
| `/camera/image_raw` | Gazebo | face_detector | Image |
| `/faces/detections` | face_detector | mood_engine, behavior_controller | String (JSON) |
| `/gaze/target` | face_detector | gaze_controller | PointStamped |
| `/audio/tone` | audio_simulator | mood_engine | String |
| `/audio/wake_word` | audio_simulator | mood_engine, behavior_controller | Bool |
| `/audio/speech` | audio_simulator | behavior_controller | String |
| `/mood/state` | mood_engine | behavior_controller | String (JSON) |
| `/behavior/state` | behavior_controller | (monitoring) | String |
| `/expression/target` | mood_engine, behavior_controller | expression_renderer | String |
| `/gesture/command` | behavior_controller | gesture_generator | String |
| `/face/display` | expression_renderer | (display) | Image |
| `/joint_trajectory_controller/joint_trajectory` | gaze_controller, gesture_generator | ros2_control | JointTrajectory |

---

## 7. Parameter Summary

| Node | Key Parameters |
|------|----------------|
| face_detector | `scale_factor`, `min_neighbors`, `focal_length`, `known_face_width` |
| audio_simulator | `wake_word`, `auto_events`, `event_interval` |
| gaze_controller | `tracking_gain`, `max_velocity`, `smoothing_factor`, `pan_limits`, `tilt_limits` |
| gesture_generator | `gesture_speed` |
| expression_renderer | `width`, `height`, `fps`, `blink_interval`, `transition_speed` |
| mood_engine | `decay_rate`, `empathy_weight`, `interaction_boost`, `neutral_valence`, `neutral_arousal` |
| behavior_controller | `idle_timeout`, `greeting_duration`, `response_duration` |
