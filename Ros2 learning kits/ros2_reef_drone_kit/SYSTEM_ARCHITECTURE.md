# ros2_reef_drone_kit - System Architecture

## Package Overview

| Package | Layer | Purpose |
|---------|-------|---------|
| `reef_drone_description` | System | URDF/Xacro, 6-thruster AUV |
| `reef_drone_gazebo` | System | Underwater physics plugins |
| `reef_drone_sensors` | Perception | DVL, depth, magnetometer simulation |
| `reef_drone_estimation` | Estimation | 12-state EKF |
| `reef_drone_control` | Control | PID controllers, thruster allocation |
| `reef_drone_nav` | Planning | Mission execution, waypoint following |
| `reef_drone_bringup` | System | Launch orchestration |
| `reef_drone_demos` | Application | Progressive demos + breakers |

---

## 1. Package-by-Package Analysis

### reef_drone_description (System Layer)

**Purpose:** BlueROV2-style AUV definition

**Physical Properties:**
- Mass: 11.5 kg
- Volume: 0.0114 m³
- Net buoyancy: +1.8 N (slightly positive)
- Dimensions: 0.457m × 0.338m × 0.254m

**Thruster Configuration (6-DOF):**
| Thruster | Position | Direction | DOF |
|----------|----------|-----------|-----|
| T1 (FL) | [0.12, -0.12, 0] | [0.707, 0.707, 0] | Surge/Sway/Yaw |
| T2 (FR) | [0.12, 0.12, 0] | [0.707, -0.707, 0] | Surge/Sway/Yaw |
| T3 (RL) | [-0.12, -0.12, 0] | [0.707, -0.707, 0] | Surge/Sway/Yaw |
| T4 (RR) | [-0.12, 0.12, 0] | [0.707, 0.707, 0] | Surge/Sway/Yaw |
| T5 (VL) | [0, -0.10, 0.05] | [0, 0, 1] | Heave/Pitch/Roll |
| T6 (VR) | [0, 0.10, 0.05] | [0, 0, 1] | Heave/Pitch/Roll |

**Sensors:**
- IMU: Center of mass
- DVL: Bottom-facing at [0, 0, -0.13]
- Depth: Top-mounted at [0, 0, 0.13]
- Camera: Forward at [0.23, 0, 0]

---

### reef_drone_gazebo (System Layer)

**Physics Plugins:**

1. **Buoyancy:**
   - F_buoy = ρ * g * V = 1025 * 9.81 * 0.0114 = 114.6 N
   - Net: +1.8 N upward

2. **Hydrodynamics (Drag):**
   - Linear + Quadratic drag
   - Asymmetric: X=[5,20], Y=[10,40], Z=[10,40]

3. **Thruster:**
   - F = F_max * cmd * |cmd| (quadratic)
   - Max: 50 N, τ = 0.1s

---

### reef_drone_sensors (Perception Layer)

#### dvl_simulator node

| Aspect | Details |
|--------|---------|
| Input | `/ground_truth/odom` |
| Output | `/dvl/velocity` (10 Hz), `/dvl/altitude` |
| Noise | σ_v = 0.01 m/s, σ_h = 0.02 m |
| Constraint | Bottom lock: 0.5m - 100m range |

#### depth_sensor node

| Aspect | Details |
|--------|---------|
| Input | `/ground_truth/odom` (Z position) |
| Output | `/depth` (20 Hz), `/pressure` |
| Physics | P = P_atm + ρ*g*h |
| Noise | σ = 0.005 m |

#### magnetometer node

| Aspect | Details |
|--------|---------|
| Input | `/ground_truth/odom` (orientation) |
| Output | `/heading` (20 Hz), `/mag/data` |
| Field | NED: [20, 0, 40] μT |
| Noise | σ = 0.5 μT |

---

### reef_drone_estimation (Estimation Layer)

#### auv_ekf node

**State Vector (12):**
```
[px, py, pz,           # Position
 vx, vy, vz,           # Velocity
 roll, pitch, yaw,     # Orientation
 wx, wy, wz]           # Angular velocity
```

