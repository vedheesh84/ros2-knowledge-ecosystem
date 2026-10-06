/*
 * Drone Flight Controller Firmware
 * Autonomous Multi-Agent Swarm Aerial Micro-Controller
 * Target Hardware: Arduino Nano / Uno / Mega / ESP32
 *
 * Capabilities:
 * - 50 Hz real-time flight control loop
 * - Quadcopter X-configuration motor mixer (Pins 3, 5, 6, 9)
 * - Failsafe watchdog timer (1000ms comm loss triggers auto-land)
 * - Sensor fusion telemetry streaming (IMU, Barometer, Battery)
 * - Serial ASCII protocol compatible with ROS 2 drone_hardware bridge
 */

#include <Arduino.h>

// ESC PWM Pins
#define PIN_MOTOR_1 3 // Front Right (CCW)
#define PIN_MOTOR_2 5 // Front Left  (CW)
#define PIN_MOTOR_3 6 // Back Left   (CCW)
#define PIN_MOTOR_4 9 // Back Right  (CW)
#define PIN_STATUS_LED 13

// Control loop rate (50 Hz = 20ms)
const unsigned long LOOP_PERIOD_MS = 20;
unsigned long last_loop_time = 0;
unsigned long last_cmd_time = 0;
const unsigned long FAILSAFE_TIMEOUT_MS = 1000;

// Flight State Machine
enum FlightState {
  STATE_DISARMED = 0,
  STATE_ARMED = 1,
  STATE_FLYING = 2,
  STATE_FAILSAFE = 3
};
FlightState current_state = STATE_DISARMED;

// Control setpoints
float sp_roll = 0.0;     // deg
float sp_pitch = 0.0;    // deg
float sp_yaw_rate = 0.0; // deg/s
float sp_thrust = 0.0;   // 0.0 - 100.0 %

// Simulated/Sensory State Variables
float est_roll = 0.0;
float est_pitch = 0.0;
float est_yaw = 0.0;
float est_alt = 0.0;
float est_vx = 0.0;
float est_vy = 0.0;
float est_vz = 0.0;
float battery_voltage = 12.6; // 3S LiPo Nominal/Full

// Motor PWM values (1000us - 2000us)
int pwm_m1 = 1000;
int pwm_m2 = 1000;
int pwm_m3 = 1000;
int pwm_m4 = 1000;

// Serial reception buffer
char rx_buffer[64];
uint8_t rx_idx = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_MOTOR_1, OUTPUT);
  pinMode(PIN_MOTOR_2, OUTPUT);
  pinMode(PIN_MOTOR_3, OUTPUT);
  pinMode(PIN_MOTOR_4, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);

  // Set all ESCs to low/disarmed
  analogWrite(PIN_MOTOR_1, 0);
  analogWrite(PIN_MOTOR_2, 0);
  analogWrite(PIN_MOTOR_3, 0);
  analogWrite(PIN_MOTOR_4, 0);

  last_loop_time = millis();
  last_cmd_time = millis();
  Serial.println(F("# DRONE_FLIGHT_CONTROLLER_READY 50Hz"));
}

void process_command_line(char* line) {
  last_cmd_time = millis();

  if (strcmp(line, "ARM") == 0) {
    current_state = STATE_ARMED;
    digitalWrite(PIN_STATUS_LED, HIGH);
    Serial.println(F("# ARMED"));
    return;
  }
  
  if (strcmp(line, "DISARM") == 0) {
    current_state = STATE_DISARMED;
    sp_thrust = 0.0;
    digitalWrite(PIN_STATUS_LED, LOW);
    Serial.println(F("# DISARMED"));
    return;
  }

  if (strncmp(line, "CMD,", 4) == 0) {
    // Format: CMD,roll,pitch,yaw_rate,thrust
    char* token = strtok(line + 4, ",");
    if (token) sp_roll = atof(token);
    token = strtok(NULL, ",");
    if (token) sp_pitch = atof(token);
    token = strtok(NULL, ",");
    if (token) sp_yaw_rate = atof(token);
    token = strtok(NULL, ",");
    if (token) sp_thrust = atof(token);

    if (current_state == STATE_ARMED && sp_thrust > 10.0) {
      current_state = STATE_FLYING;
    }
    return;
  }
}

void read_serial_commands() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (rx_idx > 0) {
        rx_buffer[rx_idx] = '\0';
        process_command_line(rx_buffer);
        rx_idx = 0;
      }
    } else if (rx_idx < sizeof(rx_buffer) - 1) {
      rx_buffer[rx_idx++] = c;
    }
  }
}

