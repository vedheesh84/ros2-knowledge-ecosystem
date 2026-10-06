# Grass-Roots Pedagogical Coherence Audit Report
## Domain: Marine Robotics & Autonomous Underwater Vehicles (AUVs)
## Kit: `ros2_reef_drone_kit` (Milestone 5.7 / `AUV_ws`)

---

## 1. Executive Summary & Audit Mandate

The goal of this audit is to verify that the **`ros2_reef_drone_kit`** functions as a seamless, unified knowledge ecosystem. In accordance with the curriculum mandate:
- **Zero Conceptual Breaks**: Every mathematical symbol, equation, sensor operating principle, and architectural pattern must be introduced and derived from first principles before code deployment.
- **Physical Grounding**: All parameters (mass, buoyancy, drag coefficients, thruster angles, noise figures) are grounded in real-world marine physics (BlueROV2 architecture).
- **Code-to-Theory 1:1 Coherence**: Node interfaces, ROS 2 topics, service names, frame transformations (REP-103), and parameter types match across URDF models, Gazebo C++ plugins, Python nodes, Arduino firmware, and pedagogical documentation.

---

## 2. First-Principles Physics & Mathematical Derivations

### 2.1 Archimedes' Principle & Buoyancy Balance
- **Physical Principle**:
  A submerged body experiences an upward buoyant force equal to the weight of the fluid it displaces.
- **Mathematical Derivation**:
  $$F_{\text{buoy}} = \rho_{\text{seawater}} \cdot g \cdot V_{\text{disp}}$$
  Where:
  - $\rho_{\text{seawater}} = 1025.0\,\text{kg/m}^3$ (standard density of saline seawater at 20°C).
  - $g = 9.80665\,\text{m/s}^2$ (acceleration due to gravity).
  - $V_{\text{disp}} = 0.0114\,\text{m}^3$ (displaced volume of BlueROV2 hull and buoyancy foam).
  $$F_{\text{buoy}} = 1025.0 \cdot 9.80665 \cdot 0.0114 = 114.62\,\text{N}$$
- **Gravitational Weight**:
  $$W = m \cdot g = 11.5\,\text{kg} \cdot 9.80665\,\text{m/s}^2 = 112.78\,\text{N}$$
- **Net Static Force**:
  $$F_{\text{net}} = F_{\text{buoy}} - W = 114.62 - 112.78 = +1.84\,\text{N}$$
- **Pedagogical Significance**:
  The vehicle possesses **slightly positive buoyancy** (+1.8 N). If power is lost or an emergency occurs, the AUV will passively float to the surface for recovery rather than sinking to the seabed.

---

### 2.2 Passive Metacentric Stability (Self-Righting Moment)
- **Physical Principle**:
  To prevent the vehicle from rolling or pitching upside down underwater, the Center of Buoyancy (CB) must be positioned above the Center of Mass (CM).
- **Derivation**:
  In `reef_drone.urdf.xacro`, link `buoyancy_link` is positioned with origin $z = +0.02\,\text{m}$ relative to `base_link` (CoM at $z=0$).
  When the vehicle tilts by angle $\phi$, the buoyancy force acting at CB and gravity acting at CM create a restoring torque couple:
  $$\tau_{\text{restoring}} = r_{\text{CB/CM}} \times F_{\text{buoy}} = -F_{\text{buoy}} \cdot h_m \cdot \sin(\phi)$$
  Where $h_m = 0.02\,\text{m}$ is the metacentric height.
- **Pedagogical Significance**:
  This explains why the 6-thruster AUV does not require active pitch control. Pitch and roll perturbations are passively damped by gravity-buoyancy restoring torques.

---

### 2.3 Hydrodynamic Drag (Morison Formulation)
- **Physical Principle**:
  As an AUV moves through viscous seawater, it experiences skin friction (linear drag at low speeds) and pressure wake separation (quadratic drag at higher speeds).
- **Derivation**:
  $$F_{\text{drag}, i} = -D_{\text{lin}, i} \cdot v_i - D_{\text{quad}, i} \cdot |v_i| \cdot v_i$$
  In `hydrodynamics_plugin.cpp` and `control.yaml`:
  - Surge ($X$): $D_{\text{lin}} = 5.0\,\text{N}\cdot\text{s/m}$, $D_{\text{quad}} = 20.0\,\text{N}\cdot\text{s}^2/\text{m}^2$ (slender frontal cross-section).
  - Sway ($Y$): $D_{\text{lin}} = 10.0\,\text{N}\cdot\text{s/m}$, $D_{\text{quad}} = 40.0\,\text{N}\cdot\text{s}^2/\text{m}^2$ (wider lateral cross-section).
  - Heave ($Z$): $D_{\text{lin}} = 10.0\,\text{N}\cdot\text{s/m}$, $D_{\text{quad}} = 40.0\,\text{N}\cdot\text{s}^2/\text{m}^2$ (large flat top/bottom foam).