**Sensor Fusion:**
| Sensor | Rate | Updates |
|--------|------|---------|
| IMU | 100 Hz | Prediction (gyro, accel) |
| DVL | 10 Hz | Velocity |
| Depth | 20 Hz | Z position |
| Heading | 20 Hz | Yaw angle |

**Output:**
- `/odom` @ 50 Hz
- TF: odom → base_link

---

### reef_drone_control (Control Layer)

#### depth_controller node

**PID Control:**
```
force_z = -(Kp*e + Ki*∫e + Kd*de/dt)
```

| Parameter | Value |
|-----------|-------|
| Kp | 50.0 N/m |
| Ki | 5.0 N/(m·s) |
| Kd | 20.0 N·s/m |
| max_force | 100.0 N |

**Note:** Ki compensates +1.8 N buoyancy

#### heading_controller node

**PD Control:**
```
torque_z = Kp*wrap(error) - Kd*yaw_rate
```

| Parameter | Value |
|-----------|-------|
| Kp | 10.0 N·m/rad |
| Kd | 5.0 N·m·s/rad |

#### velocity_controller node

**PI + Feedforward:**
```
force = Kp*e + Ki*∫e + D*|v_des|*v_des
```

| Parameter | Value |
|-----------|-------|
| Kp | 30.0 N/(m/s) |
| Ki | 3.0 N/m |
| drag_x | 20.0 N·s²/m² |
| drag_y/z | 40.0 N·s²/m² |

#### station_keeping node

**Cascaded Control:**
```
Position Loop: v_cmd = Kp_pos * (p_des - p)
Velocity Loop: F = Kp_vel*(v_cmd - v) + Ki_vel*∫e
Heading Loop: τ = Kp_head*e - Kd_head*ω
```

| Parameter | Value |
|-----------|-------|
| Kp_pos | 2.0 1/s |
| max_velocity | 0.5 m/s |
| Kp_vel | 30.0 N/(m/s) |
| Ki_vel | 3.0 N/m |

#### thruster_allocator node

**Allocation:**
```
u = B⁺ * τ  [pseudoinverse]
commands = u / max_thrust
# Scale if saturated
```

**Configuration Matrix B:**
- 6×6 matrix mapping forces/torques to thrusters
- Full rank (no redundancy)

---

### reef_drone_nav (Planning Layer)

#### waypoint_follower node

| Aspect | Details |
|--------|---------|
| Input | `/waypoints` (PoseArray), `/odom` |
| Output | `/station/setpoint` @ 10 Hz |
| Tolerance | position: 0.5m, heading: 0.1 rad |
| Hold time | 2.0 s |

#### mission_executor node

**State Machine:**
```
IDLE → DESCEND → NAVIGATE → SURFACE → IDLE
         ↑                      ↓
         ← ← ← ABORT ← ← ← ← ← ←
```

**Mission Generation:**
- Lawnmower survey pattern
- Configurable: length, width, spacing, depth

---

## 2. System Architecture Analysis

### Control Hierarchy

```
MISSION (1 Hz)
    ↓ Waypoint list
NAVIGATION (10 Hz)
    ↓ Station setpoint
CONTROL (50 Hz)
    ↓ 6D wrench
ALLOCATION
    ↓ 6 thruster commands
PHYSICS (1000 Hz)
```

### Data Flow

```
GAZEBO (Ground Truth)
    ↓
SENSORS (10-100 Hz)
├── dvl_simulator → /dvl/velocity
├── depth_sensor → /depth
└── magnetometer → /heading
    ↓
EKF (50 Hz output)
└── /odom
    ↓
CONTROLLERS (50 Hz)
├── depth_controller
├── heading_controller
├── velocity_controller
└── station_keeping
    ↓
/control/wrench
    ↓
thruster_allocator
    ↓
/thrusters/cmd
    ↓
GAZEBO (Forces)
```

### Sensor Fusion Strategy

```
High-rate: IMU (100 Hz) → Prediction
Medium-rate: DVL (10 Hz), Depth (20 Hz), Heading (20 Hz) → Updates
Asynchronous: Each measurement triggers independent Kalman update
```