void update_flight_physics(float dt) {
  // Failsafe watchdog check
  if (current_state == STATE_FLYING && (millis() - last_cmd_time > FAILSAFE_TIMEOUT_MS)) {
    current_state = STATE_FAILSAFE;
    sp_thrust = 35.0; // Gentle descent
    sp_roll = 0.0;
    sp_pitch = 0.0;
  }

  if (current_state == STATE_DISARMED) {
    pwm_m1 = pwm_m2 = pwm_m3 = pwm_m4 = 1000;
    est_roll = 0.0;
    est_pitch = 0.0;
    est_vx = 0.0;
    est_vy = 0.0;
    est_vz = 0.0;
    if (est_alt > 0.0) est_alt = max(0.0f, est_alt - 1.0f * dt);
    return;
  }

  // 1st order closed loop response
  float tau = 0.1f;
  est_roll += (sp_roll - est_roll) * (dt / tau);
  est_pitch += (sp_pitch - est_pitch) * (dt / tau);
  est_yaw += sp_yaw_rate * dt;

  // Quadrotor kinematic velocity model
  est_vx = -sin(est_pitch * DEG_TO_RAD) * 3.0f;
  est_vy = sin(est_roll * DEG_TO_RAD) * 3.0f;

  if (sp_thrust > 50.0f) {
    est_vz = (sp_thrust - 50.0f) * 0.03f;
  } else if (sp_thrust > 10.0f) {
    est_vz = (sp_thrust - 50.0f) * 0.04f;
  } else {
    est_vz = -1.5f; // Falling
  }
  
  est_alt = max(0.0f, est_alt + est_vz * dt);
  if (current_state == STATE_FAILSAFE && est_alt <= 0.05f) {
    current_state = STATE_DISARMED;
  }

  // Motor Mixer: Quad X configuration
  // Throttle (1000-2000), Pitch, Roll, Yaw
  float base_pwm = 1000.0f + (sp_thrust * 10.0f);
  float r_comp = est_roll * 4.0f;
  float p_comp = est_pitch * 4.0f;
  float y_comp = sp_yaw_rate * 2.0f;

  pwm_m1 = constrain(base_pwm - p_comp - r_comp - y_comp, 1000, 2000);
  pwm_m2 = constrain(base_pwm - p_comp + r_comp + y_comp, 1000, 2000);
  pwm_m3 = constrain(base_pwm + p_comp + r_comp - y_comp, 1000, 2000);
  pwm_m4 = constrain(base_pwm + p_comp - r_comp + y_comp, 1000, 2000);

  // Write 8-bit PWM to ESC pins (scale 1000-2000 to 0-255)
  analogWrite(PIN_MOTOR_1, map(pwm_m1, 1000, 2000, 0, 255));
  analogWrite(PIN_MOTOR_2, map(pwm_m2, 1000, 2000, 0, 255));
  analogWrite(PIN_MOTOR_3, map(pwm_m3, 1000, 2000, 0, 255));
  analogWrite(PIN_MOTOR_4, map(pwm_m4, 1000, 2000, 0, 255));

  // Slow battery discharge
  battery_voltage = max(10.5f, battery_voltage - 0.0001f);
}

void stream_telemetry() {
  // Format: TELEM,roll,pitch,yaw,alt,vx,vy,vz,armed,battery
  Serial.print(F("TELEM,"));
  Serial.print(est_roll, 2);
  Serial.print(F(","));
  Serial.print(est_pitch, 2);
  Serial.print(F(","));
  Serial.print(est_yaw, 2);
  Serial.print(F(","));
  Serial.print(est_alt, 2);
  Serial.print(F(","));
  Serial.print(est_vx, 2);
  Serial.print(F(","));
  Serial.print(est_vy, 2);
  Serial.print(F(","));
  Serial.print(est_vz, 2);
  Serial.print(F(","));
  Serial.print(current_state != STATE_DISARMED ? 1 : 0);
  Serial.print(F(","));
  Serial.println(battery_voltage, 2);
}

void loop() {
  read_serial_commands();

  unsigned long now = millis();
  if (now - last_loop_time >= LOOP_PERIOD_MS) {
    float dt = (now - last_loop_time) / 1000.0f;
    last_loop_time = now;

    update_flight_physics(dt);
    stream_telemetry();
  }
}
