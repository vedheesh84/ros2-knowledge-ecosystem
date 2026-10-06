## ARM 15: SERVO HARDWARE, SERIAL BRIDGES & TIMING JITTER

*Purpose: Master embedded hardware integration for robotic manipulators. Learn PWM servo signaling, I2C driver communication with the PCA9685, robust serial framing protocols with microcontrollers, power delivery constraints, and timing jitter.*

### Must Answer
- How do standard hobby and digital PWM servos operate (50 Hz frame, $1.0\text{ ms} - 2.0\text{ ms}$ pulse width)?
- How does the PCA9685 16-channel 12-bit PWM generator offload timing-critical pulses from the host CPU over I2C?
- What is Timing Jitter in serial communications, and how does it degrade joint trajectory smoothness?
- How do we design a robust binary/ASCII serial packet protocol with start/stop bytes and CRC checksums?
- What causes power supply brownouts during multi-joint acceleration, and how do we isolate logic and motor power rails?

### Key Insight
A Linux operating system is not hard real-time; delegating high-frequency PWM generation to dedicated I2C/microcontroller hardware isolates the robot from OS scheduling jitter.

---

### 1. PWM Servo Signal Mechanics

Standard robotic servos require a periodic pulse-width modulation (PWM) control signal:
- **Frequency**: $50\text{ Hz}$ (Period $T = 20.0\text{ ms}$).
- **Pulse Width**:
  - $1.0\text{ ms} \implies -90^\circ$ (Minimum angle)
  - $1.5\text{ ms} \implies 0^\circ$ (Center / Home position)
  - $2.0\text{ ms} \implies +90^\circ$ (Maximum angle)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PWM SERVO TIMING DIAGRAM                          │
│                                                                             │
│    5V ──┐                                                                   │
│         │ 1.5 ms (Center)                                                   │
│    0V ──┴─────────────── 20.0 ms Period (50 Hz) ────────────────────► Time  │
└─────────────────────────────────────────────────────────────────────────────┘
```

If the CPU is delayed by $100 \ \mu\text{s}$ due to OS context switching, the servo misinterprets this as a $9^\circ$ angular command jump, causing violent jitter and motor chatter.

---

### 2. The PCA9685 I2C Hardware Offloader

To eliminate CPU timing jitter, the **PCA9685** provides:
- Dedicated on-chip $25\text{ MHz}$ crystal oscillator.
- 12-bit resolution ($4096$ discrete steps per $20\text{ ms}$ period).
- Resolution: $\frac{20\text{ ms}}{4096} = 4.88 \ \mu\text{s}$ per step (corresponding to $< 0.5^\circ$ angular precision).
- Host SBC simply writes the target 12-bit register value over standard I2C ($400\text{ kHz}$).

---

### 3. Robust Serial Packet Protocol Design

When communicating between a ROS2 PC node and an Arduino / STM32 bridge over USB Serial, raw unformatted strings cause buffer corruption.

#### Production Packet Structure:
```text
[START_BYTE 0xAA] [CMD_TYPE] [JOINT_ID] [VAL_HIGH] [VAL_LOW] [CHECKSUM] [STOP_BYTE 0x55]
```
- **Header Synchronization**: Guarantees recovery if bytes are dropped.
- **XOR / CRC8 Checksum**: Discards corrupted packets caused by motor EMI noise.

---

### 4. Power Rail Isolation & Stall Currents

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ELECTRICAL POWER TOPOLOGY                          │
│                                                                             │
│   [Logic Battery / 5V Reg] ──────▶ [Raspberry Pi / Jetson SBC]              │
│                                                 │                           │
│                                       (Optoisolated I2C / Serial)           │
│                                                 ▼                           │
│   [High-Current Battery (7.4V/12V)] ─▶ [UBEC 5V/10A] ─▶ [Servos / PCA9685] │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### The Brownout Mechanism:
When all 5 servos accelerate simultaneously, peak inrush current can spike to **$6.0 - 8.0\text{ Amps}$**. If the SBC shares the same power rail, the voltage drops below $4.63\text{ V}$, causing an immediate Linux kernel reset (brownout crash).
**Rule**: Always isolate logic and servo power rails.

---

### 5. Hands-On Lab & Practical Code References

#### 1. Source Code & Firmware References:
- **ROS 2 Hardware Bridge:** [`ros2_arm_kit/src/arm_hardware/arm_hardware/servo_bridge.py`](../../Ros2%20learning%20kits/ros2_arm_kit/src/arm_hardware/arm_hardware/servo_bridge.py)
- **Arduino Servo Firmware:** [`ros2_arm_kit/arduino/robotic_arm_controller/robotic_arm_controller.ino`](../../Ros2%20learning%20kits/ros2_arm_kit/arduino/robotic_arm_controller/robotic_arm_controller.ino)
- **Pseudo-Hardware Serial Emulator:** [`ros2_arm_kit/scripts/pseudo_arm_emulator.py`](../../Ros2%20learning%20kits/ros2_arm_kit/scripts/pseudo_arm_emulator.py)
- **Hardware Launch Orchestration:** [`ros2_arm_kit/src/arm_bringup/launch/arm_hardware.launch.py`](../../Ros2%20learning%20kits/ros2_arm_kit/src/arm_bringup/launch/arm_hardware.launch.py)

#### 2. Desktop Hardware-in-the-Loop (HIL) Testing:
Before connecting physical servos, verify the entire communication pipeline using the virtual serial bridge:

```bash
# Terminal 1: Launch Pseudo-Hardware Serial Emulator
python3 "02 — Domains/ROS2/Ros2 learning kits/ros2_arm_kit/scripts/pseudo_arm_emulator.py" --port /tmp/tty_arm_fake

# Terminal 2: Launch Hardware Bridge with Robot Description
ros2 launch arm_bringup arm_hardware.launch.py serial_port:=/tmp/tty_arm_fake

# Terminal 3: Dispatch Trajectory Commands & Verify /joint_states
ros2 run arm_demos demo_01_joint_control
ros2 topic echo /joint_states
```

#### 3. Physical Hardware Deployment:
1. Flash `robotic_arm_controller.ino` to Arduino Uno/Mega or ESP32 using the Arduino IDE.
2. Wire logic grounds (`GND`) together between SBC and microcontroller.
3. Power PCA9685 / servos with external 5V/6V 10A power supply (never directly from USB/Arduino 5V rail).
4. Launch hardware bridge connecting to physical USB port:
```bash
ros2 launch arm_bringup arm_hardware.launch.py serial_port:=/dev/ttyUSB0
```
