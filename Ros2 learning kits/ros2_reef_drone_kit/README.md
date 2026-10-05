# ros2_reef_drone_kit

**Underwater Robotics Learning Kit**

A systems learning platform for autonomous underwater vehicles (AUVs), 6-DOF control, and underwater sensor fusion.
Not a toy. Not a demo. A teaching tool for real understanding.

---

## What This Kit Is

This is the fifth kit in the ROS2 Learning Kit series:

| Kit | Focus | Core Skills |
|-----|-------|-------------|
| **ROS2_kits_ws** | Fundamentals | Lifecycle, topics, services, actions |
| **ros2_turtlebot_kit** | AMR | SLAM, Nav2, EKF, ros2_control |
| **ros2_mobile_manipulator_kit** | Manipulation | Arm control, perception, coordination |
| **ros2_quadruped_kit** | Legged | MPC, gaits, floating-base dynamics |
| **ros2_reef_drone_kit** | Underwater | 6-DOF, thrusters, DVL, buoyancy |

**Prerequisites:** Complete the first kit. Familiarity with control theory helps.

---

## What This Kit Is NOT

- A production AUV stack
- A replacement for UUV Simulator
- A deep-sea ready system
- A complete autonomy solution

---

## Core Philosophy

### AUVs Are Different

Unlike ground robots, AUVs face unique challenges:

| Challenge | Ground Robot | AUV |
|-----------|--------------|-----|
| GPS | Available | Not underwater |
| Locomotion | Wheels/legs | Thrusters |
| Degrees of Freedom | 2-3 (x, y, yaw) | 6 (x, y, z, roll, pitch, yaw) |
| Environment | Air | Water (buoyancy, drag) |
| Sensing | LIDAR, cameras | DVL, sonar, pressure |

### The Control Hierarchy

```
Mission Layer (0.1 Hz)      "Survey the reef"
       │
       ▼
Navigation Layer (1 Hz)     "Path to next waypoint"
       │
       ▼
Guidance Layer (10 Hz)      "Velocity commands"
       │
       ▼
Control Layer (50 Hz)       "PID → Force/torque"
       │
       ▼
Allocation Layer (100 Hz)   "Forces → Thruster commands"
       │
       ▼
Thrusters (motor drivers)
```

---

## Package Architecture

```
ros2_reef_drone_kit/src/
│
├── reef_drone_description/  # URDF with 6 thrusters, sensors
├── reef_drone_gazebo/       # C++ plugins: buoyancy, drag, thrusters
├── reef_drone_sensors/      # DVL, depth, magnetometer simulation
├── reef_drone_control/      # PID controllers, thruster allocation
├── reef_drone_estimation/   # EKF sensor fusion
├── reef_drone_nav/          # 3D waypoint navigation
├── reef_drone_bringup/      # Launch files, ocean world
└── reef_drone_demos/        # 7 demos + failure injection
```

---

## Quick Start

```bash
# Build
cd ros2_reef_drone_kit
colcon build --symlink-install
source install/setup.bash

# Visualize robot (no physics)
ros2 launch reef_drone_description display.launch.py

# Run simulation
ros2 launch reef_drone_bringup simulation.launch.py

# Run full system
ros2 launch reef_drone_bringup full_system.launch.py

# Start with Demo 01
ros2 run reef_drone_demos demo_01_buoyancy
```

---

## Vehicle Design (BlueROV2-Style)

### 6-Thruster Vectored Configuration

```
        TOP VIEW                    FRONT VIEW

    T1 ╲          ╱ T2              T5 ┃    ┃ T6
        ╲        ╱                     ┃    ┃
    ┌────────────────┐              ┌──┴────┴──┐
    │                │              │          │
    │       ●        │              │    ○     │
    │    (center)    │              │          │
    └────────────────┘              └──────────┘
        ╱        ╲
    T3 ╱          ╲ T4

T1-T4: Horizontal vectored (45°) → Surge, Sway, Yaw
T5-T6: Vertical → Heave, Pitch, Roll
```

### Physical Properties

```yaml
mass: 11.5 kg
dimensions: 0.457m × 0.338m × 0.254m
displaced_volume: 0.0114 m³
net_buoyancy: +1.8 N (slightly positive)
max_thrust_per_thruster: 50 N
```

---

## Sensor Suite

| Sensor | Purpose | Topic |
|--------|---------|-------|
| IMU | Orientation, angular velocity | `/imu/data` |
| DVL | Velocity relative to seafloor | `/dvl/velocity` |
| Depth | Pressure-based depth | `/depth` |
| Magnetometer | Heading reference | `/heading` |
| Camera | Visual perception | `/camera/image_raw` |

### DVL Working Principle

```
The Doppler Velocity Log:
1. Emits 4 acoustic beams at seafloor
2. Measures Doppler shift of reflections
3. Computes 3D velocity from beam geometry

     AUV
    / | | \
   /  |  |  \
  ↙  ↙ ↘  ↘
  Beam1  Beam4
      Seafloor

v = c × Δf / (2 × f)  (Doppler equation)
```

