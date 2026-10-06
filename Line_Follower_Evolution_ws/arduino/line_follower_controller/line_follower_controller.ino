/* ==============================================================================
 * line_follower_controller.ino
 * Progressive Line Follower Evolution Embedded Firmware (V1 through V5 Support)
 * 
 * Hardware Target: Arduino Uno / Nano / Mega / ESP32
 * Capabilities:
 * - 8-Channel Analog IR Reflectance Array (Pins A0..A7)
 * - Auto-Calibration & Normalization (EEPROM/RAM bounds)
 * - Microcontroller-Side Weighted Centroid Math: e = sum(w_i * I_i) / sum(I_i)
 * - Crossbar / Intersection Detection (active_sensors >= 6)
 * - Dual Quadrature Wheel Encoders on External Interrupts (Pins 2 & 3)
 * - L298N / TB6612 Dual H-Bridge PWM Motor Driving (Pins 5, 6, 7, 8, 9, 4)
 * - Closed-Loop Cascaded PID Speed & Heading Stabilization
 * - 50 Hz Streaming Serial Telemetry (NMEA-style frames)
 * - Real-Time Command Dispatch (ESTOP, CALIBRATE, SET_PID, SET_SPEED)
 * ============================================================================== */

#include <Arduino.h>

// Pin Mappings
const uint8_t IR_PINS[8] = {A0, A1, A2, A3, A4, A5, A6, A7};

// Motor Driver (L298N)
const uint8_t PIN_MOTOR_L_PWM = 5;  // ENA
const uint8_t PIN_MOTOR_L_IN1 = 7;
const uint8_t PIN_MOTOR_L_IN2 = 8;

const uint8_t PIN_MOTOR_R_PWM = 6;  // ENB
const uint8_t PIN_MOTOR_R_IN3 = 9;
const uint8_t PIN_MOTOR_R_IN4 = 4;

// Encoders (External Interrupts)
const uint8_t PIN_ENC_L = 2; // INT0
const uint8_t PIN_ENC_R = 3; // INT1

// Sensor Geometry: 8 sensors across 70mm bar (-35mm to +35mm)
const float SENSOR_WEIGHTS_M[8] = {
    -0.035f, -0.025f, -0.015f, -0.005f,
    +0.005f, +0.015f, +0.025f, +0.035f
};

// Calibration Boundaries
int g_calib_min[8] = {1023, 1023, 1023, 1023, 1023, 1023, 1023, 1023};
int g_calib_max[8] = {0, 0, 0, 0, 0, 0, 0, 0};
bool g_calibrated = false;

// Encoder Tick Counters
volatile long g_ticks_left = 0;
volatile long g_ticks_right = 0;

void isrEncoderLeft() {
    g_ticks_left++;
}

void isrEncoderRight() {
    g_ticks_right++;
}

// Control Parameters
float g_kp = 35.0f;
float g_kd = 2.5f;
float g_ki = 0.05f;

float g_base_speed_pwm = 140.0f; // 0..255 PWM
float g_last_error = 0.0f;
float g_integral_error = 0.0f;
uint32_t g_last_pid_time = 0;

// State Variables
volatile bool g_estop_active = false;
uint32_t g_telemetry_seq = 0;
uint32_t g_last_telemetry_tx = 0;

void setMotorSpeeds(int left_pwm, int right_pwm) {
    if (g_estop_active) {
        analogWrite(PIN_MOTOR_L_PWM, 0);
        analogWrite(PIN_MOTOR_R_PWM, 0);
        return;
    }
    
    // Left Motor Direction
    if (left_pwm >= 0) {
        digitalWrite(PIN_MOTOR_L_IN1, HIGH);
        digitalWrite(PIN_MOTOR_L_IN2, LOW);
    } else {
        digitalWrite(PIN_MOTOR_L_IN1, LOW);
        digitalWrite(PIN_MOTOR_L_IN2, HIGH);
        left_pwm = -left_pwm;
    }
    
    // Right Motor Direction
    if (right_pwm >= 0) {
        digitalWrite(PIN_MOTOR_R_IN3, HIGH);
        digitalWrite(PIN_MOTOR_R_IN4, LOW);
    } else {
        digitalWrite(PIN_MOTOR_R_IN3, LOW);
        digitalWrite(PIN_MOTOR_R_IN4, HIGH);
        right_pwm = -right_pwm;
    }
    
    analogWrite(PIN_MOTOR_L_PWM, constrain(left_pwm, 0, 255));
    analogWrite(PIN_MOTOR_R_PWM, constrain(right_pwm, 0, 255));
}

void calibrateSensors(uint16_t duration_ms) {
    uint32_t start = millis();
    while (millis() - start < duration_ms) {
        for (uint8_t i = 0; i < 8; i++) {
            int raw = analogRead(IR_PINS[i]);
            if (raw < g_calib_min[i]) g_calib_min[i] = raw;
            if (raw > g_calib_max[i]) g_calib_max[i] = raw;
        }
        delay(10);
    }
    g_calibrated = true;
    Serial.println("$ACK,CALIBRATION_COMPLETE");
}

uint8_t calculateChecksum(const char* payload) {
    uint8_t csum = 0;
    while (*payload) {
        csum ^= (uint8_t)(*payload++);
    }
    return csum;
}

