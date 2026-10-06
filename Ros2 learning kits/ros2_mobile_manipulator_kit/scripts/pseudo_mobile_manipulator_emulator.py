#!/usr/bin/env python3
"""
Mobile Manipulator Pseudo-Hardware Serial Emulator
===================================================

Emulates both the 4WD mobile base controller and the 6-DOF articulated arm controller
for the ros2_control hardware interfaces (BaseHardwareInterface & ArmHardwareInterface).

Creates two virtual serial ports (PTY) or a single unified port:
  - Base Port: /tmp/tty_mm_base (VEL,<left>,<right>\n -> ENC,<fl>,<fr>,<bl>,<br>\n at 50 Hz)
  - Arm Port:  /tmp/tty_mm_arm  (SET_ALL_SERVOS,<s0>..<s5>\n -> SERVO_POS,<p0>..<p5>\n at 50 Hz)

Enables full desktop hardware-in-the-loop (HIL) testing without physical hardware.
"""

import os
import pty
import time
import threading
import argparse
import signal
import sys
import math

class VirtualSerialChannel:
    def __init__(self, port_path, name="Channel"):
        self.port_path = port_path
        self.name = name
        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_name = os.ttyname(self.slave_fd)

        if os.path.exists(self.port_path):
            try:
                os.remove(self.port_path)
            except OSError:
                pass
        os.symlink(self.slave_name, self.port_path)
        print(f"[{self.name}] Virtual PTY active: {self.slave_name} -> {self.port_path}")

    def read_nonblocking(self, max_bytes=128):
        try:
            return os.read(self.master_fd, max_bytes).decode('utf-8', errors='ignore')
        except OSError:
            return ""

    def write(self, data_str):
        try:
            os.write(self.master_fd, data_str.encode('utf-8'))
        except OSError:
            pass

    def close(self):
        try:
            os.close(self.master_fd)
        except OSError:
            pass
        try:
            os.close(self.slave_fd)
        except OSError:
            pass
        if os.path.islink(self.port_path):
            try:
                os.remove(self.port_path)
            except OSError:
                pass
        print(f"[{self.name}] Closed.")


class PseudoMobileManipulator:
    def __init__(self, base_port="/tmp/tty_mm_base", arm_port="/tmp/tty_mm_arm"):
        self.base_chan = VirtualSerialChannel(base_port, name="BaseChannel")
        self.arm_chan = VirtualSerialChannel(arm_port, name="ArmChannel")
        self.running = False

        # Base kinematics state
        self.wheel_radius = 0.075
        self.encoder_cpr = 360
        self.left_vel_cmd = 0.0
        self.right_vel_cmd = 0.0
        self.fl_counts = 0.0
        self.fr_counts = 0.0
        self.bl_counts = 0.0
        self.br_counts = 0.0

        # Arm state (6 servos: 0-180 degrees, default home is 90)
        self.target_servos = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]
        self.current_servos = [90.0, 90.0, 90.0, 90.0, 90.0, 90.0]

    def start(self):
        self.running = True
        self.base_rx_thread = threading.Thread(target=self._base_rx_loop, daemon=True)
        self.base_tx_thread = threading.Thread(target=self._base_tx_loop, daemon=True)
        self.arm_rx_thread = threading.Thread(target=self._arm_rx_loop, daemon=True)
        self.arm_tx_thread = threading.Thread(target=self._arm_tx_loop, daemon=True)

        self.base_rx_thread.start()
        self.base_tx_thread.start()
        self.arm_rx_thread.start()
        self.arm_tx_thread.start()
        print("[PseudoMobileManipulator] Emulator engine online at 50 Hz streaming rate.")

    def _base_rx_loop(self):
        buf = ""
        while self.running:
            data = self.base_chan.read_nonblocking()
            if data:
                buf += data
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if line.startswith("VEL,"):
                        parts = line[4:].split(",")
                        if len(parts) >= 2:
                            try:
                                self.left_vel_cmd = float(parts[0])
                                self.right_vel_cmd = float(parts[1])
                            except ValueError:
                                pass
                    elif line == "STOP" or line == "STOP_BASE":
                        self.left_vel_cmd = 0.0
                        self.right_vel_cmd = 0.0
                    elif line == "RST":
                        self.fl_counts = self.fr_counts = self.bl_counts = self.br_counts = 0.0
            time.sleep(0.005)

    def _base_tx_loop(self):
        dt = 0.02 # 50 Hz
        while self.running:
            # Integrate velocities into encoder ticks
            ticks_per_meter = self.encoder_cpr / (2.0 * math.pi * self.wheel_radius)
            d_left = self.left_vel_cmd * dt * ticks_per_meter
            d_right = self.right_vel_cmd * dt * ticks_per_meter

            self.fl_counts += d_left
            self.bl_counts += d_left
            self.fr_counts += d_right
            self.br_counts += d_right

            msg = f"ENC,{int(self.fl_counts)},{int(self.fr_counts)},{int(self.bl_counts)},{int(self.br_counts)}\n"
            self.base_chan.write(msg)
            time.sleep(dt)

    def _arm_rx_loop(self):
        buf = ""
        while self.running:
            data = self.arm_chan.read_nonblocking()
            if data:
                buf += data
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if line.startswith("SET_ALL_SERVOS,"):
                        parts = line[15:].split(",")
                        for i in range(min(len(parts), 6)):
                            try:
                                self.target_servos[i] = float(parts[i])
                            except ValueError:
                                pass
                    elif line.startswith("ARM,"):
                        parts = line[4:].split(",")
                        for i in range(min(len(parts), 6)):
                            try:
                                self.target_servos[i] = float(parts[i])
                            except ValueError:
                                pass
                    elif line == "STOP" or line == "STOP_ARM":
                        pass
            time.sleep(0.005)

    def _arm_tx_loop(self):
        dt = 0.02 # 50 Hz
        alpha = 0.15 # Smooth interpolation
        while self.running:
            for i in range(6):
                self.current_servos[i] += alpha * (self.target_servos[i] - self.current_servos[i])

            servos_str = ",".join(f"{s:.1f}" for s in self.current_servos)
            msg = f"SERVO_POS,{servos_str}\n"
            self.arm_chan.write(msg)
            time.sleep(dt)

    def stop(self):
        self.running = False
        self.base_chan.close()
        self.arm_chan.close()
        print("[PseudoMobileManipulator] Emulator stopped.")


def main():
    parser = argparse.ArgumentParser(description="Mobile Manipulator Pseudo-Hardware Serial Emulator")
    parser.add_argument("--base-port", default="/tmp/tty_mm_base", help="Symlink path for base virtual serial port")
    parser.add_argument("--arm-port", default="/tmp/tty_mm_arm", help="Symlink path for arm virtual serial port")
    args = parser.parse_args()

    emulator = PseudoMobileManipulator(base_port=args.base_port, arm_port=args.arm_port)
    emulator.start()

    def shutdown_handler(signum, frame):
        emulator.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    print("[PseudoMobileManipulator] Press Ctrl+C to terminate.")
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
