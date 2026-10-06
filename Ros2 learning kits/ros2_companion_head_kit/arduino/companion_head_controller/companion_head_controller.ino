/*
 * ==============================================================================
 * Companion Head 2-DOF Pan/Tilt Microcontroller Firmware
 * ==============================================================================
 * Target: Arduino Uno / Nano / Mega / ESP32 / RP2040
 * Baud Rate: 115200 bps
 *
 * Capabilities:
 * - Controls 2 PWM Servos (neck_pan_joint on Pin 9, neck_tilt_joint on Pin 10)
 * - Streams joint positions back to ros2_control at 50 Hz:
 *   "SERVO_POS <pan_deg> <tilt_deg>\n"
 * - Decodes motion commands:
 *   "SERVO <pan_deg> <tilt_deg>\n"
 * - Standalone simulation mode for benchtop testing without physical servos:
 *   Uncomment '#define SIMULATION_MODE'
 * ==============================================================================
 */

#include <Arduino.h>

#ifndef SIMULATION_MODE
#include <Servo.h>
#endif

// --- Configuration ---
#define BAUD_RATE 115200
#define FEEDBACK_RATE_HZ 50
#define FEEDBACK_INTERVAL_MS (1000 / FEEDBACK_RATE_HZ)

// Pin Definitions
#define PIN_SERVO_PAN 9
#define PIN_SERVO_TILT 10
#define PIN_STATUS_LED 13

// Servo Constraints
#define PAN_MIN_DEG 0
#define PAN_MAX_DEG 180
#define PAN_NOMINAL_DEG 90

#define TILT_MIN_DEG 45
#define TILT_MAX_DEG 135
#define TILT_NOMINAL_DEG 90

#ifndef SIMULATION_MODE
Servo panServo;
Servo tiltServo;
#endif

// State Variables
int currentPanDeg = PAN_NOMINAL_DEG;
int currentTiltDeg = TILT_NOMINAL_DEG;
int targetPanDeg = PAN_NOMINAL_DEG;
int targetTiltDeg = TILT_NOMINAL_DEG;

unsigned long lastFeedbackTime = 0;
String inputBuffer = "";

void setup() {
  Serial.begin(BAUD_RATE);
  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_STATUS_LED, LOW);

#ifndef SIMULATION_MODE
  panServo.attach(PIN_SERVO_PAN);
  tiltServo.attach(PIN_SERVO_TILT);

  panServo.write(PAN_NOMINAL_DEG);
  tiltServo.write(TILT_NOMINAL_DEG);
#endif

  currentPanDeg = PAN_NOMINAL_DEG;
  currentTiltDeg = TILT_NOMINAL_DEG;
  targetPanDeg = PAN_NOMINAL_DEG;
  targetTiltDeg = TILT_NOMINAL_DEG;

  lastFeedbackTime = millis();
}

void processCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  if (cmd.startsWith("SERVO")) {
    // Format: SERVO <pan_deg> <tilt_deg>
    int firstSpace = cmd.indexOf(' ');
    if (firstSpace > 0) {
      int secondSpace = cmd.indexOf(' ', firstSpace + 1);
      if (secondSpace > 0) {
        int pan = cmd.substring(firstSpace + 1, secondSpace).toInt();
        int tilt = cmd.substring(secondSpace + 1).toInt();

        // Clamp
        pan = constrain(pan, PAN_MIN_DEG, PAN_MAX_DEG);
        tilt = constrain(tilt, TILT_MIN_DEG, TILT_MAX_DEG);

        targetPanDeg = pan;
        targetTiltDeg = tilt;

#ifndef SIMULATION_MODE
        panServo.write(targetPanDeg);
        tiltServo.write(targetTiltDeg);
#endif
        digitalWrite(PIN_STATUS_LED, HIGH);
      }
    }
  } else if (cmd.equalsIgnoreCase("PING")) {
    Serial.println("PONG");
  }
}

void loop() {
  // Read Serial input
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (inputBuffer.length() > 0) {
        processCommand(inputBuffer);
        inputBuffer = "";
      }
    } else {
      inputBuffer += c;
    }
  }

  // Simulation mode position integration
#ifdef SIMULATION_MODE
  currentPanDeg += (targetPanDeg - currentPanDeg) * 0.2f;
  currentTiltDeg += (targetTiltDeg - currentTiltDeg) * 0.2f;
#else
  currentPanDeg = targetPanDeg;
  currentTiltDeg = targetTiltDeg;
#endif

  // Periodic feedback streaming at 50 Hz
  unsigned long now = millis();
  if (now - lastFeedbackTime >= FEEDBACK_INTERVAL_MS) {
    lastFeedbackTime = now;
    Serial.print("SERVO_POS ");
    Serial.print(currentPanDeg);
    Serial.print(" ");
    Serial.println(currentTiltDeg);
    digitalWrite(PIN_STATUS_LED, LOW);
  }
}
