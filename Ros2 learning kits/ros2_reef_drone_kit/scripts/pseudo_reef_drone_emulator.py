#!/usr/bin/env python3
"""
pseudo_reef_drone_emulator.py - Desktop Pseudo-Hardware Emulator for Reef Drone AUV

Creates a virtual serial port (PTY loopback) to emulate the physical Arduino/ESP32
flight controller and MS5837-30BA pressure sensor without physical hardware.

Virtual Port: /tmp/ttyAUV_SIM
Protocol:
  - Input:  "<T1,T2,T3,T4,T5,T6>\n" (normalized values in [-1.0, 1.0])
  - Output: "$TELEM,DEPTH:<m>,PRESS:<Pa>,TEMP:<C>,STATUS:<ARMED/FAILSAFE>\n" (20 Hz)
"""

import os
import pty
import sys
import time
import signal
import select
import random
import numpy as np

SYMLINK_PATH = "/tmp/ttyAUV_SIM"

class PseudoAUVEmulator:
    def __init__(self):
        # Open pseudo-terminal master/slave pair
        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_name = os.ttyname(self.slave_fd)

        # Create convenience symlink
        try:
            if os.path.islink(SYMLINK_PATH) or os.path.exists(SYMLINK_PATH):
                os.unlink(SYMLINK_PATH)
            os.symlink(self.slave_name, SYMLINK_PATH)
        except Exception as e:
            print(f"[WARN] Failed to create symlink {SYMLINK_PATH}: {e}")

        print(f"[AUV_EMU] Virtual Serial Port created at: {self.slave_name}")
        print(f"[AUV_EMU] Symlinked to: {SYMLINK_PATH}")

        # Physical parameters (BlueROV2 / Reef Drone specs)
        self.mass = 11.5          # kg
        self.buoyancy_net = 1.8   # N (upward net force)
        self.max_thrust = 50.0    # N per thruster
        self.linear_drag_z = 10.0 # N*s/m
        self.quad_drag_z = 40.0   # N*s^2/m^2

        # State
        self.depth = 5.0          # Start at 5.0m depth
        self.velocity_z = 0.0     # m/s (depth rate, positive down)
        self.armed = False
        self.last_cmd_time = time.time()
        self.running = True
        self.cmd_thrusts = [0.0] * 6

        # Failsafe settings
        self.timeout_sec = 0.5    # 500ms heartbeat timeout

        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def _handle_exit(self, signum, frame):
        self.running = False

    def parse_packet(self, data_str: str):
        # Expected: "<T1,T2,T3,T4,T5,T6>"
        start = data_str.find("<")
        end = data_str.find(">")
        if start != -1 and end != -1 and end > start:
            payload = data_str[start + 1:end]
            parts = payload.split(",")
            if len(parts) == 6:
                try:
                    self.cmd_thrusts = [float(p.strip()) for p in parts]
                    self.armed = True
                    self.last_cmd_time = time.time()
                except ValueError:
                    pass

    def update_physics(self, dt: float):
        now = time.time()
        # Watchdog check
        if self.armed and (now - self.last_cmd_time > self.timeout_sec):
            self.armed = False
            self.cmd_thrusts = [0.0] * 6

        if self.armed:
            # T5 and T6 are vertical thrusters (positive commands = downward push / dive)
            # Upward thrust = negative command in depth coordinates
            vert_cmd = (self.cmd_thrusts[4] + self.cmd_thrusts[5]) / 2.0
            thrust_force_z = -vert_cmd * (2.0 * self.max_thrust) # positive = down
        else:
            thrust_force_z = 0.0

        # Net forces in depth direction (positive down):
        # Weight - Buoyancy = -1.8 N (upward buoyancy pushes towards depth 0)
        # Drag opposes velocity
        drag_force = -self.linear_drag_z * self.velocity_z - self.quad_drag_z * abs(self.velocity_z) * self.velocity_z
        buoyancy_force_down = -self.buoyancy_net # upward = negative in depth axis

        total_force = thrust_force_z + buoyancy_force_down + drag_force
        accel_z = total_force / self.mass

        self.velocity_z += accel_z * dt
        self.depth += self.velocity_z * dt

        # Ocean surface limit (depth cannot be negative)
        if self.depth < 0.0:
            self.depth = 0.0
            if self.velocity_z < 0:
                self.velocity_z = 0.0

    def get_telemetry_packet(self) -> str:
        # Hydrostatic pressure: P = P_atm + rho * g * depth
        p_atm = 101325.0 # Pa
        rho = 1025.0     # kg/m^3
        g = 9.80665      # m/s^2

        pressure = p_atm + rho * g * self.depth + random.gauss(0.0, 15.0)
        status_str = "ARMED" if self.armed else "FAILSAFE"
        temp = 22.5 + random.gauss(0.0, 0.05)

        return f"$TELEM,DEPTH:{self.depth:.3f},PRESS:{pressure:.1f},TEMP:{temp:.1f},STATUS:{status_str}\n"

    def run(self):
        last_update = time.time()
        last_telem = time.time()
        rx_buffer = ""

        print("[AUV_EMU] Emulator loop active. Transmitting telemetry @ 20 Hz.")

        while self.running:
            now = time.time()
            dt = now - last_update
            last_update = now

            self.update_physics(dt)

            # Check for incoming commands
            r, _, _ = select.select([self.master_fd], [], [], 0.01)
            if self.master_fd in r:
                try:
                    data = os.read(self.master_fd, 256).decode("utf-8", errors="ignore")
                    rx_buffer += data
                    if "\n" in rx_buffer or ">" in rx_buffer:
                        self.parse_packet(rx_buffer)
                        rx_buffer = ""
                except OSError:
                    pass

            # Send telemetry at 20 Hz (every 50ms)
            if now - last_telem >= 0.05:
                last_telem = now
                packet = self.get_telemetry_packet()
                try:
                    os.write(self.master_fd, packet.encode("utf-8"))
                except OSError:
                    pass

            time.sleep(0.01)

        self.cleanup()

    def cleanup(self):
        print("\n[AUV_EMU] Shutting down emulator.")
        try:
            if os.path.islink(SYMLINK_PATH):
                os.unlink(SYMLINK_PATH)
        except Exception:
            pass
        try:
            os.close(self.master_fd)
            os.close(self.slave_fd)
        except Exception:
            pass


if __name__ == "__main__":
    emu = PseudoAUVEmulator()
    emu.run()
