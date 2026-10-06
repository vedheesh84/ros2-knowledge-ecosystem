/*
 * =============================================================================
 * ROBOTIC ARM SERVO CONTROLLER FIRMWARE
 * Arduino / ESP32 5/6-DOF Articulated Robotic Arm Hardware Bridge
 * =============================================================================
 *
 * Compatible with ROS 2 `arm_hardware` (servo_bridge.py / PCA9685).
 *
 * COMMUNICATION PROTOCOL:
 * ----------------------
 * Baud Rate: 115200 bps
 * Stream Rate: 50 Hz (20 ms period)
 *
 * Inbound (ROS 2 -> Microcontroller):
 *   ANGLES,<j1_rad>,<j2_rad>,<j3_rad>,<j4_rad>,<gripper_rad>\n
 *   SERVO,<joint_idx>,<angle_deg>\n
 *   HOME\n                             - Return all servos to home (0.0 rad)
 *   TEST,ON\n                          - Enable emulation mode (synthetic feedback without servos)
 *   TEST,OFF\n                         - Disable emulation mode (physical PWM pins / PCA9685)
 *
 * Outbound (Microcontroller -> ROS 2):
 *   POS,<j1_rad>,<j2_rad>,<j3_rad>,<j4_rad>,<gripper_rad>\n
 *   STATUS,<msg>\n
 *
 * PIN DEFINITIONS / HARDWARE SUPPORT:
 * -----------------------------------
 * Mode A: Direct PWM Pins (Arduino Uno / Mega with Servo.h)
 *   - Joint 1 (Base Yaw):      Pin 3
 *   - Joint 2 (Shoulder Pitch):Pin 5
 *   - Joint 3 (Elbow Pitch):   Pin 6
 *   - Joint 4 (Wrist Pitch):   Pin 9
 *   - Joint 5 (Gripper Base):  Pin 10
 *
 * Mode B: PCA9685 16-channel 12-bit PWM generator over I2C (Address 0x40):
 *   - SDA: Pin A4 (Uno) / Pin 20 (Mega) / Pin 21 (ESP32)
 *   - SCL: Pin A5 (Uno) / Pin 21 (Mega) / Pin 22 (ESP32)
 * =============================================================================
 */

#include <Arduino.h>
#include <Servo.h>

// Configuration
#define SERIAL_BAUD 115200
#define NUM_JOINTS 5
#define CONTROL_FREQ_HZ 50
#define CONTROL_PERIOD_MS (1000 / CONTROL_FREQ_HZ)
#define CMD_TIMEOUT_MS 2000

// Servo objects for direct pin actuation
Servo servos[NUM_JOINTS];
const int SERVO_PINS[NUM_JOINTS] = {3, 5, 6, 9, 10};

// Joint angle state (radians)
float target_angles[NUM_JOINTS] = {0.0, 0.0, 0.0, 0.0, 0.0};
float current_angles[NUM_JOINTS] = {0.0, 0.0, 0.0, 0.0, 0.0};

// Emulation mode flag (can be toggled via TEST,ON / TEST,OFF)
bool simulation_mode = false;
unsigned long last_cmd_time = 0;
unsigned long last_control_time = 0;

// Serial RX buffer
char rx_buf[128];
uint8_t rx_ptr = 0;

// Convert radians [-pi/2, pi/2] to servo microseconds [1000us, 2000us]
int rad_to_us(float rad) {
  float deg = rad * (180.0 / 3.1415926535);
  // Center is 1500 us (0 deg). 90 deg is 2000 us, -90 deg is 1000 us.
  float us = 1500.0 + (deg / 90.0) * 500.0;
  return constrain((int)round(us), 900, 2100);
}

// Convert servo microseconds back to radians
float us_to_rad(int us) {
  float deg = ((float)(us - 1500) / 500.0) * 90.0;
  return deg * (3.1415926535 / 180.0);
}

void parse_serial_command(char* cmd) {
  if (strncmp(cmd, "ANGLES,", 7) == 0) {
    char* token = strtok(cmd + 7, ",");
    int idx = 0;
    while (token != NULL && idx < NUM_JOINTS) {
      target_angles[idx] = atof(token);
      token = strtok(NULL, ",");
      idx++;
    }
    last_cmd_time = millis();
  } else if (strncmp(cmd, "SERVO,", 6) == 0) {
    char* token = strtok(cmd + 6, ",");
    if (token != NULL) {
      int j_idx = atoi(token);
      token = strtok(NULL, ",");
      if (token != NULL && j_idx >= 0 && j_idx < NUM_JOINTS) {
        float deg = atof(token);
        target_angles[j_idx] = deg * (3.1415926535 / 180.0);
        last_cmd_time = millis();
      }
    }
  } else if (strcmp(cmd, "HOME") == 0) {
    for (int i = 0; i < NUM_JOINTS; i++) {
      target_angles[i] = 0.0;
    }
    last_cmd_time = millis();
  } else if (strcmp(cmd, "TEST,ON") == 0) {
    simulation_mode = true;
    Serial.println("STATUS,TEST_MODE_ENABLED");
  } else if (strcmp(cmd, "TEST,OFF") == 0) {
    simulation_mode = false;
    Serial.println("STATUS,TEST_MODE_DISABLED");
  }
}

void process_serial_input() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (rx_ptr > 0) {
        rx_buf[rx_ptr] = '\0';
        parse_serial_command(rx_buf);
        rx_ptr = 0;
      }
    } else if (rx_ptr < sizeof(rx_buf) - 1) {
      rx_buf[rx_ptr++] = c;
    }
  }
}

void setup() {
  Serial.begin(SERIAL_BAUD);

  for (int i = 0; i < NUM_JOINTS; i++) {
    servos[i].attach(SERVO_PINS[i]);
    servos[i].writeMicroseconds(1500); // 0 deg center
    current_angles[i] = 0.0;
    target_angles[i] = 0.0;
  }

  last_cmd_time = millis();
  last_control_time = millis();
  Serial.println("STATUS,ROBOTIC_ARM_INITIALIZED");
}

void loop() {
  process_serial_input();

  unsigned long now = millis();
  if (now - last_control_time >= CONTROL_PERIOD_MS) {
    last_control_time = now;

    // Smooth trajectory filter (exponential low-pass / interpolation)
    float alpha = 0.15;
    for (int i = 0; i < NUM_JOINTS; i++) {
      current_angles[i] += alpha * (target_angles[i] - current_angles[i]);

      if (!simulation_mode) {
        int us = rad_to_us(current_angles[i]);
        servos[i].writeMicroseconds(us);
      }
    }

    // Stream 50 Hz joint state feedback to ROS 2: POS,<j1>,<j2>,<j3>,<j4>,<j5>\n
    Serial.print("POS,");
    for (int i = 0; i < NUM_JOINTS; i++) {
      Serial.print(current_angles[i], 3);
      if (i < NUM_JOINTS - 1) Serial.print(",");
    }
    Serial.println();
  }
}
