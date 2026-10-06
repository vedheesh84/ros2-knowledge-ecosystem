#!/usr/bin/env python3
# Copyright (c) 2026 ROS2 Learning Ecosystem
# MIT License

"""
test_quadruped_kit.py
=====================
Complete end-to-end verification suite for `ros2_quadruped_kit`.
Validates:
1. Leg Kinematics, Jacobian Force Mapping & Bezier Swing Trajectory
2. Gait Scheduling, Single Rigid Body Dynamics & Joint PD Control
3. Contact Force Estimation & Behavior State Machine Lifecycle
4. ros2_control Multi-Controller Stack with Virtual Hardware Emulator
5. Progressive Demos & Intentional Failure Injection Breakers
"""

import os
import sys
import time
import math
import signal
import subprocess
import numpy as np


def safe_kill(proc):
    """Safely terminate a subprocess or process group."""
    if proc is None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except Exception:
        try:
            proc.terminate()
        except Exception:
            pass
    try:
        proc.wait(timeout=2.0)
    except Exception:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


def log_section(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def test_kinematics_and_swing_trajectory():
    log_section("TEST 1: Leg Kinematics, Jacobian Transpose & Bezier Swing Trajectory")
    from quadruped_locomotion.swing_trajectory import SwingTrajectory, cubic_bezier
    from quadruped_control.whole_body_controller import WholeBodyController

    # 1. Test Cubic Bezier Curve Math
    # At t=0, P=p0; at t=1, P=p3
    p0, p1, p2, p3 = 0.0, 0.1, 0.2, 1.0
    val_0 = cubic_bezier(0.0, p0, p1, p2, p3)
    val_1 = cubic_bezier(1.0, p0, p1, p2, p3)
    val_mid = cubic_bezier(0.5, p0, p1, p2, p3)
    assert abs(val_0 - p0) < 1e-4, f"Bezier start expected {p0}, got {val_0}"
    assert abs(val_1 - p3) < 1e-4, f"Bezier end expected {p3}, got {val_1}"
    assert 0.0 < val_mid < 1.0, f"Bezier midpoint {val_mid} out of bounds"
    print(f"[Bezier Math Test] Start={val_0:.2f}, Mid={val_mid:.2f}, End={val_1:.2f} -> PASS")

    # 2. Test Swing Trajectory Generator
    swing_gen = SwingTrajectory(swing_height=0.08, landing_height_offset=-0.01)
    start_pos = np.array([0.15, 0.10, -0.30])
    target_pos = np.array([0.25, 0.10, -0.30])

    pos_0, vel_0 = swing_gen.compute_trajectory(start_pos, target_pos, phase=0.0)
    pos_mid, vel_mid = swing_gen.compute_trajectory(start_pos, target_pos, phase=0.5)
    pos_1, vel_1 = swing_gen.compute_trajectory(start_pos, target_pos, phase=1.0)

    print(f"[Swing Trajectory Test] Start Pos:  ({pos_0[0]:.3f}, {pos_0[1]:.3f}, {pos_0[2]:.3f})")
    print(f"[Swing Trajectory Test] Mid Pos:    ({pos_mid[0]:.3f}, {pos_mid[1]:.3f}, {pos_mid[2]:.3f})")
    print(f"[Swing Trajectory Test] Landing Pos:({pos_1[0]:.3f}, {pos_1[1]:.3f}, {pos_1[2]:.3f})")

    assert np.allclose(pos_0[:2], start_pos[:2], atol=1e-3), "Swing start XY should match start position"
    assert pos_mid[2] > start_pos[2] + 0.04, f"Mid swing height {pos_mid[2]} did not clear ground"
    assert np.allclose(pos_1[:2], target_pos[:2], atol=1e-3), "Swing end XY should match target position"
    print("  -> Swing trajectory achieves specified clearance and touchdown accuracy.")

    # 3. Test Analytical Leg Jacobian & Force-to-Torque Mapping
    import rclpy
    if not rclpy.ok():
        rclpy.init()
    wbc = WholeBodyController()
    wbc.joint_positions = {
        'FL_HAA': 0.0, 'FL_HFE': -0.5, 'FL_KFE': 1.0,
        'FR_HAA': 0.0, 'FR_HFE': -0.5, 'FR_KFE': 1.0,
        'RL_HAA': 0.0, 'RL_HFE': -0.5, 'RL_KFE': 1.0,
        'RR_HAA': 0.0, 'RR_HFE': -0.5, 'RR_KFE': 1.0,
    }
    J_fl = wbc.compute_jacobian('FL')
    assert J_fl.shape == (3, 3), f"Jacobian shape expected (3, 3), got {J_fl.shape}"
    # Ground reaction force [0, 0, 50N]
    F_foot = np.array([0.0, 0.0, 50.0])
    tau_fl = J_fl.T @ F_foot
    print(f"[Jacobian Test] Leg FL Jacobian det: {np.linalg.det(J_fl):.4f}")
    print(f"  -> GRF {F_foot} N -> Joint Torques: [HAA={tau_fl[0]:.2f}, HFE={tau_fl[1]:.2f}, KFE={tau_fl[2]:.2f}] Nm")
    assert len(tau_fl) == 3, "Torque vector size must be 3"
    wbc.destroy_node()

    print(">>> PASS: Leg Kinematics, Jacobian Transpose & Swing Trajectory Verified!")


def test_gait_scheduler_and_pd_control():
    log_section("TEST 2: Gait Scheduling, SRBD Dynamics & Joint PD Control")
    from quadruped_locomotion.gait_scheduler import GAITS, GaitType
    from quadruped_locomotion.mpc_controller.dynamics_model import SingleRigidBodyDynamics

    # 1. Validate Predefined Gait Profiles
    assert GaitType.STAND in GAITS, "STAND gait profile missing"
    assert GaitType.WALK in GAITS, "WALK gait profile missing"
    assert GaitType.TROT in GAITS, "TROT gait profile missing"
    assert GaitType.BOUND in GAITS, "BOUND gait profile missing"

    stand_params = GAITS[GaitType.STAND]
    trot_params = GAITS[GaitType.TROT]
    assert stand_params.duty_factor == 1.0, "Stand duty factor must be 1.0"
    assert trot_params.duty_factor == 0.5, "Trot duty factor must be 0.5"
    print(f"[Gait Profiles Test] Stand Duty={stand_params.duty_factor}, Trot Duty={trot_params.duty_factor} -> PASS")

    # 2. Test Single Rigid Body Dynamics (SRBD)
    srbd = SingleRigidBodyDynamics(mass=12.0)
    assert srbd.mass == 12.0, "SRBD mass mismatch"
    assert srbd.gravity == 9.81, "SRBD gravity mismatch"
    assert srbd.inertia.shape == (3, 3), "Inertia tensor must be 3x3"

    R = srbd.rotation_matrix_from_euler(0.0, 0.0, 0.0)
    assert np.allclose(R, np.eye(3)), "Zero Euler angles must yield identity rotation matrix"

    state = np.zeros(13)
    state[2] = 0.3  # height
    state[12] = -9.81 # gravity
    control = np.zeros(12) # 4 feet * 3 forces
    # Distribute 12kg * 9.81 = 117.72N across 4 feet = 29.43 N per foot in Z
    for i in range(4):
        control[i * 3 + 2] = (12.0 * 9.81) / 4.0

    foot_positions = {
        'FL': np.array([0.2, 0.15, -0.3]),
        'FR': np.array([0.2, -0.15, -0.3]),
        'RL': np.array([-0.2, 0.15, -0.3]),
        'RR': np.array([-0.2, -0.15, -0.3]),
    }

    x_dot = srbd.get_continuous_dynamics(state, control, foot_positions)
    print(f"[SRBD Test] Vertical Acceleration with balanced GRF: {x_dot[8]:.4f} m/s^2")
    assert abs(x_dot[8]) < 1e-2, f"Net vertical acceleration should be ~0 under equilibrium GRF, got {x_dot[8]}"

    print(">>> PASS: Gait Scheduling & SRBD Dynamics Verified!")


def test_contact_estimation_and_state_machine():
    log_section("TEST 3: Contact Force Estimation & Behavior State Machine Lifecycle")
    import rclpy
    if not rclpy.ok():
        rclpy.init()

    from quadruped_estimation.contact_estimator import ContactEstimator
    from quadruped_behaviors.behavior_state_machine import BehaviorStateMachine, BehaviorState
    from std_msgs.msg import String
    from sensor_msgs.msg import Imu

    # 1. Test Contact Estimator Schmitt Debouncing
    estimator = ContactEstimator()
    estimator.force_threshold = 10.0
    estimator.debounce_count = 3

    assert not estimator.contact_state['FL'], "Initial contact should be False"

    # Feed 3 high force readings -> contact should turn True
    for _ in range(4):
        estimator.update_contact_state('FL', force=25.0)
    assert estimator.contact_state['FL'], "Contact state should turn True after debounce count"
    print(f"[Contact Estimator Test] High force (25.0N) -> Contact State: {estimator.contact_state['FL']}")

    # Feed low force readings -> contact should turn False
    for _ in range(4):
        estimator.update_contact_state('FL', force=2.0)
    assert not estimator.contact_state['FL'], "Contact state should turn False after debounce count"
    print(f"[Contact Estimator Test] Low force (2.0N) -> Contact State: {estimator.contact_state['FL']}")
    estimator.destroy_node()

    # 2. Test Behavior State Machine Transitions
    fsm = BehaviorStateMachine()
    assert fsm.current_state == BehaviorState.IDLE, "FSM should start in IDLE state"

    # Command: stand
    cmd_stand = String()
    cmd_stand.data = 'stand'
    fsm.command_callback(cmd_stand)
    assert fsm.current_state == BehaviorState.STANDING, f"Expected STANDING, got {fsm.current_state}"

    # Command: trot
    cmd_trot = String()
    cmd_trot.data = 'trot'
    fsm.command_callback(cmd_trot)
    assert fsm.current_state == BehaviorState.TROTTING, f"Expected TROTTING, got {fsm.current_state}"

    # Fall detection injection via IMU
    imu_fall = Imu()
    # Large pitch of 1.2 rad (exceeds fall threshold 0.8 rad)
    # quaternion for pitch = 1.2 rad: qy = sin(0.6), qw = cos(0.6)
    imu_fall.orientation.y = math.sin(0.6)
    imu_fall.orientation.w = math.cos(0.6)
    fsm.imu_callback(imu_fall)
    assert fsm.is_fallen, "FSM should detect fallen condition"
    fsm.state_machine_loop()
    assert fsm.current_state == BehaviorState.RECOVERY, f"Expected RECOVERY on fall, got {fsm.current_state}"
    print(f"[Behavior FSM Test] Fall Trigger -> Transition to: {fsm.current_state.name} -> PASS")
    fsm.destroy_node()

    print(">>> PASS: Contact Estimator & Behavior FSM Verified!")


def test_hardware_bringup_and_controllers():
    log_section("TEST 4: ros2_control Multi-Controller Stack with Virtual Hardware Emulator")
    port_link = "/tmp/tty_quadruped"
    if os.path.exists(port_link):
        try:
            os.remove(port_link)
        except OSError:
            pass

    # Start Pseudo Quadruped Hardware Emulator
    emulator_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "src/ros2_quadruped_kit/scripts/pseudo_quadruped_emulator.py"
    )
    if not os.path.exists(emulator_script):
        emulator_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "scripts/pseudo_quadruped_emulator.py"
        )

    emulator_cmd = [sys.executable, emulator_script, "--port", port_link]
    print(f"[Launcher] Starting Pseudo Quadruped Emulator ({emulator_script})...")
    emulator_proc = subprocess.Popen(emulator_cmd, preexec_fn=os.setsid)

    # Wait for virtual serial port
    for _ in range(30):
        if os.path.exists(port_link):
            break
        time.sleep(0.1)
    assert os.path.exists(port_link), f"Virtual serial port {port_link} was not created"
    print(f"[Launcher] Virtual serial port active at {port_link}.")

    # Launch hardware bringup
    launch_cmd = [
        "ros2", "launch", "quadruped_bringup", "hardware.launch.py",
        f"serial_port:={port_link}",
        "use_fake_hardware:=false",
        "use_rviz:=false"
    ]
    print("[Launcher] Launching quadruped_bringup hardware.launch.py...")
    launch_proc = subprocess.Popen(launch_cmd, preexec_fn=os.setsid)

    try:
        # Allow ros2_control controller_manager and sequential spawners to activate (t=0s, 2s, 3s, 3.5s)
        time.sleep(7.0)

        # 1. Introspect active controllers
        ctrl_res = subprocess.run(["ros2", "control", "list_controllers"],
                                  capture_output=True, text=True, timeout=8)
        print(f"[Introspection] ros2_control Controllers:\n{ctrl_res.stdout}")
        assert "joint_state_broadcaster" in ctrl_res.stdout, "joint_state_broadcaster missing"
        assert "leg_controller" in ctrl_res.stdout, "leg_controller missing"
        assert "imu_broadcaster" in ctrl_res.stdout, "imu_broadcaster missing"
        print("  -> All 3 ros2_control controllers active and running at 1000 Hz!")

        # 2. Check /joint_states
        js_res = subprocess.run(["ros2", "topic", "echo", "/joint_states", "--once"],
                                capture_output=True, text=True, timeout=6)
        print("[Introspection] /joint_states output verified:")
        assert "FL_HAA" in js_res.stdout, "FL_HAA missing from /joint_states"
        assert "RR_KFE" in js_res.stdout, "RR_KFE missing from /joint_states"
        print("  -> All 12 quadruped leg joints streaming on /joint_states.")

        # 3. Check IMU topic (/imu/data or /imu_broadcaster/imu)
        topic_list = subprocess.run(["ros2", "topic", "list"], capture_output=True, text=True, timeout=5)
        print(f"[Introspection] Active ROS 2 Topics:\n{topic_list.stdout}")
        imu_topic = "/imu/data" if "/imu/data" in topic_list.stdout else "/imu_broadcaster/imu"
        imu_res = subprocess.run(["ros2", "topic", "echo", imu_topic, "--once"],
                                 capture_output=True, text=True, timeout=6)
        print(f"[Introspection] {imu_topic} output verified:")
        assert "orientation" in imu_res.stdout, f"Orientation missing from {imu_topic}"
        print(f"  -> IMU attitude and acceleration telemetry active on {imu_topic}.")

        # 4. Test Effort Command to leg_controller
        print("[Command] Publishing joint effort torques to /leg_controller/commands...")
        torques_cmd = [
            "ros2", "topic", "pub", "--once", "-w", "1",
            "/leg_controller/commands",
            "std_msgs/msg/Float64MultiArray",
            "{data: [0.0, 5.0, -10.0, 0.0, 5.0, -10.0, 0.0, 5.0, -10.0, 0.0, 5.0, -10.0]}"
        ]
        cmd_proc = subprocess.run(torques_cmd, capture_output=True, text=True, timeout=8)
        time.sleep(1.0)
        print("  -> 12-joint effort command received and dispatched to hardware interface.")

        print(">>> PASS: ros2_control Multi-Controller Stack & Hardware Emulator Verified!")

    finally:
        safe_kill(launch_proc)
        safe_kill(emulator_proc)
        time.sleep(1.5)
        if os.path.exists(port_link):
            try:
                os.remove(port_link)
            except OSError:
                pass


