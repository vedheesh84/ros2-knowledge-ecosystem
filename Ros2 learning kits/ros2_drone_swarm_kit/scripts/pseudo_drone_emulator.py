#!/usr/bin/env python3
import os
import pty
import tty
import termios
import select
import time
import math
import argparse
import signal
import sys

class PseudoDroneEmulator:
    """
    Simulates physical drone flight controller hardware over a virtual serial PTY port.
    Streams 50 Hz telemetry and responds to ARM, DISARM, and CMD attitude/thrust commands.
    """
    def __init__(self, port_link="/tmp/ttyVIRT_DRONE"):
        self.port_link = port_link
        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_name = os.ttyname(self.slave_fd)

        # Set raw mode on master
        tty.setraw(self.master_fd)

        # Update symlink
        if os.path.exists(self.port_link) or os.path.islink(self.port_link):
            try:
                os.unlink(self.port_link)
            except OSError:
                pass
        os.symlink(self.slave_name, self.port_link)
        print(f"[PseudoDrone] Virtual serial port active: {self.slave_name} -> {self.port_link}")

        # Flight State
        self.armed = False
        self.flying = False
        self.sp_roll = 0.0
        self.sp_pitch = 0.0
        self.sp_yaw_rate = 0.0
        self.sp_thrust = 0.0

        # Dynamics
        self.est_roll = 0.0
        self.est_pitch = 0.0
        self.est_yaw = 0.0
        self.est_alt = 0.0
        self.est_vx = 0.0
        self.est_vy = 0.0
        self.est_vz = 0.0
        self.battery = 12.6

        self.running = True
        self.rx_buffer = ""

    def process_command(self, cmd_line: str):
        cmd = cmd_line.strip()
        if not cmd:
            return

        if cmd == "ARM":
            self.armed = True
            print("[PseudoDrone] >>> ARMED received. Motors active.")
        elif cmd == "DISARM":
            self.armed = False
            self.flying = False
            self.sp_thrust = 0.0
            print("[PseudoDrone] >>> DISARMED received. Motors cut.")
        elif cmd.startswith("CMD,"):
            # Format: CMD,roll,pitch,yaw_rate,thrust
            parts = cmd.split(",")
            if len(parts) >= 5:
                try:
                    self.sp_roll = float(parts[1])
                    self.sp_pitch = float(parts[2])
                    self.sp_yaw_rate = float(parts[3])
                    self.sp_thrust = float(parts[4])
                    if self.armed and self.sp_thrust > 10.0:
                        self.flying = True
                except ValueError:
                    pass

    def update_physics(self, dt: float):
        if not self.armed:
            self.est_roll = 0.0
            self.est_pitch = 0.0
            self.est_vx = 0.0
            self.est_vy = 0.0
            self.est_vz = 0.0
            if self.est_alt > 0.0:
                self.est_alt = max(0.0, self.est_alt - 1.5 * dt)
            return

        # 1st-order attitude convergence
        tau = 0.1
        self.est_roll += (self.sp_roll - self.est_roll) * (dt / tau)
        self.est_pitch += (self.sp_pitch - self.est_pitch) * (dt / tau)
        self.est_yaw += self.sp_yaw_rate * dt

        # Velocities derived from body tilt
        self.est_vx = -math.sin(math.radians(self.est_pitch)) * 3.5
        self.est_vy = math.sin(math.radians(self.est_roll)) * 3.5

        # Vertical velocity from thrust
        if self.sp_thrust > 50.0:
            self.est_vz = (self.sp_thrust - 50.0) * 0.03
        elif self.sp_thrust > 10.0:
            self.est_vz = (self.sp_thrust - 50.0) * 0.04
        else:
            self.est_vz = -1.2 # Descending

        self.est_alt = max(0.0, self.est_alt + self.est_vz * dt)
        self.battery = max(10.5, self.battery - 0.0001)

    def run(self):
        last_tick = time.time()
        try:
            while self.running:
                now = time.time()
                dt = now - last_tick
                if dt >= 0.02: # 50 Hz
                    last_tick = now
                    self.update_physics(dt)

                    # Format telemetry: TELEM,roll,pitch,yaw,alt,vx,vy,vz,armed,battery
                    telem = (
                        f"TELEM,{self.est_roll:.2f},{self.est_pitch:.2f},{self.est_yaw:.2f},"
                        f"{self.est_alt:.2f},{self.est_vx:.2f},{self.est_vy:.2f},{self.est_vz:.2f},"
                        f"{1 if self.armed else 0},{self.battery:.2f}\r\n"
                    )
                    try:
                        os.write(self.master_fd, telem.encode('ascii'))
                    except OSError:
                        pass

                # Check for incoming serial data
                r, _, _ = select.select([self.master_fd], [], [], 0.005)
                if self.master_fd in r:
                    try:
                        chunk = os.read(self.master_fd, 128).decode('ascii', errors='ignore')
                        self.rx_buffer += chunk
                        while '\n' in self.rx_buffer:
                            line, self.rx_buffer = self.rx_buffer.split('\n', 1)
                            self.process_command(line.strip())
                    except OSError:
                        pass
        finally:
            self.cleanup()

    def cleanup(self):
        print("\n[PseudoDrone] Shutting down emulator...")
        if os.path.exists(self.port_link):
            try:
                os.unlink(self.port_link)
            except OSError:
                pass
        try:
            os.close(self.master_fd)
            os.close(self.slave_fd)
        except OSError:
            pass

def main():
    parser = argparse.ArgumentParser(description="Pseudo Drone Flight Controller Serial Emulator")
    parser.add_argument("--port", default="/tmp/ttyVIRT_DRONE", help="Symlink path for virtual serial port")
    args = parser.parse_args()

    emulator = PseudoDroneEmulator(port_link=args.port)

    def sig_handler(sig, frame):
        emulator.running = False

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    emulator.run()

if __name__ == "__main__":
    main()
