#!/usr/bin/env python3
# Copyright (c) 2026 ROS2 Learning Ecosystem
# MIT License

"""
pseudo_quadruped_emulator.py
============================
Desktop pseudo-hardware emulator for the 12-DOF Quadruped robot.
Creates a virtual serial port (PTY) that emulates the low-level MCU controller
and streaming IMU sensor telemetry at 50 Hz.

Allows running hardware bringup and ros2_control without physical hardware attached.
"""

import os
import pty
import sys
import time
import math
import select
import signal
import argparse
import numpy as np


class PseudoQuadrupedEmulator:
    def __init__(self, port_link="/tmp/tty_quadruped", rate_hz=50.0):
        self.port_link = port_link
        self.rate_hz = rate_hz
        self.dt = 1.0 / rate_hz
        self.running = True

        # Open PTY pair
        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_name = os.ttyname(self.slave_fd)

        # Create symlink
        if os.path.islink(self.port_link) or os.path.exists(self.port_link):
            try:
                os.remove(self.port_link)
            except OSError:
                pass
        os.symlink(self.slave_name, self.port_link)
        print(f"[PseudoQuadruped] Virtual PTY active: {self.slave_name} -> {self.port_link}")

        # 12-DOF Joint States
        # Order: FL_HAA, FL_HFE, FL_KFE, FR_HAA, FR_HFE, FR_KFE, RL_HAA, RL_HFE, RL_KFE, RR_HAA, RR_HFE, RR_KFE
        self.num_joints = 12
        self.positions = np.array([
            0.0, -0.5, 1.0,   # FL
            0.0, -0.5, 1.0,   # FR
            0.0, -0.5, 1.0,   # RL
            0.0, -0.5, 1.0    # RR
        ], dtype=float)
        self.velocities = np.zeros(self.num_joints, dtype=float)
        self.efforts = np.zeros(self.num_joints, dtype=float)
        self.target_torques = np.zeros(self.num_joints, dtype=float)

        # IMU states
        self.qx = 0.0
        self.qy = 0.0
        self.qz = 0.0
        self.qw = 1.0
        self.gx = 0.0
        self.gy = 0.0
        self.gz = 0.0
        self.ax = 0.0
        self.ay = 0.0
        self.az = 9.81

        # Physical simulation constants
        self.inertia = 0.05
        self.damping = 0.3
        self.buffer = ""

    def handle_line(self, line: str):
        line = line.strip()
        if not line:
            return

        if line == "PING":
            os.write(self.master_fd, b"PONG\n")
        elif line == "ESTOP":
            self.target_torques.fill(0.0)
            self.efforts.fill(0.0)
            os.write(self.master_fd, b"# ESTOP_ACTIVATED\n")
        elif line.startswith("TORQUE"):
            parts = line.split()
            if len(parts) >= 13:
                try:
                    for i in range(12):
                        self.target_torques[i] = float(parts[i + 1])
                except ValueError:
                    pass
        elif line.startswith("POS"):
            parts = line.split()
            if len(parts) >= 13:
                try:
                    for i in range(12):
                        self.positions[i] = float(parts[i + 1])
                except ValueError:
                    pass

    def update_physics(self):
        # Integrate joint dynamics: I * alpha + b * omega = tau
        accel = (self.target_torques - self.damping * self.velocities) / self.inertia
        self.velocities += accel * self.dt
        self.positions += self.velocities * self.dt
        self.efforts[:] = self.target_torques[:]

        # Small attitude noise / micro-wobble
        t = time.time()
        pitch_wobble = 0.02 * math.sin(2.0 * math.pi * 0.5 * t)
        self.qy = math.sin(pitch_wobble / 2.0)
        self.qw = math.cos(pitch_wobble / 2.0)
        self.gy = 0.02 * math.cos(2.0 * math.pi * 0.5 * t)

    def send_telemetry(self):
        pos_str = "POS " + " ".join(f"{p:.4f}" for p in self.positions) + "\n"
        vel_str = "VEL " + " ".join(f"{v:.4f}" for v in self.velocities) + "\n"
        eff_str = "EFF " + " ".join(f"{e:.4f}" for e in self.efforts) + "\n"
        imu_str = f"IMU {self.qx:.4f} {self.qy:.4f} {self.qz:.4f} {self.qw:.4f} {self.gx:.4f} {self.gy:.4f} {self.gz:.4f} {self.ax:.4f} {self.ay:.4f} {self.az:.4f}\n"

        packet = (pos_str + vel_str + eff_str + imu_str).encode('ascii')
        try:
            os.write(self.master_fd, packet)
        except OSError:
            pass

    def run(self):
        print(f"[PseudoQuadruped] Emulator streaming at {self.rate_hz} Hz. Press Ctrl+C to terminate.")
        interval = 1.0 / self.rate_hz
        next_time = time.time()

        while self.running:
            # Check for incoming commands
            r, _, _ = select.select([self.master_fd], [], [], 0.002)
            if self.master_fd in r:
                try:
                    data = os.read(self.master_fd, 1024).decode('ascii', errors='ignore')
                    self.buffer += data
                    while '\n' in self.buffer:
                        line, self.buffer = self.buffer.split('\n', 1)
                        self.handle_line(line)
                except OSError:
                    break

            now = time.time()
            if now >= next_time:
                self.update_physics()
                self.send_telemetry()
                next_time = now + interval

            time.sleep(0.002)

    def close(self):
        self.running = False
        try:
            os.close(self.master_fd)
            os.close(self.slave_fd)
        except OSError:
            pass
        if os.path.islink(self.port_link):
            try:
                os.remove(self.port_link)
            except OSError:
                pass
        print("[PseudoQuadruped] Emulator stopped.")


def main():
    parser = argparse.ArgumentParser(description="Pseudo Quadruped Hardware Emulator")
    parser.add_argument("--port", default="/tmp/tty_quadruped", help="Symlink path for PTY")
    parser.add_argument("--rate", type=float, default=50.0, help="Streaming rate in Hz")
    args = parser.parse_args()

    emulator = PseudoQuadrupedEmulator(port_link=args.port, rate_hz=args.rate)

    def sig_handler(sig, frame):
        emulator.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    try:
        emulator.run()
    finally:
        emulator.close()


if __name__ == '__main__':
    main()
