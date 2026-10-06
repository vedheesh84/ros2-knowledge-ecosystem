#!/usr/bin/env python3
"""
Robotic Arm Pseudo-Hardware Serial Emulator
===========================================

Emulates the microcontroller servo controller for the 5-DOF articulated arm.
Creates a virtual serial port (PTY) and communicates via:
  - Inbound:  ANGLES,<j1>,<j2>,<j3>,<j4>,<j5>\n
  - Outbound: POS,<j1>,<j2>,<j3>,<j4>,<j5>\n at 50 Hz

Enables end-to-end hardware-in-the-loop testing on desktop without physical arm hardware.
"""

import os
import pty
import time
import threading
import argparse
import signal
import sys

class PseudoArmHardware:
    def __init__(self, port_path="/tmp/tty_arm_fake", baud=115200):
        self.port_path = port_path
        self.baud = baud
        self.num_joints = 5
        
        self.master_fd, self.slave_fd = pty.openpty()
        self.slave_name = os.ttyname(self.slave_fd)
        
        if os.path.exists(self.port_path):
            try:
                os.remove(self.port_path)
            except OSError:
                pass
        os.symlink(self.slave_name, self.port_path)
        
        self.target_angles = [0.0] * self.num_joints
        self.current_angles = [0.0] * self.num_joints
        self.running = False
        
    def start(self):
        self.running = True
        self.tx_thread = threading.Thread(target=self._tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        self.tx_thread.start()
        self.rx_thread.start()
        print(f"[PseudoArmHardware] Virtual serial bridge active:")
        print(f"  Slave PTY: {self.slave_name}")
        print(f"  Symlink:   {self.port_path}")
        print(f"  Baud:      {self.baud}")

    def _rx_loop(self):
        buf = ""
        while self.running:
            try:
                data = os.read(self.master_fd, 128).decode('utf-8', errors='ignore')
                if not data:
                    break
                buf += data
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if line.startswith("ANGLES,"):
                        parts = line[7:].split(",")
                        for i in range(min(len(parts), self.num_joints)):
                            try:
                                self.target_angles[i] = float(parts[i])
                            except ValueError:
                                pass
                    elif line == "HOME":
                        self.target_angles = [0.0] * self.num_joints
                    elif line == "TEST,ON":
                        os.write(self.master_fd, b"STATUS,TEST_MODE_ENABLED\n")
            except OSError:
                break

    def _tx_loop(self):
        dt = 0.02 # 50 Hz
        alpha = 0.15 # Smooth filter
        while self.running:
            # Interpolate towards targets
            for i in range(self.num_joints):
                self.current_angles[i] += alpha * (self.target_angles[i] - self.current_angles[i])
                
            angles_str = ",".join(f"{a:.3f}" for a in self.current_angles)
            msg = f"POS,{angles_str}\n"
            try:
                os.write(self.master_fd, msg.encode('utf-8'))
            except OSError:
                break
            time.sleep(dt)

    def stop(self):
        self.running = False
        try:
            os.close(self.master_fd)
        except OSError:
            pass
        try:
            os.close(self.slave_fd)
        except OSError:
            pass
        if os.path.islink(self.port_path):
            os.remove(self.port_path)
        print("[PseudoArmHardware] Bridge closed")

def main():
    parser = argparse.ArgumentParser(description="Robotic Arm Pseudo-Hardware Serial Emulator")
    parser.add_argument("--port", default="/tmp/tty_arm_fake", help="Symlink path for virtual serial port")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate")
    args = parser.parse_args()
    
    bridge = PseudoArmHardware(port_path=args.port, baud=args.baud)
    bridge.start()
    
    def shutdown_handler(signum, frame):
        bridge.stop()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    print("[PseudoArmHardware] Press Ctrl+C to terminate.")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