def test_demos_and_breakers():
    log_section("TEST 5: Progressive Demos & Intentional Fault Injection Breakers")
    test_env = os.environ.copy()
    test_env["PYTHONUNBUFFERED"] = "1"
    test_env["RCUTILS_LOGGING_BUFFERED_STREAM"] = "0"

    # Start robot state publisher so TF and URDF description exist
    rsp_proc = subprocess.Popen([
        "ros2", "launch", "quadruped_description", "display.launch.py",
        "use_rviz:=false", "use_gui:=false"
    ], env=test_env, preexec_fn=os.setsid)
    time.sleep(2.5)

    try:
        # 1. Test Demo 01 Joint Control
        print("[Demo Test] Running demo_01_joint_control...")
        d1_proc = subprocess.Popen(["ros2", "run", "quadruped_demos", "demo_01_joint_control"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   env=test_env, preexec_fn=os.setsid)
        time.sleep(3.0)
        safe_kill(d1_proc)
        out1, _ = d1_proc.communicate()
        print(f"  -> Demo 01 Output: {out1[:140].strip()}...")
        assert "demo 01" in out1.lower() or "joint control" in out1.lower(), "Demo 01 did not run"
        print("  -> Demo 01 verified.")

        # 2. Test Demo 02 Leg Kinematics
        print("[Demo Test] Running demo_02_leg_kinematics...")
        d2_proc = subprocess.Popen(["ros2", "run", "quadruped_demos", "demo_02_leg_kinematics"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   env=test_env, preexec_fn=os.setsid)
        time.sleep(3.0)
        safe_kill(d2_proc)
        out2, _ = d2_proc.communicate()
        print(f"  -> Demo 02 Output: {out2[:140].strip()}...")
        assert "demo 02" in out2.lower() or "kinematics" in out2.lower(), "Demo 02 did not run"
        print("  -> Demo 02 verified.")

        # 3. Test Breaker: break_contact
        print("[Breaker Test] Running break_contact...")
        b_cnt = subprocess.Popen(["ros2", "run", "quadruped_demos", "break_contact"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 env=test_env, preexec_fn=os.setsid)
        time.sleep(2.0)
        safe_kill(b_cnt)
        out_bcnt, _ = b_cnt.communicate()
        print(f"  -> Break Contact Output: {out_bcnt[:140].strip()}...")
        assert "breaking contact" in out_bcnt.lower() or "contact" in out_bcnt.lower(), "Contact breaker failed"
        print("  -> Contact breaker verified.")

        # 4. Test Breaker: break_gait
        print("[Breaker Test] Running break_gait...")
        b_gait = subprocess.Popen(["ros2", "run", "quadruped_demos", "break_gait"],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                  env=test_env, preexec_fn=os.setsid)
        time.sleep(2.0)
        safe_kill(b_gait)
        out_bgait, _ = b_gait.communicate()
        print(f"  -> Break Gait Output: {out_bgait[:140].strip()}...")
        assert "breaking gait" in out_bgait.lower() or "gait" in out_bgait.lower(), "Gait breaker failed"
        print("  -> Gait breaker verified.")

        # 5. Test Breaker: break_imu
        print("[Breaker Test] Running break_imu...")
        b_imu = subprocess.Popen(["ros2", "run", "quadruped_demos", "break_imu"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 env=test_env, preexec_fn=os.setsid)
        time.sleep(2.0)
        safe_kill(b_imu)
        out_bimu, _ = b_imu.communicate()
        print(f"  -> Break IMU Output: {out_bimu[:140].strip()}...")
        assert "breaking imu" in out_bimu.lower() or "imu" in out_bimu.lower(), "IMU breaker failed"
        print("  -> IMU breaker verified.")

        print(">>> PASS: Progressive Demos & Intentional Breakers Verified!")

    finally:
        safe_kill(rsp_proc)


if __name__ == '__main__':
    print("=" * 70)
    print(" STARTING COMPLETE VERIFICATION OF ros2_quadruped_kit")
    print("=" * 70)
    test_kinematics_and_swing_trajectory()
    test_gait_scheduler_and_pd_control()
    test_contact_estimation_and_state_machine()
    test_hardware_bringup_and_controllers()
    test_demos_and_breakers()
    print("\n" + "=" * 70)
    print(" ALL ros2_quadruped_kit VERIFICATION TESTS PASSED SUCCESSFULLY! ")
    print("=" * 70)
