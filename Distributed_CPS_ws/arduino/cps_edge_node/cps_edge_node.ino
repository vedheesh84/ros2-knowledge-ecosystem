/* ==============================================================================
 * cps_edge_node.ino
 * Distributed Cyber-Physical Systems (CPS) Edge Sensor Anchor & Gateway Node
 * 
 * Hardware Target: Arduino Uno / Mega / Nano / ESP32
 * Role in CPS Architecture:
 * - Fixed perimeter anchor or edge robotic gateway
 * - Samples physical battery voltage divider (A0)
 * - Measures analog temperature transducer (A1)
 * - Monitors ultrasonic proximity ranger (Trig=9, Echo=10)
 * - Implements hardware failsafe / Emergency Stop interrupt (D2)
 * - Streams structured telemetry packets over serial at 2 Hz
 * - Executes supervisory remote commands (ESTOP, RESUME, PING, SET_RATE)
 * ============================================================================== */

#include <Arduino.h>

// Pin Definitions
const uint8_t PIN_BATTERY_ADC = A0;
const uint8_t PIN_TEMP_ADC    = A1;
const uint8_t PIN_ESTOP_INT   = 2;
const uint8_t PIN_RELAY_SAFE  = 8;
const uint8_t PIN_US_TRIG     = 9;
const uint8_t PIN_US_ECHO     = 10;
const uint8_t PIN_STATUS_LED  = 13;

// Telemetry & State
char ROBOT_ID[32] = "edge_anchor_1";
volatile bool g_estop_active = false;
uint32_t g_telemetry_period_ms = 500; // 2 Hz default
uint32_t g_last_telemetry_tx = 0;
uint32_t g_heartbeat_seq = 0;

// Analog Calibration Constants
const float V_REF = 5.0;           // ADC reference voltage (V)
const float R1_OHMS = 10000.0;     // Voltage divider upper resistor (10k)
const float R2_OHMS = 2200.0;      // Voltage divider lower resistor (2.2k)
const float DIVIDER_RATIO = (R1_OHMS + R2_OHMS) / R2_OHMS; // ~5.545

void onEmergencyStopInterrupt() {
    g_estop_active = true;
    digitalWrite(PIN_RELAY_SAFE, LOW); // De-energize safety relay immediately
}

float readBatteryVoltage() {
    int raw_adc = analogRead(PIN_BATTERY_ADC);
    float v_adc = (raw_adc / 1023.0f) * V_REF;
    return v_adc * DIVIDER_RATIO;
}

float readTemperatureC() {
    int raw_adc = analogRead(PIN_TEMP_ADC);
    float v_adc = (raw_adc / 1023.0f) * V_REF;
    // 10 mV/°C linear response (e.g. TMP36)
    return (v_adc - 0.5f) * 100.0f;
}

float readUltrasonicDistanceM() {
    digitalWrite(PIN_US_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_US_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_US_TRIG, LOW);
    
    unsigned long duration = pulseIn(PIN_US_ECHO, HIGH, 30000); // 30ms timeout (~5m)
    if (duration == 0) return -1.0f; // Out of range
    // Speed of sound: 343 m/s -> (duration_us / 2) * 0.000343
    return (duration * 0.0001715f);
}

uint8_t calculateChecksum(const char* payload) {
    uint8_t csum = 0;
    while (*payload) {
        csum ^= (uint8_t)(*payload++);
    }
    return csum;
}

void parseCommand(const String& cmd) {
    if (cmd.startsWith("$CMD,ESTOP")) {
        g_estop_active = true;
        digitalWrite(PIN_RELAY_SAFE, LOW);
        Serial.println("$ACK,ESTOP_ENGAGED");
    } else if (cmd.startsWith("$CMD,RESUME")) {
        g_estop_active = false;
        digitalWrite(PIN_RELAY_SAFE, HIGH);
        Serial.println("$ACK,NORMAL_OPERATION_RESUMED");
    } else if (cmd.startsWith("$CMD,PING")) {
        Serial.println("$PONG,EDGE_ALIVE");
    } else if (cmd.startsWith("$CMD,RATE,")) {
        int hz = cmd.substring(10).toInt();
        if (hz >= 1 && hz <= 20) {
            g_telemetry_period_ms = 1000 / hz;
            Serial.print("$ACK,RATE_UPDATED_HZ,");
            Serial.println(hz);
        }
    }
}

void setup() {
    Serial.begin(115200);
    
    pinMode(PIN_BATTERY_ADC, INPUT);
    pinMode(PIN_TEMP_ADC, INPUT);
    pinMode(PIN_US_TRIG, OUTPUT);
    pinMode(PIN_US_ECHO, INPUT);
    pinMode(PIN_STATUS_LED, OUTPUT);
    pinMode(PIN_RELAY_SAFE, OUTPUT);
    digitalWrite(PIN_RELAY_SAFE, HIGH); // Normal operation
    
    pinMode(PIN_ESTOP_INT, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_ESTOP_INT), onEmergencyStopInterrupt, FALLING);
    
    Serial.println("$BOOT,CPS_EDGE_NODE_INITIALIZED,FW_V1.0.0");
}

void loop() {
    uint32_t now = millis();
    
    // Process incoming serial commands
    while (Serial.available() > 0) {
        String line = Serial.readStringUntil('\n');
        line.trim();
        if (line.length() > 0) {
            parseCommand(line);
        }
    }
    
    // Periodic telemetry transmit
    if (now - g_last_telemetry_tx >= g_telemetry_period_ms) {
        g_last_telemetry_tx = now;
        g_heartbeat_seq++;
        
        float v_bat = readBatteryVoltage();
        float temp_c = readTemperatureC();
        float dist_m = readUltrasonicDistanceM();
        
        // Calculate battery percentage (12V nominal LiPo: 11.1V=0%, 12.6V=100%)
        float pct = ((v_bat - 11.1f) / (12.6f - 11.1f)) * 100.0f;
        if (pct < 0.0f) pct = 0.0f;
        if (pct > 100.0f) pct = 100.0f;
        
        char payload[128];
        snprintf(payload, sizeof(payload),
            "CPS,id=%s,seq=%lu,v=%.2f,pct=%.1f,temp=%.1f,dist=%.2f,estop=%d",
            ROBOT_ID, (unsigned long)g_heartbeat_seq, v_bat, pct, temp_c, dist_m, g_estop_active ? 1 : 0
        );
        
        uint8_t csum = calculateChecksum(payload);
        
        // Output NMEA-style frame: $<payload>*<hex_checksum>
        Serial.print("$");
        Serial.print(payload);
        Serial.print("*");
        if (csum < 16) Serial.print("0");
        Serial.println(csum, HEX);
        
        // Toggle status LED
        digitalWrite(PIN_STATUS_LED, !digitalRead(PIN_STATUS_LED));
    }
}