---

## Control Architecture

### Thruster Allocation

```
Desired wrench: τ = [Fx, Fy, Fz, Tx, Ty, Tz]
Thruster commands: u = B⁺ × τ

Where B is the 6×6 configuration matrix mapping
thruster forces to body forces/torques.
```

### PID Controllers

```yaml
Depth:    Kp=50, Ki=5, Kd=20  (N/m, N/(m·s), N·s/m)
Heading:  Kp=10, Kd=5         (N·m/rad, N·m·s/rad)
Velocity: Kp=30, Ki=3         (N/(m/s), N/m)
```

---

## State Estimation (EKF)

```
State: [x, y, z, vx, vy, vz, roll, pitch, yaw, ωx, ωy, ωz]

Sensors:
  IMU     → Prediction (high rate, drifts)
  DVL     → Velocity update
  Depth   → Z position update
  Mag     → Yaw update
```

---

## Demo Progression

| Demo | Focus | What You Learn |
|------|-------|----------------|
| 01 | Buoyancy | Archimedes' principle, passive stability |
| 02 | Thruster Control | Individual and combined thruster effects |
| 03 | Depth Hold | PID control, integral term importance |
| 04 | Heading Control | Angle wrapping, yaw stabilization |
| 05 | Station Keeping | 3D position hold, cascaded control |
| 06 | Waypoint Navigation | Line-of-sight guidance |
| 07 | Survey Mission | Complete autonomous mission |

**Do them in order.** Each builds on the previous.

---

## Failure Injection (Breakers)

| Breaker | What It Breaks | What You Learn |
|---------|----------------|----------------|
| `break_thruster` | Disable/reduce one thruster | Fault-tolerant control |
| `break_dvl` | Add noise/dropout to DVL | Dead reckoning limits |
| `break_depth` | Bias depth sensor | Calibration importance |
| `break_imu` | IMU noise/bias | Orientation drift |
| `break_current` | Add ocean current | Disturbance rejection |

```bash
# Example: Disable thruster 1
ros2 run reef_drone_demos break_thruster --ros-args -p thruster:=1 -p mode:=disable
```

---

## TF Tree

```
world
  │
  └── odom (from EKF)
        │
        └── base_link
              ├── imu_link
              ├── dvl_link
              ├── depth_sensor_link
              ├── camera_link
              │     └── camera_optical_link
              ├── thruster_1_link ... thruster_6_link
              └── buoyancy_link
```

---

## Underwater Physics

### Buoyancy

```
F_buoyancy = ρ × g × V

ρ = 1025 kg/m³ (seawater)
g = 9.81 m/s²
V = displaced volume (m³)

For neutral buoyancy: ρ_vehicle = ρ_water
```

### Hydrodynamic Drag

```
F_drag = -D_linear × v - D_quadratic × |v| × v

Linear drag dominates at low speeds
Quadratic drag dominates at high speeds
```

### Depth vs Pressure

```
P = P_atm + ρ × g × h

At depth h (m):
  P ≈ 101325 + 10055 × h  [Pa]
  1 bar ≈ 10m depth
```

---

## Troubleshooting

### "Robot sinks/floats rapidly"
→ Check displaced_volume in buoyancy plugin
→ Verify mass in URDF matches reality

### "Robot won't hold depth"
→ Check PID gains (increase Ki for steady-state)
→ Verify depth sensor publishing

### "Navigation drifts"
→ Check DVL bottom lock (altitude within range)
→ Verify EKF receiving all sensor updates

### "Jerky motion"
→ Increase control rate
→ Check thruster dynamics time constant

---

## Learning Path

```
Week 1: Physics
  - Demo 01: Buoyancy
  - Demo 02: Thruster control
  - Break: break_thruster

Week 2: Control
  - Demo 03: Depth hold
  - Demo 04: Heading control
  - Break: break_depth, break_imu

Week 3: Navigation
  - Demo 05: Station keeping
  - Demo 06: Waypoint navigation
  - Break: break_dvl, break_current

Week 4: Integration
  - Demo 07: Survey mission
  - Custom: Design your own mission
```

---

## Key Equations

### Thruster Force
```
F = F_max × cmd × |cmd|
```

### PID Control
```
u = Kp × e + Ki × ∫e dt + Kd × de/dt
```

### EKF Prediction
```
x(k+1) = f(x(k), u(k)) + w
P(k+1) = F × P(k) × Fᵀ + Q
```

### EKF Update
```
K = P × Hᵀ × (H × P × Hᵀ + R)⁻¹
x = x + K × (z - h(x))
P = (I - K × H) × P
```

---

## References

- Fossen, T.I. "Handbook of Marine Craft Hydrodynamics and Motion Control"
- UUV Simulator (Gazebo plugins reference)
- BlueROV2 documentation
- ROS2 robot_localization package

---

## License

MIT License. Use it. Teach with it. Break it. Fix it.
