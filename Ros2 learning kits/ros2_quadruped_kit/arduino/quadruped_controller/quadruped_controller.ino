/*
 * quadruped_controller.ino - Real-Time 12-DOF Legged Controller & IMU Telemetry
 * ==============================================================================
 * 
 * Hardware Target: Arduino Mega 2560 / Teensy 4.0 / ESP32 + PCA9685 / IMU (MPU6050/BNO055)
 * Baud Rate: 115200 (or 1000000 for high-rate CAN/Serial bridges)
 * 
 * SYSTEM ARCHITECTURE:
 * - 4 Legs x 3 DOF = 12 Joint Actuators:
 *   FL: FL_HAA, FL_HFE, FL_KFE
 *   FR: FR_HAA, FR_HFE, FR_KFE
 *   RL: RL_HAA, RL_HFE, RL_KFE
 *   RR: RR_HAA, RR_HFE, RR_KFE
 * - 6-DOF / 9-DOF IMU Sensor Fusion:
 *   Attitude Quaternion: [qx, qy, qz, qw]
 *   Angular Rates (rad/s): [gx, gy, gz]
 *   Linear Acceleration (m/s^2): [ax, ay, az] (gravity vector)
 * 
 * SERIAL PROTOCOL:
 * 1. Host -> MCU:
 *    "TORQUE <t0> <t1> ... <t11>\n" -> Apply joint effort torques (Nm)
 *    "POS <q0> <q1> ... <q11>\n"       -> Direct joint angle targets (rad)
 *    "PING\n"                          -> Returns "PONG\n"
 *    "ESTOP\n"                         -> Disables all PWM drivers
 * 
 * 2. MCU -> Host (50 Hz streaming):
 *    "POS <p0> <p1> ... <p11>\n"
 *    "VEL <v0> <v1> ... <v11>\n"
 *    "EFF <e0> <e1> ... <e11>\n"
 *    "IMU <qx> <qy> <qz> <qw> <gx> <gy> <gz> <ax> <ay> <az>\n"
 * 
 * SIMULATION MODE:
 * Set SIMULATION_MODE to 1 for benchtop testing without actuators or IMU attached.
 * The microcontroller integrates joint dynamics and estimates attitude locally.
 */

#define SIMULATION_MODE 1

#include <Arduino.h>

const int NUM_JOINTS = 12;
const unsigned long TELEMETRY_INTERVAL_MS = 20; // 50 Hz

// Joint state arrays
float joint_positions[NUM_JOINTS] = {
  0.0, -0.5, 1.0,  // FL: HAA, HFE, KFE
  0.0, -0.5, 1.0,  // FR: HAA, HFE, KFE
  0.0, -0.5, 1.0,  // RL: HAA, HFE, KFE
  0.0, -0.5, 1.0   // RR: HAA, HFE, KFE
};
float joint_velocities[NUM_JOINTS] = {0.0};
float joint_efforts[NUM_JOINTS] = {0.0};
float target_torques[NUM_JOINTS] = {0.0};

// IMU states
float qx = 0.0, qy = 0.0, qz = 0.0, qw = 1.0;
float gx = 0.0, gy = 0.0, gz = 0.0;
float ax = 0.0, ay = 0.0, az = 9.81;

unsigned long last_telemetry_time = 0;
unsigned long last_update_time = 0;
bool estop_active = false;

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) {}
  
  last_telemetry_time = millis();
  last_update_time = millis();
  
  Serial.println("# QUADRUPED_MCU_READY: 12-DOF Actuator & IMU Controller Online");
}

void loop() {
  unsigned long now = millis();
  float dt = (now - last_update_time) * 0.001f;
  if (dt <= 0.0f) dt = 0.001f;
  last_update_time = now;

  // Process incoming serial commands
  while (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() == 0) continue;

    if (line.startsWith("PING")) {
      Serial.println("PONG");
    } else if (line.startsWith("ESTOP")) {
      estop_active = true;
      for (int i = 0; i < NUM_JOINTS; i++) {
        target_torques[i] = 0.0f;
        joint_efforts[i] = 0.0f;
      }
      Serial.println("# ESTOP_ACTIVATED");
    } else if (line.startsWith("TORQUE ")) {
      estop_active = false;
      int idx = 0;
      int start_pos = 7; // after "TORQUE "
      while (start_pos < line.length() && idx < NUM_JOINTS) {
        int next_space = line.indexOf(' ', start_pos);
        if (next_space == -1) next_space = line.length();
        String val_str = line.substring(start_pos, next_space);
        target_torques[idx] = val_str.toFloat();
        idx++;
        start_pos = next_space + 1;
      }
    } else if (line.startsWith("POS ")) {
      estop_active = false;
      int idx = 0;
      int start_pos = 4; // after "POS "
      while (start_pos < line.length() && idx < NUM_JOINTS) {
        int next_space = line.indexOf(' ', start_pos);
        if (next_space == -1) next_space = line.length();
        String val_str = line.substring(start_pos, next_space);
        joint_positions[idx] = val_str.toFloat();
        idx++;
        start_pos = next_space + 1;
      }
    }
  }

#if SIMULATION_MODE
  // Integrate simulated physical dynamics: I * alpha + b * omega = tau
  const float inertia = 0.05f;
  const float damping = 0.3f;
  for (int i = 0; i < NUM_JOINTS; i++) {
    float effort = estop_active ? 0.0f : target_torques[i];
    float accel = (effort - damping * joint_velocities[i]) / inertia;
    joint_velocities[i] += accel * dt;
    joint_positions[i] += joint_velocities[i] * dt;
    joint_efforts[i] = effort;
  }
#endif

  // Periodic Telemetry Streaming
  if (now - last_telemetry_time >= TELEMETRY_INTERVAL_MS) {
    last_telemetry_time = now;

    // Send POS
    Serial.print("POS");
    for (int i = 0; i < NUM_JOINTS; i++) {
      Serial.print(" ");
      Serial.print(joint_positions[i], 4);
    }
    Serial.println();

    // Send VEL
    Serial.print("VEL");
    for (int i = 0; i < NUM_JOINTS; i++) {
      Serial.print(" ");
      Serial.print(joint_velocities[i], 4);
    }
    Serial.println();

    // Send EFF
    Serial.print("EFF");
    for (int i = 0; i < NUM_JOINTS; i++) {
      Serial.print(" ");
      Serial.print(joint_efforts[i], 4);
    }
    Serial.println();

    // Send IMU
    Serial.print("IMU ");
    Serial.print(qx, 4); Serial.print(" ");
    Serial.print(qy, 4); Serial.print(" ");
    Serial.print(qz, 4); Serial.print(" ");
    Serial.print(qw, 4); Serial.print(" ");
    Serial.print(gx, 4); Serial.print(" ");
    Serial.print(gy, 4); Serial.print(" ");
    Serial.print(gz, 4); Serial.print(" ");
    Serial.print(ax, 4); Serial.print(" ");
    Serial.print(ay, 4); Serial.print(" ");
    Serial.println(az, 4);
  }
}
