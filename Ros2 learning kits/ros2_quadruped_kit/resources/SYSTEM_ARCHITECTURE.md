# ros2_quadruped_kit - System Architecture

## Package Overview

| Package | Layer | Purpose |
|---------|-------|---------|
| `quadruped_description` | System | URDF/Xacro, 12-DOF kinematics |
| `quadruped_hardware` | Hardware | C++ ros2_control for leg motors |
| `quadruped_bringup` | System | Launch orchestration |
| `quadruped_perception` | Perception | Terrain mapping |
| `quadruped_estimation` | Estimation | EKF state estimation, contact detection |
| `quadruped_locomotion` | Planning | Gait scheduling, MPC, swing trajectory |
| `quadruped_control` | Control | Whole-body control, joint PD |
| `quadruped_behaviors` | Decision | Behavior state machine |
| `quadruped_demos` | Application | Progressive demos + breakers |

---

## 1. Package-by-Package Analysis

### quadruped_description (System Layer)

**Purpose:** 12-DOF quadruped robot definition

**Leg Kinematics (per leg):**
```
HAA (Hip Abduction) - X axis rotation
└── HFE (Hip Flexion) - Y axis rotation
    └── KFE (Knee Flexion) - Y axis rotation
        └── Foot (sphere, r=0.02m)
```

**Physical Properties:**
- Body: 0.4m × 0.2m × 0.1m, 8 kg
- Legs: hip_offset=0.08m, upper=0.20m, lower=0.20m
- Total: 12 kg

**Joint Limits:**
| Joint | Range | Max Effort | Max Velocity |
|-------|-------|------------|--------------|
| HAA | ±0.5 rad | 30 Nm | 10 rad/s |
| HFE | -0.5 to 1.57 rad | 30 Nm | 10 rad/s |
| KFE | -0.1 to 2.7 rad | 30 Nm | 10 rad/s |

**Controllers:**
- `joint_state_broadcaster` @ 1000 Hz
- `leg_controller` (JointGroupEffortController)
- `imu_broadcaster`

---

### quadruped_estimation (Estimation Layer)

#### state_estimator node

**State Vector (12 states):**
```
[px, py, pz,           # Position (3)
 vx, vy, vz,           # Velocity (3)
 roll, pitch, yaw,     # Orientation (3)
 wx, wy, wz]           # Angular velocity (3)
```

**Subscriptions:**
| Topic | Type | Rate | Purpose |
|-------|------|------|---------|
| `/imu/data` | Imu | 1000 Hz | Prediction |
| `/joint_states` | JointState | 1000 Hz | Leg kinematics |
| `/contact/{leg}` | Bool | 100 Hz | Update constraints |

**Publications:**
| Topic | Type | Rate |
|-------|------|------|
| `/odom` | Odometry | 200 Hz |
| TF: odom→base_link | Transform | 200 Hz |

**EKF Algorithm:**
1. **Predict (IMU):** Integrate acceleration and gyro
2. **Update (Contact):** Zero velocity constraint when foot in stance

#### contact_estimator node

**Algorithm:**
```python
force = joint_effort[KFE] * 3.0  # Scale factor
contact = force > threshold (10 N)
# Debounce: 3 consecutive readings
```

---

### quadruped_locomotion (Planning Layer)

#### gait_scheduler node

**Gait Patterns:**
| Gait | Period | Duty | Phase Offsets (FL,FR,RL,RR) |
|------|--------|------|----------------------------|
| STAND | 1.0s | 1.0 | [0, 0, 0, 0] |
| WALK | 1.0s | 0.75 | [0, 0.5, 0.25, 0.75] |
| TROT | 0.5s | 0.5 | [0, 0.5, 0.5, 0] |
| BOUND | 0.4s | 0.4 | [0, 0, 0.5, 0.5] |

**Phase-Based Control:**
```python
leg_phase = (master_phase + phase_offset) % 1.0
contact = leg_phase >= (1.0 - duty_factor)
```

**Publications:**
- `/gait/contact_schedule` - [FL, FR, RL, RR] contact state
- `/gait/phase` - [FL, FR, RL, RR] leg phases

#### mpc_controller node

**Purpose:** Generate optimal ground reaction forces

