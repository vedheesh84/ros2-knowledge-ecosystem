#!/usr/bin/env python3
"""
pseudo_companion_head_emulator.py
=================================
Desktop Pseudo-Hardware Emulator for Companion Head 2-DOF Pan/Tilt Neck.

Creates a virtual serial port using PTY and responds to ros2_control hardware interface
commands with realistic servo dynamics and 50 Hz position telemetry:
- Listens for: "SERVO <pan_deg> <tilt_deg>\n"
- Streams: "SERVO_POS <pan_deg> <tilt_deg>\n" at 50 Hz
- Supports: "PING" -> "PONG"

Usage:
    python3 scripts/pseudo_companion_head_emulator.py --serial-port /tmp/tty_companion_head
"""

import os
import pty
import sys
import time
import errno
import signal
import select
import argparse
import threading

class PseudoCompanionHeadEmulator:
    def __init__(self, serial_port_symlink: str = "/tmp/tty_companion_head"):
        self.symlink_path = serial_port_symlink
        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_name = os.ttyname(self.slave_fd)
        self.running = True

        # Joint States (in degrees)
        self.pan_target = 90.0
        self.tilt_target = 90.0
        self.pan_pos = 90.0
        self.tilt_pos = 90.0

        # Replace existing symlink if present
        if os.path.islink(self.symlink_path) or os.path.exists(self.symlink_path):
            os.remove(self.symlink_path)
        os.symlink(self.slave_name, self.symlink_path)
        print(f"[EMULATOR] Virtual Companion Head Serial Port active at {self.symlink_path} -> {self.slave_name}")

        self.lock = threading.Lock()
        self.read_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.write_thread = threading.Thread(target=self._streamer_loop, daemon=True)

    def start(self):
        self.read_thread.start()
        self.write_thread.start()

    def _reader_loop(self):
        buf = ""
        while self.running:
            try:
                r, _, _ = select.select([self.master_fd], [], [], 0.05)
                if not r:
                    continue
                data = os.read(self.master_fd, 256).decode("utf-8", errors="ignore")
                if not data:
                    continue
                buf += data
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if line:
                        self._process_command(line)
            except (OSError, select.error) as e:
                if not self.running:
                    break
                time.sleep(0.01)

    def _process_command(self, cmd: str):
        if cmd.startswith("SERVO"):
            parts = cmd.split()
            if len(parts) >= 3:
                try:
                    p = float(parts[1])
                    t = float(parts[2])
                    with self.lock:
                        self.pan_target = max(0.0, min(180.0, p))
                        self.tilt_target = max(45.0, min(135.0, t))
                except ValueError:
                    pass
        elif cmd.upper() == "PING":
            try:
                os.write(self.master_fd, b"PONG\n")
            except OSError:
                pass

    def _streamer_loop(self):
        rate = 50.0  # 50 Hz
        dt = 1.0 / rate
        while self.running:
            start_t = time.time()
            with self.lock:
                # 1st order servo low-pass filter
                alpha = 0.3
                self.pan_pos += alpha * (self.pan_target - self.pan_pos)
                self.tilt_pos += alpha * (self.tilt_target - self.tilt_pos)
                msg = f"SERVO_POS {self.pan_pos:.1f} {self.tilt_pos:.1f}\n"

            try:
                os.write(self.master_fd, msg.encode("utf-8"))
            except OSError as e:
                if e.errno == errno.EIO:
                    pass  # Client disconnected
            
            elapsed = time.time() - start_t
            sleep_t = max(0.001, dt - elapsed)
            time.sleep(sleep_t)

    def stop(self):
        self.running = False
        try:
            os.close(self.master_fd)
            os.close(self.slave_fd)
        except OSError:
            pass
        if os.path.islink(self.symlink_path) or os.path.exists(self.symlink_path):
            try:
                os.remove(self.symlink_path)
            except OSError:
                pass
        print("[EMULATOR] Shutdown complete.")

def main():
    parser = argparse.ArgumentParser(description="Pseudo Companion Head Serial Emulator")
    parser.add_argument("--serial-port", default="/tmp/tty_companion_head", help="Virtual serial port path")
    args = parser.parse_args()

    emulator = PseudoCompanionHeadEmulator(args.serial_port)
    emulator.start()

    def sig_handler(sig, frame):
        emulator.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    while True:
        time.sleep(1.0)

if __name__ == "__main__":
    main()