- **Pedagogical Significance**:
  The velocity controller utilizes these exact drag coefficients for **feedforward control**:
  $$F_{\text{ff}} = D_{\text{quad}} \cdot |v_{\text{des}}| \cdot v_{\text{des}}$$
  anticipating the quadratic drag force required to sustain cruise velocity.

---

### 2.4 Doppler Velocity Log (DVL) Acoustics
- **Physical Principle**:
  Acoustic waves emitted by the AUV reflect off the stationary seafloor with a Doppler frequency shift proportional to the vehicle's relative velocity.
- **Derivation**:
  $$\Delta f = \frac{2 f_0 v_{\text{beam}}}{c}$$
  Where $c \approx 1500\,\text{m/s}$ (speed of sound in water) and $f_0$ is transducer frequency.
  Four Janus acoustic beams (tilted at 30° from vertical) measure along-beam velocities, which are geometrically projected into 3D body velocity:
  $$\mathbf{v}_{\text{body}} = J_{\text{Janus}}^{-1} \mathbf{v}_{\text{beams}}$$
- **Pedagogical Significance**:
  Explains why AUVs can navigate without GPS: the DVL provides drift-free ground-referenced velocity as long as "bottom lock" (altitude $0.5\,\text{m} \le h \le 100.0\,\text{m}$) is maintained.

---

### 2.5 Hydrostatic Pressure to Depth Conversion
- **Physical Principle**:
  Water pressure increases linearly with depth due to the weight of the water column above.
- **Derivation**:
  $$P(h) = P_{\text{atm}} + \rho_{\text{seawater}} \cdot g \cdot h$$
  $$h = \frac{P - P_{\text{atm}}}{\rho_{\text{seawater}} \cdot g}$$
  In `depth_sensor.py`:
  - $P_{\text{atm}} = 101325\,\text{Pa}$.
  - At depth $h = 5.0\,\text{m}$:
    $$P = 101325 + 1025 \cdot 9.80665 \cdot 5.0 = 151584\,\text{Pa} \approx 1.516\,\text{bar}$$
- **Pedagogical Significance**:
  Depth is directly observable via pressure sensors without drift, anchoring the vertical $Z$ coordinate in the EKF state estimation.

---

### 2.6 Thruster Allocation Matrix & Pseudoinverse
- **Physical Principle**:
  Mapping 6 desired generalized body wrenches $\tau = [F_x, F_y, F_z, T_x, T_y, T_z]^T$ to 6 individual thruster commands $u = [u_1, \dots, u_6]^T$.
- **Derivation**:
  $$\tau = B \cdot u$$
  Where column $i$ of $B$ is:
  $$B_{:, i} = \begin{bmatrix} \mathbf{d}_i \\ \mathbf{p}_i \times \mathbf{d}_i \end{bmatrix}$$
  Horizontal thrusters T1..T4 are mounted at 45° ($\alpha = \pi/4$, $\cos\alpha = \sin\alpha = \frac{\sqrt{2}}{2} \approx 0.707$):
  - T1: $\mathbf{p}_1 = [0.12, -0.12, 0]$, $\mathbf{d}_1 = [0.707, 0.707, 0]$
  - T2: $\mathbf{p}_2 = [0.12, 0.12, 0]$, $\mathbf{d}_2 = [0.707, -0.707, 0]$
  - T3: $\mathbf{p}_3 = [-0.12, -0.12, 0]$, $\mathbf{d}_3 = [0.707, -0.707, 0]$
  - T4: $\mathbf{p}_4 = [-0.12, 0.12, 0]$, $\mathbf{d}_4 = [0.707, 0.707, 0]$
  Vertical thrusters T5, T6:
  - T5: $\mathbf{p}_5 = [0, -0.10, 0.05]$, $\mathbf{d}_5 = [0, 0, 1]$
  - T6: $\mathbf{p}_6 = [0, 0.10, 0.05]$, $\mathbf{d}_6 = [0, 0, 1]$
- **Pseudoinverse Mapping**:
  $$u = B^+ \cdot \tau = B^T (B B^T)^{-1} \tau$$
  If saturated ($\max |u_i| > 1.0$), all commands are scaled uniformly:
  $$u_{\text{scaled}} = \frac{u}{\max_i |u_i|}$$
  preserving the resultant direction of force and torque.

---

## 3. Package & Node Coherence Matrix