**State (13):** [pos, euler, vel, omega, g]
**Control (12):** [F_FL, F_FR, F_RL, F_RR] × 3

**Cost Weights:**
```yaml
Q: [0,0,100,        # z-height
    100,100,0,      # roll/pitch balance
    10,10,1,        # velocity tracking
    1,1,10,         # angular velocity
    0]              # gravity
R: 0.001            # Force effort
```

**Force Computation:**
1. Weight distribution: `F_z = (m*g) / n_contact`
2. Velocity correction: `F_x, F_y = kp * error`
3. Balance: Roll/pitch correction
4. Friction cone: `|F_x|, |F_y| <= μ * F_z`

#### swing_trajectory node

**Bezier Trajectory:**
```
P(t) = (1-t)³*P₀ + 3(1-t)²t*P₁ + 3(1-t)t²*P₂ + t³*P₃
```

- Peak height: max(start_z, end_z) + 0.08m
- X-Y: Cubic Bezier with control points at 30%, 70%

---

### quadruped_control (Control Layer)

#### whole_body_controller node

**Jacobian Transpose Control:**
```
τ = J^T * F
```

- J: 3×3 Jacobian (foot velocity = J * joint_velocity)
- F: Desired foot force [Fx, Fy, Fz]
- τ: Joint torques [τ_HAA, τ_HFE, τ_KFE]

**Subscriptions:**
- `/mpc/forces` - Desired forces
- `/joint_states` - Current angles

**Publications:**
- `/leg_controller/commands` - 12 joint torques

#### joint_pd_controller node

**Control Law:**
```
τ = τ_ff + Kp*(q_des - q) + Kd*(0 - dq)
```

**Parameters:**
- Kp: 50 (stiffness)
- Kd: 2.0 (damping)

**Default Standing Pose:**
- HAA: 0.0 rad
- HFE: -0.5 rad
- KFE: 1.0 rad

---

### quadruped_behaviors (Decision Layer)

**State Machine:**
```
IDLE → STANDING → WALKING → TROTTING
         ↑           ↓
         ← RECOVERY ←

EMERGENCY (always checked if fallen)
```

**Fall Detection:**
```python
is_fallen = (|roll| > 0.8 rad) or (|pitch| > 0.8 rad)
```

**Velocity Limits by State:**
| State | Max Linear | Max Angular |
|-------|------------|-------------|
| IDLE | 0 | 0 |
| STANDING | 0 | 0 |
| WALKING | 0.3 m/s | 0.2 rad/s |
| TROTTING | 1.0 m/s | 0.5 rad/s |

---

## 2. System Architecture Analysis

### Hierarchical Control Stack

```
BEHAVIOR (50 Hz)
    ↓ State selection, velocity limits
GAIT SCHEDULER (100 Hz)
    ↓ Contact schedule, leg phases
MPC CONTROLLER (33 Hz)
    ↓ Optimal forces
WHOLE-BODY CONTROL
    ↓ Joint torques
JOINT PD (500 Hz)
    ↓ Final torques
ROS2_CONTROL (1000 Hz)
    ↓ Hardware commands
```

### Data Flow

```
/cmd_vel
    ↓
behavior_state_machine
    ├── /gait/select
    └── /cmd_vel_filtered
            ↓
    gait_scheduler
        ├── /gait/contact_schedule
        └── /gait/phase
                ↓
        mpc_controller ←── /odom (from EKF)
            └── /mpc/forces
                    ↓
            whole_body_controller ←── /joint_states
                └── /leg_controller/commands
                        ↓
                joint_pd_controller
                    └── /joint_efforts
                            ↓
                        Hardware
```

### Sensor Fusion

```
IMU (1000 Hz) ──────→ State Estimator (200 Hz) ───→ MPC (33 Hz)
                            ↑
Joint Kinematics ───────────┘
                            ↑
Contact Detection ──────────┘
```

---

## 3. Coordination Patterns

### Multi-Rate Synchronization

| Component | Rate | Dependency |
|-----------|------|------------|
| ROS2_control | 1000 Hz | Hardware |
| Joint PD | 500 Hz | joint_states |
| State Estimator | 200 Hz | IMU |
| Gait Scheduler | 100 Hz | cmd_vel |
| MPC | 33 Hz | odom |
| Behavior | 50 Hz | cmd_vel, IMU |