---

## 3. Coordination Patterns

### Mode Selection

- Only ONE control mode active at a time
- Modes: depth_controller OR heading_controller OR velocity_controller OR station_keeping
- thruster_allocator always active

### Feedback Loop Frequencies

| Loop | Input Rate | Control Rate |
|------|------------|--------------|
| Depth | 20 Hz | 50 Hz |
| Heading | 20 Hz | 50 Hz |
| Position | 50 Hz | 50 Hz |
| Mission | 1 Hz | 10 Hz |

---

## 4. Agent-Based Analysis

### What Each Component Knows

| Component | Local Knowledge |
|-----------|-----------------|
| DVL Simulator | Doppler physics, bottom lock |
| Depth Sensor | Hydrostatic pressure |
| EKF | Kalman math, state propagation |
| Controllers | PID tuning, dynamics |
| Allocator | Thruster geometry (B matrix) |

### What Each Component Assumes

| Component | Assumptions |
|-----------|-------------|
| DVL | Seafloor at constant depth |
| Depth | Constant water density |
| EKF | Measurements arrive in order |
| Station Keeping | Vehicle near-level |
| Allocator | Thrusters respond immediately |

---

## 5. Coupling Analysis

### Tight Coupling

| Coupling | Risk |
|----------|------|
| Sensors → EKF | Format assumptions |
| EKF → Controllers | 12-state format |
| Controllers → Allocator | 6D wrench format |
| Allocator → B matrix | Hardcoded geometry |

### Loose Coupling

| Component | Why Loose |
|-----------|-----------|
| Control modes | Same output format |
| Waypoint source | Agnostic to publisher |
| Mission patterns | Configurable |

---

## 6. Reusability Analysis

### Highly Reusable

| Component | Reason |
|-----------|--------|
| DVL Simulator | Generic underwater sensor |
| Depth Sensor | Generic pressure measurement |
| EKF structure | Standard Kalman framework |
| PID controllers | Generic single-axis |
| Waypoint follower | Navigation pattern |
| Pseudoinverse allocation | Algorithm is generic |

### Robot-Specific

| Component | Reason |
|-----------|--------|
| Thruster B matrix | Vehicle geometry |
| Drag coefficients | Hull shape |
| Control gains | Vehicle dynamics |
| Buoyancy parameters | Volume/mass |

---

## 7. Topic Summary

| Topic | Publisher | Subscriber | Type |
|-------|-----------|------------|------|
| `/ground_truth/odom` | Gazebo | Sensors | Odometry |
| `/dvl/velocity` | dvl_sim | EKF | TwistWithCovarianceStamped |
| `/depth` | depth_sensor | depth_ctrl, EKF | Float64 |
| `/heading` | magnetometer | heading_ctrl, EKF | Float64 |
| `/imu/data` | Gazebo | EKF | Imu |
| `/odom` | EKF | Controllers, Nav | Odometry |
| `/control/wrench` | Controllers | Allocator | Wrench |
| `/thrusters/cmd` | Allocator | Gazebo | Float64MultiArray |
| `/station/setpoint` | waypoint_follower | station_keeping | PoseStamped |
| `/waypoints` | mission_executor | waypoint_follower | PoseArray |

---

## 8. Parameter Summary

| Node | Key Parameters |
|------|----------------|
| DVL | `update_rate`, `noise_stddev`, `seafloor_depth`, `max_range` |
| Depth | `noise_stddev`, `surface_z`, `water_density` |
| Magnetometer | `noise_stddev`, `declination`, `field_*` |
| EKF | Process noise Q, measurement noise R |
| Depth Controller | `kp=50`, `ki=5`, `kd=20`, `max_force=100` |
| Heading Controller | `kp=10`, `kd=5`, `max_torque=20` |
| Velocity Controller | `kp=30`, `ki=3`, `drag_*` |
| Station Keeping | `kp_pos=2`, `kp_vel=30`, `max_velocity=0.5` |
| Waypoint Follower | `position_tolerance=0.5`, `hold_time=2.0` |

---

## 9. Integration Complexity Hotspots