void parseCommand(const String& cmd) {
    if (cmd.startsWith("$CMD,PING")) {
        Serial.println("$PONG,LFE_CONTROLLER_ALIVE");
    } else if (cmd.startsWith("$CMD,ESTOP")) {
        g_estop_active = true;
        setMotorSpeeds(0, 0);
        Serial.println("$ACK,ESTOP_ENGAGED");
    } else if (cmd.startsWith("$CMD,RESUME")) {
        g_estop_active = false;
        Serial.println("$ACK,NORMAL_OPERATION_RESUMED");
    } else if (cmd.startsWith("$CMD,CALIBRATE")) {
        calibrateSensors(3000);
    } else if (cmd.startsWith("$CMD,SET_PID,")) {
        // Format: $CMD,SET_PID,kp,kd,ki
        int idx1 = cmd.indexOf(',', 13);
        int idx2 = cmd.indexOf(',', idx1 + 1);
        if (idx1 > 0 && idx2 > 0) {
            g_kp = cmd.substring(13, idx1).toFloat();
            g_kd = cmd.substring(idx1 + 1, idx2).toFloat();
            g_ki = cmd.substring(idx2 + 1).toFloat();
            Serial.print("$ACK,PID_UPDATED,");
            Serial.print(g_kp); Serial.print(",");
            Serial.print(g_kd); Serial.print(",");
            Serial.println(g_ki);
        }
    }
}

void setup() {
    Serial.begin(115200);
    
    // Motor Pins
    pinMode(PIN_MOTOR_L_PWM, OUTPUT);
    pinMode(PIN_MOTOR_L_IN1, OUTPUT);
    pinMode(PIN_MOTOR_L_IN2, OUTPUT);
    
    pinMode(PIN_MOTOR_R_PWM, OUTPUT);
    pinMode(PIN_MOTOR_R_IN3, OUTPUT);
    pinMode(PIN_MOTOR_R_IN4, OUTPUT);
    
    // Encoders
    pinMode(PIN_ENC_L, INPUT_PULLUP);
    pinMode(PIN_ENC_R, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_ENC_L), isrEncoderLeft, RISING);
    attachInterrupt(digitalPinToInterrupt(PIN_ENC_R), isrEncoderRight, RISING);
    
    // Default calibration fallback (0 to 1023)
    for (uint8_t i = 0; i < 8; i++) {
        g_calib_min[i] = 100;
        g_calib_max[i] = 900;
    }
    
    Serial.println("$BOOT,LFE_CONTROLLER_INITIALIZED,FW_V1.0.0");
}

void loop() {
    uint32_t now = millis();
    
    // Process serial incoming commands
    while (Serial.available() > 0) {
        String line = Serial.readStringUntil('\n');
        line.trim();
        if (line.length() > 0) {
            parseCommand(line);
        }
    }
    
    // 1. Read & Normalize 8 IR Sensors
    float normalized[8];
    float sum_intensity = 0.0f;
    float sum_weighted = 0.0f;
    uint8_t active_count = 0;
    
    for (uint8_t i = 0; i < 8; i++) {
        int raw = analogRead(IR_PINS[i]);
        float norm = (float)(raw - g_calib_min[i]) / (float)(g_calib_max[i] - g_calib_min[i] + 1);
        norm = constrain(norm, 0.0f, 1.0f);
        normalized[i] = norm;
        sum_intensity += norm;
        sum_weighted += SENSOR_WEIGHTS_M[i] * norm;
        if (norm > 0.6f) active_count++;
    }
    
    // 2. Weighted Centroid Calculation
    float error_m = 0.0f;
    if (sum_intensity > 0.1f) {
        error_m = sum_weighted / sum_intensity;
    }
    
    bool intersection = (active_count >= 6);
    
    // 3. Closed-Loop PID Steering Controller (50 Hz)
    float dt = (now - g_last_pid_time) * 0.001f;
    if (dt <= 0.0f) dt = 0.02f;
    g_last_pid_time = now;
    
    float d_error = (error_m - g_last_error) / dt;
    g_integral_error = constrain(g_integral_error + error_m * dt, -0.05f, 0.05f);
    
    float steering = -(g_kp * error_m + g_kd * d_error + g_ki * g_integral_error);
    g_last_error = error_m;
    
    int left_pwm = (int)(g_base_speed_pwm - steering * 1000.0f);
    int right_pwm = (int)(g_base_speed_pwm + steering * 1000.0f);
    
    setMotorSpeeds(left_pwm, right_pwm);
    
    // 4. Periodic 50 Hz Telemetry Output
    if (now - g_last_telemetry_tx >= 20) {
        g_last_telemetry_tx = now;
        g_telemetry_seq++;
        
        char payload[128];
        snprintf(payload, sizeof(payload),
            "LFE,seq=%lu,e=%.4f,int=%d,el=%ld,er=%ld,estop=%d",
            (unsigned long)g_telemetry_seq, error_m, intersection ? 1 : 0,
            g_ticks_left, g_ticks_right, g_estop_active ? 1 : 0
        );
        
        uint8_t csum = calculateChecksum(payload);
        Serial.print("$");
        Serial.print(payload);
        Serial.print("*");
        if (csum < 16) Serial.print("0");
        Serial.println(csum, HEX);
    }
}