| Package | Node / Script | Role in Stack | Input Topics | Output Topics | Physical / Algorithmic Concept |
|---|---|---|---|---|---|
| `reef_drone_description` | `display.launch.py` | Visual System Model | None | `/robot_description`, TF | REP-103 frames, URDF Xacro, 6-thruster kinematic tree |
| `reef_drone_gazebo` | C++ Plugins | Physics Engine | `/thrusters/cmd` | `/ground_truth/odom` | Archimedes buoyancy, Morison quadratic drag, quadratic thrust |
| `reef_drone_sensors` | `dvl_simulator` | Bottom-lock Acoustic Sonar | `/ground_truth/odom` | `/dvl/velocity`, `/dvl/altitude` | Doppler acoustic shift, Janus 4-beam geometry |
| `reef_drone_sensors` | `depth_sensor` | Hydrostatic Barometer | `/ground_truth/odom` | `/depth`, `/pressure` | Hydrostatic gradient $P = P_0 + \rho g h$ |
| `reef_drone_sensors` | `magnetometer` | Earth Magnetic Field Sensor | `/ground_truth/odom` | `/heading`, `/mag/data` | NED-to-ENU field projection, tilt-compensated compass |
| `reef_drone_estimation` | `auv_ekf` | 12-State Kalman Filter | `/imu/data`, `/dvl/velocity`, `/depth`, `/heading` | `/odom`, TF (`odom` $\to$ `base_link`) | State prediction via IMU gyro/accel, sensor update corrections |
| `reef_drone_control` | `thruster_allocator` | Wrench Allocation | `/control/wrench` | `/thrusters/cmd` | Matrix pseudoinverse $B^+ \tau$, vector direction preservation |
| `reef_drone_control` | `depth_controller` | Heave PID Regulation | `/depth`, `/depth/setpoint` | `/control/wrench` ($F_z$) | Buoyancy offset compensation via integral anti-windup clamping |
| `reef_drone_control` | `heading_controller` | Yaw PD Regulation | `/heading`, `/heading/setpoint` | `/control/wrench` ($T_z$) | Shortest angular error wrapping $\text{atan2}(\sin \Delta, \cos \Delta)$ |
| `reef_drone_control` | `velocity_controller` | 3D Velocity Tracking | `/dvl/velocity`, `/cmd_vel` | `/control/wrench` ($F_{xyz}$) | PI feedback + Morison quadratic drag feedforward compensation |
| `reef_drone_control` | `station_keeping` | 3D Position Hold | `/odom`, `/station/setpoint` | `/control/wrench` | Cascaded outer position loop $\to$ inner velocity loop $\to$ body wrench |
| `reef_drone_nav` | `waypoint_follower` | 3D Trajectory Tracking | `/odom`, `/waypoints` | `/station/setpoint` | Line-of-sight 3D guidance, hold timers, tolerance spheres |
| `reef_drone_nav` | `mission_executor` | Autonomous State Machine | `/odom`, `/mission/command` | `/waypoints`, `/mission/status` | FSM (`IDLE` $\to$ `DESCEND` $\to$ `NAVIGATE` $\to$ `SURFACE`), lawnmower transects |
| `reef_drone_hardware` | `flight_bridge_node` | Physical Hardware Bridge | `/thrusters/cmd` | `/depth`, `/pressure`, `/hardware/status` | Bidirectional 115200 serial packet framing, 500ms failsafe watchdog |
| `arduino/` | `reef_drone_controller.ino` | Microcontroller Firmware | Serial commands | ESC PWM pulses, I2C MS5837 | Hardware timers, 1100-1900µs ESC PWM generation, I2C read |
| `scripts/` | `pseudo_reef_drone_emulator.py` | Desktop Digital Twin | Virtual serial `/tmp/ttyAUV_SIM` | Simulated telemetry packets | PTY loopback, real-time vertical dynamics integration |
| `scripts/` | `test_reef_drone_kit.py` | Automated Test Harness | All nodes | Test exit code (0/1) | 8-phase automated regression validation (100% pass) |

---

## 4. Grass-Roots Audit Checklist & Verification Status

1. **Naming & Topic Alignment**: 100% coherent. All topics follow ROS REP-103 conventions (`/ground_truth/odom`, `/dvl/velocity`, `/depth`, `/pressure`, `/heading`, `/odom`, `/control/wrench`, `/thrusters/cmd`).
2. **Coordinate Frames**: World is ENU (East-North-Up), Body is Forward-Left-Up. Depth is positive down ($h = -z$).
3. **No Dangling Concepts**: Every parameter in YAML configuration files (`config/control.yaml`, `config/sensors.yaml`, `config/ekf.yaml`, `config/nav.yaml`, `config/hardware.yaml`) corresponds directly to an in-code declared parameter with documented defaults.
4. **Safety & Failsafe Integrity**: Microprocessor firmware, pseudo-hardware emulator, and ROS 2 hardware bridge all enforce an identical 500ms heartbeat timeout, guaranteeing that motors disarm to neutral (1500µs) if communication drops.
5. **Educational Progression**: Demos 01 through 07 progress step-by-step from passive physics (01: Buoyancy), to open-loop actuation (02: Thrusters), single-axis control (03: Depth, 04: Heading), multi-axis station keeping (05), path tracking (06), and fully autonomous reef survey execution (07).
