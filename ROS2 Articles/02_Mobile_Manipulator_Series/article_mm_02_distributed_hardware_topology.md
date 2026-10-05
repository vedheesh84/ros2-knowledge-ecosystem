## MM 02: DISTRIBUTED HARDWARE TOPOLOGY & MULTI-PROCESSOR ARCHITECTURE

*Purpose: Master the physical and computational hardware architecture of autonomous mobile manipulators. Learn dual-processor topology (High-level SBC + Low-level Real-time MCU), serial/I2C/CAN bus communication, power rail distribution, and electromagnetic interference (EMI) isolation.*

### Must Answer
- Why can a single Raspberry Pi or Jetson SBC not handle hard real-time motor PWM and high-level ROS2 SLAM simultaneously?
- What is the Dual-Processor Architecture (Host Compute SBC + Real-Time Microcontroller MCU)?
- How do we design an isolated communication protocol between the host SBC and low-level MCUs over USB Serial / micro-ROS?
- What causes heavy voltage dips and ground bounce when 4 drive motors and 5 servos start simultaneously?
- How do optocouplers, flyback diodes, and dedicated UBEC regulators protect sensitive computer hardware from inductive spikes?

### Key Insight
A mobile manipulator is an electrical high-noise environment: high-current inductive drive motors generate violent back-EMF spikes that will instantly crash an unshielded SBC unless power rails and signal lines are galvanically isolated.

---

### 1. Dual-Processor Hardware Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DUAL-TIER COMPUTATIONAL TOPOLOGY                      │
│                                                                             │
│   TIER 1: HIGH-LEVEL HOST COMPUTER (SBC / Linux / Non-Realtime)             │
│   • Hardware: Raspberry Pi 4/5, NVIDIA Jetson Orin Nano, x86 Mini-PC        │
│   • Responsibilities: ROS2 Node Graph, Nav2, MoveIt2, OpenCV, YOLO, TF2     │
│   • Timing: 10 Hz - 50 Hz loop rates, OS context-switching jitter           │
│                                                                             │
│                              │                                              │
│                              │ High-Speed USB Serial / micro-ROS (115200+)  │
│                              ▼                                              │
│                                                                             │
│   TIER 2: LOW-LEVEL EMBEDDED CONTROLLERS (MCU / Bare-Metal / Realtime)      │
│   • Hardware: Arduino Mega 2560 / STM32F4 / ESP32 + PCA9685 PWM Driver      │
│   • Responsibilities: Hardware interrupt encoder counting, PID motor PWM,  │
│     servo pulse generation, battery voltage monitoring, E-stop hardware lock│
│   • Timing: Deterministic 1000 Hz (1 ms) hard real-time execution           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Multi-Bus Communication Hierarchy

1. **USB / UART Serial Link ($115200 - 921600\text{ baud}$)**:
   - High-throughput bidirectional telemetry between SBC and Arduino Mega.
   - SBC sends: Target wheel velocity $(\omega_L, \omega_R)$ + Target servo angles $(q_1, \dots, q_5)$.
   - MCU sends: Encoder tick increments $(\Delta N_L, \Delta N_R)$ + Battery voltage + Current feedback.
2. **I2C Bus ($400\text{ kHz}$)**:
   - Communicates from host/MCU to PCA9685 16-channel servo controller and MPU6050/BNO055 IMU.
3. **USB Video / Direct CSI Bus**:
   - High-bandwidth raw camera image streaming at $30\text{ FPS}$ ($1280 \times 720$).

---

### 3. Electrical Power Rail Isolation & Ground Loops

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ISOLATED POWER DISTRIBUTION                        │
│                                                                             │
│   [Main 3S/4S LiPo Battery (11.1V - 14.8V)]                                 │
│          │                                                                  │
│          ├──▶ [L298N / TB6612FNG Motor Drivers] ──▶ (4WD Drive Motors)      │
│          │     (Inductive noise, 0 - 6A current spikes)                     │
│          │                                                                  │
│          ├──▶ [UBEC 1: Step-Down 5V / 8A] ────────▶ [PCA9685 & Servos]      │
│          │     (Isolated Servo Power Rail)                                  │
│          │                                                                  │
│          └──▶ [UBEC 2: Isolated Step-Down 5V / 5A] ─▶ [Host SBC & Sensors]  │
│                (Clean, Filtered Logic Power Rail)   (Raspberry Pi / Jetson) │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Ground Loop Prevention:
When motor current surges through common ground wires, Ohm's law ($V = I \cdot R_{\text{wire}}$) causes the ground potential to jump by $0.2 - 0.5\text{ V}$ (**Ground Bounce**). This corrupts digital logic signals.
**Rule**: Connect all grounds at a single **Star Ground Point** located directly at the battery terminal.

---

### 4. Hands-On Lab & Practical Code References

#### 1. Hardware Interface Driver Source:
- C++ Hardware Plugin: [`ros2_mobile_manipulator_kit/src/mobile_manipulator_hardware/src/arm_hardware_interface.cpp`](file:///e:/Intelligent%20Systems%20Knowledge%20Ecosystem/02%20—%20Domains/ROS2/Ros2%20learning%20kits/ros2_mobile_manipulator_kit/src/mobile_manipulator_hardware/src/arm_hardware_interface.cpp)
- Base Hardware Interface: [`ros2_mobile_manipulator_kit/src/mobile_manipulator_hardware/src/base_hardware_interface.cpp`](file:///e:/Intelligent%20Systems%20Knowledge%20Ecosystem/02%20—%20Domains/ROS2/Ros2%20learning%20kits/ros2_mobile_manipulator_kit/src/mobile_manipulator_hardware/src/base_hardware_interface.cpp)
