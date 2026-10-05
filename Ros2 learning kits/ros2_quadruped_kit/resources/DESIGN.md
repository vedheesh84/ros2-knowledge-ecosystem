# ros2_quadruped_kit - Design Document

## Advanced Quadruped Learning Kit

A systems learning platform for legged locomotion, dynamic balance, and Model Predictive Control.

---

## 1. Why This Kit Exists

Previous kits taught:
- **ROS2_kits_ws**: Fundamentals (lifecycle, topics, actions)
- **ros2_turtlebot_kit**: AMR (SLAM, Nav2, EKF, ros2_control)
- **ros2_mobile_manipulator_kit**: Manipulation (arm control, perception, coordination)

This kit teaches what none of those cover:
- **Floating-base dynamics** (robot isn't attached to anything)
- **Contact-switching** (feet make/break contact)
- **Dynamic balance** (not statically stable like a car)
- **Model Predictive Control** (optimization-based control)
- **Real-time constraints** (ms-level control loops)

---

## 2. Platform Specification

### 2.1 Mechanical Design

```
                    BODY (floating base)
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────┴────┐      ┌────┴────┐      ┌────┴────┐
   │  FRONT  │      │  REAR   │      │         │
   │  LEFT   │      │  LEFT   │      │   IMU   │
   │   LEG   │      │   LEG   │      │ CAMERA  │
   └────┬────┘      └────┬────┘      └─────────┘
        │                │
   ┌────┴────┐      ┌────┴────┐
   │  FRONT  │      │  REAR   │
   │  RIGHT  │      │  RIGHT  │
   │   LEG   │      │   LEG   │
   └─────────┘      └─────────┘
```

**Each Leg (×4):**
```
       HAA (Hip Abduction/Adduction)
        │   Rotates leg in/out
        │
       HFE (Hip Flexion/Extension)
        │   Swings leg forward/back
        │
      UPPER LEG
        │
       KFE (Knee Flexion/Extension)
        │   Bends knee
        │
      LOWER LEG
        │
       FOOT (with force sensor)
```

**Joint Naming Convention:**
```
FL_HAA, FL_HFE, FL_KFE   (Front Left)
FR_HAA, FR_HFE, FR_KFE   (Front Right)
RL_HAA, RL_HFE, RL_KFE   (Rear Left)
RR_HAA, RR_HFE, RR_KFE   (Rear Right)
```

### 2.2 Hardware Specifications

| Component | Specification | Purpose |
|-----------|---------------|---------|
| **DOF** | 12 (4 legs × 3 joints) | Locomotion |
| **Actuators** | Brushless DC + planetary gearbox | High torque, backdrivable |
| **Joint Sensors** | Absolute encoders (14-bit) | Position feedback |
| **IMU** | 6-axis (3 accel + 3 gyro) | Body orientation |
| **Foot Sensors** | 3-axis force/torque (per foot) | Contact detection |
| **Camera** | RGB-D (640×480 @ 30fps) | Terrain perception |
| **Compute** | Embedded Linux (Jetson/RPi5) | On-board processing |
| **Weight** | ~12 kg | Realistic dynamics |
| **Battery** | 24V LiPo, 5000mAh | ~30 min operation |

### 2.3 Kinematic Parameters

```yaml
# Typical small quadruped dimensions
body:
  length: 0.40      # m (front-to-back)
  width: 0.20       # m (left-to-right)
  height: 0.10      # m (body thickness)

leg:
  hip_offset: 0.08  # m (hip abduction axis offset)
  upper_leg: 0.20   # m (hip to knee)
  lower_leg: 0.20   # m (knee to foot)

mass:
  body: 8.0         # kg
  upper_leg: 0.5    # kg (each)
  lower_leg: 0.3    # kg (each)
  total: ~12.0      # kg
```

---

## 3. Software Architecture

### 3.1 Package Structure

```
ros2_quadruped_kit/src/
│
├── quadruped_description/        # TRUTH: What the robot IS
│   ├── urdf/                     # URDF/xacro files
│   ├── meshes/                   # Visual/collision meshes
│   └── config/                   # Joint limits, inertias
│
├── quadruped_hardware/           # INTERFACE: Hardware abstraction
│   ├── include/                  # C++ headers
│   │   ├── leg_hardware.hpp      # Single leg interface
│   │   ├── imu_hardware.hpp      # IMU interface
│   │   └── force_sensor.hpp      # Foot force interface
│   └── src/                      # Implementations
│
├── quadruped_bringup/            # ORCHESTRATION: Launch files
│   ├── launch/
│   │   ├── hardware.launch.py
│   │   ├── simulation.launch.py
│   │   └── full_stack.launch.py
│   └── config/
│
├── quadruped_estimation/         # STATE: Where the robot is
│   ├── state_estimator.py        # Floating base estimation
│   ├── contact_estimator.py      # Contact detection
│   └── terrain_estimator.py      # Ground plane estimation
│
├── quadruped_locomotion/         # MOTION: How the robot moves
│   ├── gait_scheduler.py         # Gait pattern generation
│   ├── footstep_planner.py       # Foot placement planning
│   ├── swing_trajectory.py       # Swing leg trajectories
│   └── mpc_controller/           # Model Predictive Control
│       ├── mpc_node.py
│       ├── dynamics_model.py
│       └── qp_solver.py
│
├── quadruped_control/            # EXECUTION: Joint-level control
│   ├── whole_body_controller.py  # Torque computation
│   ├── joint_pd_controller.py    # Low-level PD control
│   └── impedance_controller.py   # Compliant contact
│
├── quadruped_perception/         # SENSING: What the robot sees
│   ├── terrain_mapping.py        # Heightmap from RGB-D
│   └── obstacle_detection.py     # Obstacle avoidance
│
├── quadruped_behaviors/          # DECISIONS: What to do
│   ├── behavior_state_machine.py
│   ├── walk_behavior.py
│   ├── trot_behavior.py
│   └── recovery_behavior.py
│
└── quadruped_demos/              # LEARNING: Progressive demos
    ├── demo_01_joint_control.py
    ├── demo_02_leg_kinematics.py
    ├── demo_03_standing.py
    ├── demo_04_weight_shifting.py
    ├── demo_05_walking.py
    ├── demo_06_trotting.py
    ├── demo_07_disturbance.py
    └── breakers/
```

### 3.2 Control Hierarchy

```
                    ┌─────────────────────────────────┐
                    │     BEHAVIOR LAYER (10 Hz)      │
                    │   "Walk forward at 0.3 m/s"     │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │   LOCOMOTION LAYER (100 Hz)     │
                    │   MPC + Gait Scheduler          │
                    │   "Body trajectory + footsteps" │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │  WHOLE-BODY CONTROL (500 Hz)    │
                    │  "Joint torques from forces"    │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │   JOINT CONTROL (1000 Hz)       │
                    │   PD control + safety limits    │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │        HARDWARE (1000 Hz)       │
                    │   Motor drivers + sensors       │
                    └─────────────────────────────────┘
```

**Why different rates?**
- Behavior: Strategic decisions (slow, high-level)
- Locomotion: Trajectory optimization (medium, compute-heavy)
- Whole-body: Force distribution (fast, reactive)
- Joint: Motor control (fastest, safety-critical)

---

## 4. ros2_control Architecture

### 4.1 Hardware Interfaces

```cpp
// Each leg exposes these interfaces
class LegHardwareInterface : public hardware_interface::SystemInterface
{
    // State Interfaces (readable)
    std::vector<double> joint_positions_;    // 3 joints
    std::vector<double> joint_velocities_;   // 3 joints
    std::vector<double> joint_efforts_;      // 3 joints (torque feedback)
    std::vector<double> foot_forces_;        // 3-axis force at foot
    bool foot_contact_;                      // Binary contact flag

    // Command Interfaces (writable)
    std::vector<double> position_commands_;  // For position mode
    std::vector<double> velocity_commands_;  // For velocity mode
    std::vector<double> effort_commands_;    // For torque mode (MPC uses this)

    // Hybrid mode for impedance control
    std::vector<double> kp_gains_;           // Position gains
    std::vector<double> kd_gains_;           // Velocity gains
};
```

### 4.2 Controller Configuration

```yaml
# ros2_controllers.yaml
controller_manager:
  ros__parameters:
    update_rate: 1000  # Hz - critical for stability

    # Joint state broadcaster for all 12 joints
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster

    # IMU broadcaster
    imu_broadcaster:
      type: imu_sensor_broadcaster/IMUSensorBroadcaster

    # Per-leg effort controllers (for torque mode)
    fl_leg_controller:
      type: effort_controllers/JointGroupEffortController
    fr_leg_controller:
      type: effort_controllers/JointGroupEffortController
    rl_leg_controller:
      type: effort_controllers/JointGroupEffortController
    rr_leg_controller:
      type: effort_controllers/JointGroupEffortController

# Alternative: Trajectory controllers for position mode
fl_leg_trajectory:
  type: joint_trajectory_controller/JointTrajectoryController
  joints: [FL_HAA, FL_HFE, FL_KFE]
  command_interfaces: [position]
  state_interfaces: [position, velocity]
```

### 4.3 Gazebo Integration

```xml
<!-- gazebo.urdf.xacro -->
<gazebo>
  <plugin filename="gz_ros2_control-system" name="gz_ros2_control">
    <parameters>$(find quadruped_description)/config/sim_controllers.yaml</parameters>
    <ros>
      <remapping>/joint_states:=/quadruped/joint_states</remapping>
    </ros>
  </plugin>
</gazebo>

<!-- Contact sensors per foot -->
<gazebo reference="FL_foot_link">
  <sensor name="FL_foot_contact" type="contact">
    <contact>
      <collision>FL_foot_collision</collision>
    </contact>
    <plugin filename="gz_ros2_control" name="contact_sensor">
      <ros>
        <argument>--ros-args -r ~/contact:=/quadruped/FL_contact</argument>
      </ros>
    </plugin>
  </sensor>
</gazebo>
```

---

## 5. State Estimation

### 5.1 The Floating Base Problem

Unlike wheeled robots, quadrupeds have no fixed reference:

```
Wheeled Robot:              Quadruped:
   FIXED                       FLOATING
   odom → base_link            odom → body_link
   (wheel odometry)            (estimated from IMU + contacts)
```

**State vector (18 states):**
```
x = [
    position (3),      # x, y, z in world
    orientation (4),   # quaternion
    linear_vel (3),    # vx, vy, vz
    angular_vel (3),   # wx, wy, wz
    joint_pos (12),    # Not always estimated, from encoders
    joint_vel (12)     # From encoders
]
```

### 5.2 Estimation Pipeline

```
┌─────────────────┐      ┌─────────────────┐
│      IMU        │      │   Joint         │
│  (accel, gyro)  │      │   Encoders      │
└────────┬────────┘      └────────┬────────┘
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────────┐
│           EXTENDED KALMAN FILTER            │
│                                             │
│  Prediction: IMU integration                │
│  Update: Foot contact constraints           │
│                                             │
│  Key insight:                               │
│  When foot is on ground, it's a             │
│  FIXED POINT. This constrains body motion.  │
└─────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   body_pose     │
│   body_twist    │
│   (in odom)     │
└─────────────────┘
```

### 5.3 Contact Estimation

```python
class ContactEstimator:
    """
    Determine which feet are on ground.

    LEARNING: Contact is not binary in reality.
    We threshold force measurements.
    """

    def estimate_contact(self, foot_forces: List[np.ndarray]) -> List[bool]:
        contacts = []
        for force in foot_forces:
            # Normal force threshold (N)
            # Too low = noise, too high = misses light contact
            contact = force[2] > self.contact_threshold  # Z-axis force
            contacts.append(contact)
        return contacts
```

---

## 6. Gait Planning

### 6.1 Gait Patterns

```
WALK (slow, stable, always 3 feet down):
    Time →
    FL: ████░░░░████░░░░████
    FR: ░░████░░░░████░░░░██
    RL: ░░░░████░░░░████░░░░
    RR: ██░░░░████░░░░████░░

    █ = stance (foot on ground)
    ░ = swing (foot in air)

TROT (faster, 2 diagonal feet together):
    Time →
    FL: ████░░░░████░░░░████
    FR: ░░░░████░░░░████░░░░
    RL: ░░░░████░░░░████░░░░
    RR: ████░░░░████░░░░████

    Diagonal pairs: (FL, RR) and (FR, RL)

BOUND (fast, front/rear pairs):
    Time →
    FL: ████░░░░████░░░░████
    FR: ████░░░░████░░░░████
    RL: ░░░░████░░░░████░░░░
    RR: ░░░░████░░░░████░░░░
```

### 6.2 Gait Scheduler

```python
class GaitScheduler:
    """
    Generates contact schedule for each leg.

    LEARNING: Gait is just a phase pattern.
    Phase ∈ [0, 1) wraps around.
    """

    def __init__(self, gait_type: str, cycle_time: float):
        self.gait_type = gait_type
        self.cycle_time = cycle_time

        # Phase offsets per leg
        self.phase_offsets = {
            'walk': [0.0, 0.25, 0.5, 0.75],   # Staggered
            'trot': [0.0, 0.5, 0.5, 0.0],      # Diagonal pairs
            'bound': [0.0, 0.0, 0.5, 0.5],     # Front/rear pairs
        }

        # Stance duration (fraction of cycle)
        self.stance_duration = {
            'walk': 0.75,   # 75% of time on ground (stable)
            'trot': 0.50,   # 50% of time on ground
            'bound': 0.40,  # 40% of time on ground (dynamic)
        }

    def get_contact_state(self, time: float) -> List[bool]:
        """Return which legs should be in stance."""
        phase = (time / self.cycle_time) % 1.0
        contacts = []

        offsets = self.phase_offsets[self.gait_type]
        duty = self.stance_duration[self.gait_type]

        for offset in offsets:
            leg_phase = (phase - offset) % 1.0
            in_stance = leg_phase < duty
            contacts.append(in_stance)

        return contacts
```

### 6.3 Swing Trajectory

```python
class SwingTrajectory:
    """
    Compute foot trajectory during swing phase.

    LEARNING: Swing must:
    - Lift foot above ground (clearance)
    - Move to next foothold
    - Land softly (low velocity at touchdown)
    """

    def compute_trajectory(
        self,
        start_pos: np.ndarray,
        end_pos: np.ndarray,
        swing_height: float,
        phase: float  # 0 = liftoff, 1 = touchdown
    ) -> np.ndarray:
        """
        Bezier curve swing trajectory.
        """
        # Horizontal interpolation
        xy = start_pos[:2] + phase * (end_pos[:2] - start_pos[:2])

        # Vertical: parabola with peak at mid-swing
        z_ground = (start_pos[2] + end_pos[2]) / 2
        z = z_ground + swing_height * 4 * phase * (1 - phase)

        return np.array([xy[0], xy[1], z])
```

---

## 7. Model Predictive Control (MPC)

### 7.1 What MPC Does

```
Current State ────────────────────────────────────────┐
                                                      │
                                                      ▼
                    ┌─────────────────────────────────────────────┐
                    │              MPC SOLVER                     │
                    │                                             │
                    │  Given:                                     │
                    │  - Current body state                       │
                    │  - Desired body trajectory (from behavior)  │
                    │  - Contact schedule (from gait)             │
                    │  - Dynamics model                           │
                    │                                             │
                    │  Optimize:                                  │
                    │  - Ground reaction forces (per foot)        │
                    │                                             │
                    │  Subject to:                                │
                    │  - Dynamics constraints                     │
                    │  - Friction cone (no slip)                  │
                    │  - Force limits                             │
                    │  - Contact constraints (no pull on ground)  │
                    └─────────────────────────────────────────────┘
                                                      │
                                                      ▼
                    Ground Reaction Forces ───────────────────────┐
                                                                  │
                                                                  ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │              WHOLE-BODY CONTROLLER                      │
                    │                                                         │
                    │  Convert forces to joint torques:                       │
                    │  τ = J^T * F                                            │
                    │  (Jacobian transpose maps foot forces to joint torques) │
                    └─────────────────────────────────────────────────────────┘
                                                                  │
                                                                  ▼
                                              Joint Torque Commands
```

### 7.2 Simplified Dynamics Model

```python
class SingleRigidBodyDynamics:
    """
    Simplified model: body as single rigid mass.

    LEARNING: We ignore leg dynamics for MPC planning.
    Legs are "massless" - their job is to apply forces.

    This is valid because:
    - Leg mass << body mass
    - Control rate is fast enough
    """

    def __init__(self, mass: float, inertia: np.ndarray):
        self.m = mass
        self.I = inertia  # 3x3 inertia matrix
        self.g = np.array([0, 0, -9.81])

    def compute_dynamics(
        self,
        state: np.ndarray,           # [pos, quat, vel, omega]
        foot_forces: List[np.ndarray],  # 4 feet × 3D forces
        foot_positions: List[np.ndarray]  # 4 feet × 3D positions
    ) -> np.ndarray:
        """
        Compute state derivative.

        Newton-Euler equations:
        m * a = sum(forces) + m*g
        I * alpha = sum(r × f)  (torques from foot forces)
        """
        # Sum forces
        total_force = sum(foot_forces) + self.m * self.g
        linear_accel = total_force / self.m

        # Sum torques (r × f for each foot)
        body_pos = state[:3]
        total_torque = np.zeros(3)
        for pos, force in zip(foot_positions, foot_forces):
            r = pos - body_pos  # Lever arm
            total_torque += np.cross(r, force)

        angular_accel = np.linalg.solve(self.I, total_torque)

        return np.concatenate([state[7:10], linear_accel, state[10:13], angular_accel])
```

### 7.3 QP Formulation

```python
class MPCController:
    """
    Convex MPC using Quadratic Programming.

    LEARNING: We linearize dynamics and solve a QP.
    This is fast enough for real-time (~100 Hz).
    """

    def __init__(self, horizon: int = 10, dt: float = 0.03):
        self.horizon = horizon  # Prediction steps
        self.dt = dt            # Time step

    def solve(
        self,
        current_state: np.ndarray,
        desired_trajectory: np.ndarray,  # [horizon, state_dim]
        contact_schedule: np.ndarray     # [horizon, 4] boolean
    ) -> np.ndarray:
        """
        Solve for optimal ground reaction forces.

        min  Σ ||x_k - x_des_k||²_Q + Σ ||f_k||²_R
        s.t. x_{k+1} = A*x_k + B*f_k       (dynamics)
             f_z ≥ 0                        (no pulling on ground)
             |f_x|, |f_y| ≤ μ*f_z           (friction cone)
             f = 0 if not in contact        (swing legs)

        Returns: optimal forces [horizon, 4 legs, 3 dims]
        """
        # Build QP matrices
        # H: Hessian (quadratic cost)
        # g: gradient (linear cost)
        # A_eq, b_eq: equality constraints (dynamics)
        # A_ineq, b_ineq: inequality constraints (friction, limits)

        # Solve with OSQP or similar
        solution = self.qp_solver.solve(H, g, A_eq, b_eq, A_ineq, b_ineq)

        return solution.reshape(self.horizon, 4, 3)
```

---

## 8. Safety Systems

### 8.1 Safety Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│  LEVEL 1: HARDWARE LIMITS (always active)                       │
│  - Joint position limits (mechanical stops + software)          │
│  - Joint velocity limits (motor controller)                     │
│  - Current limits (motor driver)                                │
│  - Watchdog timer (if no command, go limp)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│  LEVEL 2: CONTROLLER SAFETY (500 Hz)                            │
│  - Torque limits (before sending to hardware)                   │
│  - Velocity damping (slow down if too fast)                     │
│  - Self-collision avoidance                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│  LEVEL 3: BEHAVIOR SAFETY (100 Hz)                              │
│  - Fall detection (IMU orientation)                             │
│  - Slip detection (foot force anomalies)                        │
│  - Terrain hazard detection                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│  LEVEL 4: EMERGENCY STOP (any level can trigger)                │
│  - E-stop button (hardware)                                     │
│  - Software kill switch                                         │
│  - Fall recovery mode                                           │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Fall Detection

```python
class FallDetector:
    """
    Detect if robot is falling or has fallen.

    LEARNING: Quadrupeds can detect falls early
    and attempt recovery before impact.
    """

    def __init__(self):
        self.orientation_threshold = 0.5  # rad (~30 deg)
        self.angular_velocity_threshold = 3.0  # rad/s

    def detect_fall(
        self,
        orientation: np.ndarray,   # Roll, pitch, yaw
        angular_velocity: np.ndarray,
        contact_states: List[bool]
    ) -> Tuple[bool, str]:
        """
        Returns (is_falling, reason)
        """
        roll, pitch, yaw = orientation

        # Check orientation
        if abs(roll) > self.orientation_threshold:
            return True, "excessive_roll"
        if abs(pitch) > self.orientation_threshold:
            return True, "excessive_pitch"

        # Check angular velocity (spinning out of control)
        if np.linalg.norm(angular_velocity) > self.angular_velocity_threshold:
            return True, "spinning"

        # Check contacts (no feet on ground is bad)
        if not any(contact_states):
            return True, "no_contact"

        return False, "stable"
```

### 8.3 Recovery Behavior

```python
class RecoveryBehavior:
    """
    Attempt to recover from disturbance or fall.

    LEARNING: Recovery is about quickly finding
    a stable configuration, not perfect control.
    """

    def execute(self, fall_type: str, current_state: np.ndarray):
        if fall_type == "excessive_roll":
            # Extend legs on falling side, retract on other
            return self.roll_recovery(current_state)

        elif fall_type == "excessive_pitch":
            # Shift legs to catch fall
            return self.pitch_recovery(current_state)

        elif fall_type == "no_contact":
            # Emergency leg extension to find ground
            return self.find_ground(current_state)

        elif fall_type == "fallen":
            # Full stand-up sequence
            return self.stand_up_sequence()

    def stand_up_sequence(self):
        """
        Pre-planned sequence to stand from lying down.

        1. Tuck all legs
        2. Roll to belly-down
        3. Push up with all four legs
        4. Stabilize
        """
        pass
```

---

## 9. Sensor Integration

### 9.1 Sensor Data Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           HARDWARE LAYER                                  │
├────────────┬────────────┬────────────────┬────────────┬─────────────────┤
│   12×      │    1×      │      4×        │    1×      │      1×         │
│  Encoders  │    IMU     │  Force/Torque  │   RGB-D    │   Battery       │
│  (14-bit)  │  (6-axis)  │   (per foot)   │  (D435)    │   Monitor       │
└─────┬──────┴─────┬──────┴───────┬────────┴─────┬──────┴────────┬────────┘
      │            │              │              │               │
      ▼            ▼              ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ros2_control LAYER                               │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │ joint_state_    │  │ imu_sensor_     │  │ force_torque_   │          │
│  │ broadcaster     │  │ broadcaster     │  │ broadcaster     │          │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘          │
└───────────┼─────────────────────┼─────────────────────┼───────────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
    /joint_states           /imu/data           /foot_forces
    (12 joints)           (orientation +      (4 × 3D forces)
                           angular vel)


┌───────────────────────────────────────────────────────────────────────┐
│                        ESTIMATION LAYER                                │
│                                                                        │
│         ┌───────────────────────────────────────┐                     │
│         │         State Estimator (EKF)         │                     │
│         │                                       │                     │
│         │  Inputs: IMU, foot positions,         │                     │
│         │          contact states               │                     │
│         │  Output: body pose & twist            │                     │
│         └───────────────────────────────────────┘                     │
└───────────────────────────────────────────────────────────────────────┘
```

### 9.2 IMU Processing

```python
class IMUProcessor:
    """
    Process raw IMU data for state estimation.

    LEARNING: Raw IMU has:
    - Bias (drifts over time)
    - Noise (high frequency)
    - Gravity (mixed with linear accel)
    """

    def __init__(self):
        self.gyro_bias = np.zeros(3)
        self.accel_bias = np.zeros(3)
        self.gravity = np.array([0, 0, 9.81])

    def process(self, raw_accel: np.ndarray, raw_gyro: np.ndarray,
                orientation: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns (linear_acceleration, angular_velocity) in world frame.
        """
        # Remove gyro bias
        angular_vel = raw_gyro - self.gyro_bias

        # Remove gravity from accelerometer
        R = self.quaternion_to_rotation_matrix(orientation)
        gravity_body = R.T @ self.gravity
        linear_accel = raw_accel - self.accel_bias - gravity_body

        # Transform to world frame
        linear_accel_world = R @ linear_accel
        angular_vel_world = R @ angular_vel

        return linear_accel_world, angular_vel_world
```

### 9.3 RGB-D Terrain Mapping

```python
class TerrainMapper:
    """
    Build local heightmap from RGB-D camera.

    LEARNING: Quadrupeds need to know:
    - Where is safe to step?
    - What's the ground height?
    - Are there obstacles?
    """

    def __init__(self, resolution: float = 0.02):  # 2cm cells
        self.resolution = resolution
        self.heightmap = {}  # (i, j) -> height

    def update(self, depth_image: np.ndarray, camera_pose: np.ndarray):
        """
        Project depth pixels to 3D and update heightmap.
        """
        # For each pixel in depth image
        for u in range(0, depth_image.shape[1], 4):  # Subsample
            for v in range(0, depth_image.shape[0], 4):
                depth = depth_image[v, u]
                if depth <= 0 or depth > 3.0:  # Invalid or too far
                    continue

                # Back-project to 3D
                point_camera = self.pixel_to_3d(u, v, depth)
                point_world = self.transform_point(point_camera, camera_pose)

                # Update heightmap cell
                i = int(point_world[0] / self.resolution)
                j = int(point_world[1] / self.resolution)

                # Keep maximum height (ground surface, not holes)
                if (i, j) not in self.heightmap:
                    self.heightmap[(i, j)] = point_world[2]
                else:
                    self.heightmap[(i, j)] = max(self.heightmap[(i, j)], point_world[2])
```

---

## 10. Demo Progression

### Learning Sequence

| Demo | Title | Concepts | Prerequisites |
|------|-------|----------|---------------|
| 01 | Joint Control | ros2_control, joint limits | None |
| 02 | Leg Kinematics | FK/IK for single leg | Demo 01 |
| 03 | Standing | Static balance, weight distribution | Demo 02 |
| 04 | Weight Shifting | CoM control, tripod support | Demo 03 |
| 05 | Walking | Gait scheduling, swing trajectories | Demo 04 |
| 06 | Trotting | Dynamic balance, MPC introduction | Demo 05 |
| 07 | Disturbance Recovery | Fall detection, reactive control | Demo 06 |

### Demo 01: Joint Control

```python
"""
LEARNING OBJECTIVES:
- Understand 12-DOF joint structure
- See joint naming convention
- Practice sending joint commands
- Observe joint limits

TRY:
- Command each joint individually
- Command all legs to same configuration
- Hit a joint limit (safely)
"""
```

### Demo 02: Leg Kinematics

```python
"""
LEARNING OBJECTIVES:
- Forward kinematics: joints → foot position
- Inverse kinematics: foot position → joints
- Understand workspace limits
- See Jacobian for velocity mapping

KEY INSIGHT:
IK for a leg is much simpler than for an arm.
Only 3 DOF, and geometry is well-defined.
"""
```

### Demo 03: Standing

```python
"""
LEARNING OBJECTIVES:
- Distribute weight across 4 feet
- Maintain body orientation
- React to small disturbances
- First use of force feedback

KEY INSIGHT:
Standing is about controlling foot forces,
not just foot positions.
"""
```

### Demo 04: Weight Shifting

```python
"""
LEARNING OBJECTIVES:
- Shift center of mass
- Prepare for foot lift
- Maintain balance on 3 legs
- Understand support polygon

KEY INSIGHT:
Before lifting a foot, you must shift
weight off that foot.
"""
```

### Demo 05: Walking

```python
"""
LEARNING OBJECTIVES:
- Gait pattern (walk = always 3 feet down)
- Swing trajectory planning
- Footstep placement
- Slow, stable locomotion

KEY INSIGHT:
Walking is about coordinating:
- When to lift each foot (gait)
- Where to place each foot (planning)
- How to move each foot (trajectory)
"""
```

### Demo 06: Trotting

```python
"""
LEARNING OBJECTIVES:
- Dynamic gait (only 2 feet down at times)
- MPC for body trajectory
- Higher speed locomotion
- Active balance control

KEY INSIGHT:
Trotting is NOT faster walking.
It requires fundamentally different control.
The robot is dynamically stable, not statically.
"""
```

### Demo 07: Disturbance Recovery

```python
"""
LEARNING OBJECTIVES:
- Detect pushes and kicks
- Reactive stepping
- Fall detection and prevention
- Recovery from near-falls

KEY INSIGHT:
Robustness isn't about perfect control.
It's about detecting problems early
and reacting appropriately.
"""
```

---

## 11. Failure Injection (Breakers)

| Breaker | What It Breaks | What You Learn |
|---------|----------------|----------------|
| `break_contact_estimation` | Incorrect contact flags | Estimation coupling |
| `break_imu` | Noisy/biased IMU | State estimation limits |
| `break_foot_slip` | Reduce friction | Friction cone constraints |
| `break_leg_failure` | Disable one leg | Tripod gaits, redundancy |
| `break_latency` | Add control delay | Real-time requirements |
| `break_model_mismatch` | Wrong inertia values | Model accuracy importance |

---

## 12. What NOT to Include

This kit intentionally excludes:

| Excluded | Reason |
|----------|--------|
| Full nonlinear MPC | Too computationally expensive for learning |
| Reinforcement learning gaits | Obscures the underlying physics |
| Complex terrain (stairs, gaps) | Focus on fundamentals first |
| Manipulation (dog with arm) | Separate learning goal |
| Multi-robot coordination | Adds complexity without core insight |

The goal is **understanding**, not **capability**.

---

## 13. Hardware Recommendations

For physical implementation:

### Option A: Commercial Platform
- **Unitree Go1** (~$2700) - Well-supported, SDK available
- **Xiaomi CyberDog** (~$1500) - Consumer-friendly

### Option B: DIY Build
- **Mini Cheetah inspired** - Open-source designs available
- **Stanford Pupper** (~$600) - Low-cost educational platform

### Option C: Simulation Only
- **Gazebo + gz_ros2_control** - This kit fully supports
- **Isaac Sim** - Higher fidelity, NVIDIA GPU required

---

## 14. TF Tree

```
                                 odom
                                  │
                            (state_estimator)
                                  │
                              body_link ◄─── FLOATING BASE
              ┌────────────────────┼────────────────────┐
              │                    │                    │
         imu_link            camera_link          ┌────┴────┐
                                  │               │         │
                            camera_optical    FL_hip    FR_hip ...
                                              │
                                          FL_upper_leg
                                              │
                                          FL_lower_leg
                                              │
                                          FL_foot ◄─── CONTACT POINT
```

---

## 15. Summary

This kit teaches:

1. **Floating-base dynamics** - The robot isn't fixed to anything
2. **Contact-rich control** - Feet make and break contact
3. **Multi-level control** - Behavior → Locomotion → Whole-body → Joint
4. **MPC basics** - Optimization-based trajectory tracking
5. **State estimation** - Knowing where you are with proprioception
6. **Gait patterns** - Coordinating 4 legs for stable locomotion
7. **Safety** - Real-time constraints and fall detection

This is the most complex kit in the series.
It should be attempted only after mastering the previous kits.