| Hotspot | Issue | Mitigation |
|---------|-------|------------|
| DVL bottom lock | Out of range = no velocity | Check altitude |
| EKF timestamp sync | No explicit sync | High-rate prediction |
| Control mode switching | Manual selection | Mode manager |
| Thruster saturation | Force clipping | Proportional scaling |
| Mission abort | Manual intervention | ABORT state |

---

## 10. Architectural Insights

**Strengths:**
- Clean layered architecture
- Comprehensive sensor simulation
- Multiple control modes
- Cascaded station keeping
- Progressive demos

**Limitations:**
- No IMU bias estimation
- No time synchronization
- Single control mode only
- Hardcoded B matrix
- No obstacle avoidance

**Suitable For:**
- AUV algorithm learning
- Simulation studies
- Control theory research
- Mission planning development

---

## 11. Hardware Layer & Testing Sandbox Architecture

### Overview
To bridge pure simulation and physical hardware, `ros2_reef_drone_kit` features an integrated Hardware Abstraction Layer and an isolated desktop Testing Sandbox:

```
ros2_reef_drone_kit/
├── arduino/
│   └── reef_drone_controller/
│       └── reef_drone_controller.ino  # Physical Arduino/ESP32 firmware (6 ESC PWM, I2C MS5837)
├── scripts/
│   ├── pseudo_reef_drone_emulator.py  # Desktop PTY virtual serial bridge (100% offline twin)
│   └── test_reef_drone_kit.py         # 8-phase automated regression test harness
├── src/
│   └── reef_drone_hardware/           # ROS 2 hardware bridge node
├── ERROR_DIAGNOSIS_AND_SOLUTIONS.md   # Exhaustive error & solution registry
└── COHERENCE_AUDIT_REPORT.md          # First-principles pedagogical audit
```

### Hardware Communication Protocol
- **Transport**: Serial UART / USB CDC @ 115200 baud (device path `/tmp/ttyAUV_SIM` in sandbox emulation).
- **Thruster Command Packet (ROS 2 -> Microcontroller)**:
  `"<T1,T2,T3,T4,T5,T6>\n"`
  Where $T_i \in [-1.0, 1.0]$. The microcontroller maps normalized floats to ESC pulse widths ($1100\,\mu\text{s}$ full reverse, $1500\,\mu\text{s}$ neutral, $1900\,\mu\text{s}$ full forward).
- **Sensor Telemetry Packet (Microcontroller -> ROS 2)**:
  `"$TELEM,DEPTH:<m>,PRESS:<Pa>,TEMP:<C>,STATUS:<ARMED/FAILSAFE>\n"`
  Streamed at 20 Hz, parsed by `flight_bridge_node` into `/depth`, `/pressure`, and `/hardware/status`.
- **Failsafe Watchdog**:
  A 500ms deadman timer on the microcontroller disarms all thrusters to neutral ($1500\,\mu\text{s}$) if serial heartbeat commands cease.

### Testing Sandbox Harness
The automated test runner (`test_reef_drone_kit.py`) exercises 8 distinct validation layers:
1. `test_01_urdf_and_kinematics`: Verifies URDF Xacro tree, 12 links, 6 thruster joints, and $+0.02\,\text{m}$ metacentric height.
2. `test_02_thrust_allocation_matrix`: Verifies rank-5 configuration matrix $B$ and $B^+$ pseudoinverse mapping.
3. `test_03_sensor_simulation`: Verifies DVL bottom lock, hydrostatic pressure gradient, and magnetometer compass.
4. `test_04_ekf_estimation`: Verifies 12-state Kalman prediction, sensor corrections, and positive-definite covariance.
5. `test_05_controllers`: Verifies depth hold, heading regulation, velocity tracking, and cascaded station keeping.
6. `test_06_navigation_and_mission`: Verifies lawnmower transect pattern generation and state machine transitions.
7. `test_07_demos_and_breakers`: Verifies progressive educational demos and fault injection breakers.
8. `test_08_hardware_bridge_and_emulator`: Verifies bidirectional PTY serial exchange and failsafe watchdog disarming.