### Feedback Loops

**Closed Loops (local):**
- Joint PD control (each joint)
- MPC force correction

**Open Loops (feedforward):**
- Gait scheduling (phase-based)
- Swing trajectory (no adjustment)

---

## 4. Agent-Based Analysis

### What Each Component Knows

| Component | Local Knowledge |
|-----------|-----------------|
| state_estimator | EKF math, leg kinematics |
| gait_scheduler | Gait patterns, phases |
| mpc_controller | SRBD dynamics, QP |
| whole_body_ctrl | Jacobian computation |
| joint_pd | PD control law |
| behavior_fsm | State transitions |

### What Each Component Assumes

| Component | Assumptions |
|-----------|-------------|
| state_estimator | IMU bias is zero |
| gait_scheduler | Symmetric leg phases |
| mpc_controller | SRBD approximation valid |
| whole_body_ctrl | Jacobian accurate |
| contact_estimator | KFE effort ∝ force |

---

## 5. Coupling Analysis

### Critical Dependencies

| Coupling | Risk |
|----------|------|
| state_estimator ↔ MPC | Bad state → wrong forces |
| gait_scheduler ↔ swing | Wrong timing → foot collision |
| controller_manager ↔ all | Crash → blind planning |

### Data Flow Assumptions

- **No explicit sync:** All async pub/sub
- **Latency:** ~100ms behavior → hardware
- **Message loss:** No retry logic

---

## 6. Reusability Analysis

### Highly Reusable

| Component | Reason |
|-----------|--------|
| Swing trajectory (Bezier) | Pure math, no ROS |
| Gait scheduler | Phase-based, generic |
| Behavior FSM structure | State pattern |
| Jacobian transpose control | Standard robotics |
| ros2_control integration | Standard ROS2 |

### Robot-Specific

| Component | Reason |
|-----------|--------|
| URDF dimensions | Physical robot |
| Control gains (Kp, Kd) | Tuned for dynamics |
| SRBD inertia | Robot mass/geometry |
| Leg kinematics | DOF configuration |

---

## 7. Topic Summary

| Topic | Publisher | Subscriber | Type |
|-------|-----------|------------|------|
| `/imu/data` | imu_broadcaster | state_est, behavior | Imu |
| `/joint_states` | joint_state_broadcaster | state_est, wbc | JointState |
| `/odom` | state_estimator | mpc_controller | Odometry |
| `/cmd_vel` | user/nav | behavior, gait | Twist |
| `/gait/contact_schedule` | gait_scheduler | mpc, swing | Float64MultiArray |
| `/mpc/forces` | mpc_controller | wbc | Float64MultiArray |
| `/leg_controller/commands` | wbc | joint_pd | Float64MultiArray |
| `/behavior/state` | behavior | monitor | String |

---

## 8. Parameter Summary

| Node | Key Parameters |
|------|----------------|
| state_estimator | Process noise Q, measurement noise R |
| contact_estimator | `force_threshold`, `debounce_count` |
| gait_scheduler | Gait patterns (period, duty, phases) |
| mpc_controller | Cost weights Q, R, horizon, dt |
| whole_body_ctrl | Leg dimensions |
| joint_pd | Kp=50, Kd=2.0, default pose |
| behavior | Velocity limits per state, fall threshold |

---

## 9. Integration Complexity Hotspots

| Hotspot | Issue | Mitigation |
|---------|-------|------------|
| State estimator drift | No IMU bias estimation | Short operation time |
| Gait/MPC sync | Phase sampling | High-rate scheduler |
| Contact detection | Heuristic force | Real F/T sensors |
| Controller timing | Multi-rate | Careful rate selection |

---

## 10. Architectural Insights

**Strengths:**
- Clear layered hierarchy
- Standard ROS2 patterns
- Modular control stack
- Educational documentation

**Limitations:**
- No explicit synchronization
- No health monitoring
- Simplified dynamics (SRBD)
- No learning/adaptation

**Suitable For:**
- Educational quadruped learning
- Research prototyping
- Controlled indoor environments
