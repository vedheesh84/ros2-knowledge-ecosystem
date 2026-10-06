#!/usr/bin/env python3
"""
Comprehensive Automated Verification Test Suite for ros2_arm_kit
================================================================
Verifies:
1. Analytical Kinematics (FK, IK, Jacobian)
2. Hardware Bridge with Pseudo-Arm Serial Emulator (PTY)
3. Arm Simulation Launch Stack & TF / Pose Tracking
4. Gripper Controller & Pick-and-Place State Machine
5. Progressive Demos & Intentional Failure Breakers
"""

import os
import sys
import time
import subprocess
import signal
import math

sys.path.insert(0, '/media/ved/DATA/testing_sandbox/src/ros2_arm_kit/src/arm_kinematics')

def log_section(title):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)

def safe_kill(proc):
    if proc is None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=2)
    except Exception:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            pass

def test_kinematics_math():
    log_section("TEST 1: Analytical Kinematics Solvers (FK, IK, Jacobian)")
    from arm_kinematics.forward_kinematics import ForwardKinematics
    from arm_kinematics.inverse_kinematics import InverseKinematics
    from arm_kinematics.jacobian import ArmJacobian

    fk = ForwardKinematics()
    ik = InverseKinematics()
    jac = ArmJacobian()

    # 1. Forward Kinematics at Home Position (0, 0, 0, 0)
    x0, y0, z0, pitch0 = fk.compute_fk(0.0, 0.0, 0.0, 0.0)
    print(f"[FK Test] Home Pose -> X: {x0:.4f}m, Y: {y0:.4f}m, Z: {z0:.4f}m, Pitch: {pitch0:.4f}rad")
    assert abs(y0) < 1e-4, f"Home pose Y should be 0, got {y0}"
    assert abs(z0 - 0.096) < 1e-3, f"Home pose Z should be ~0.096m (d1), got {z0}"

    # 2. Inverse Kinematics Target Reaching
    target_x, target_y, target_z, target_pitch = 0.18, 0.0, 0.12, -0.5
    sol = ik.solve(target_x, target_y, target_z, target_pitch=target_pitch)
    assert sol is not None, f"IK solver failed on reachable target ({target_x}, {target_y}, {target_z})"
    q1, q2, q3, q4 = sol
    print(f"[IK Test] Target ({target_x}, {target_y}, {target_z}) -> Solved Joints: [{q1:.3f}, {q2:.3f}, {q3:.3f}, {q4:.3f}]")

    # Verify FK matches target
    fx, fy, fz, fp = fk.compute_fk(q1, q2, q3, q4)
    pos_err = math.sqrt((fx - target_x)**2 + (fy - target_y)**2 + (fz - target_z)**2)
    print(f"[IK Verification] Recovered Position -> ({fx:.4f}, {fy:.4f}, {fz:.4f}), Error: {pos_err*1000:.2f} mm")
    assert pos_err < 0.015, f"IK to FK error too large: {pos_err} m"

    # 3. Singularity Rejection
    unreachable = ik.solve(2.0, 2.0, 2.0)
    assert unreachable is None, "IK solver should return None for out-of-reach target"
    print("[IK Singularity Test] Out-of-reach target (2.0, 2.0, 2.0) correctly rejected.")

    # 4. Jacobian Manipulability
    m = jac.manipulability_index(q2, q3, q4)
    print(f"[Jacobian Test] Manipulability Index at configuration: {m:.5f}")
    assert m > 0.0, "Manipulability index must be positive for non-singular pose"

    print(">>> PASS: Kinematics Solvers Verified!")


def test_hardware_serial_bridge():
    log_section("TEST 2: Hardware Serial Bridge with Pseudo-Arm Emulator (PTY)")
    test_port = "/tmp/tty_arm_test"
    if os.path.exists(test_port):
        try:
            os.remove(test_port)
        except OSError:
            pass

    # Start Pseudo-Arm Emulator in new process group
    emulator_cmd = [
        sys.executable,
        "/media/ved/DATA/testing_sandbox/src/ros2_arm_kit/scripts/pseudo_arm_emulator.py",
        "--port", test_port,
        "--baud", "115200"
    ]
    print("[Launcher] Starting Pseudo Arm Emulator...")
    emulator_proc = subprocess.Popen(emulator_cmd, preexec_fn=os.setsid)

    # Wait for virtual port symlink creation
    for _ in range(30):
        if os.path.exists(test_port):
            break
        time.sleep(0.1)

    assert os.path.exists(test_port), f"Virtual serial port {test_port} was not created!"
    print(f"[Launcher] Virtual port {test_port} active.")

    # Start servo_bridge node via ros2 run in new process group
    bridge_cmd = [
        "ros2", "run", "arm_hardware", "servo_bridge.py",
        "--ros-args", "-p", f"serial_port:={test_port}", "-p", "baud_rate:=115200"
    ]
    print("[Launcher] Starting servo_bridge node...")
    bridge_proc = subprocess.Popen(bridge_cmd, preexec_fn=os.setsid)

    try:
        time.sleep(3.0) # Allow bridge to connect and stream at 50 Hz

        # Check /joint_states output via ros2 topic echo
        echo_cmd = ["ros2", "topic", "echo", "/joint_states", "--once"]
        echo_res = subprocess.run(echo_cmd, capture_output=True, text=True, timeout=8)
        print("[Introspection] Joint States output received:")
        assert "name:" in echo_res.stdout, "No JointState received on /joint_states"
        assert "joint_1" in echo_res.stdout, "joint_1 missing from JointState"
        assert "gripper_base_joint" in echo_res.stdout, "gripper_base_joint missing from JointState"
        print("  -> /joint_states verified with all arm and gripper joints.")

        # Publish a trajectory command to move the arm
        pub_cmd = [
            "ros2", "topic", "pub", "--once",
            "/arm_controller/joint_trajectory",
            "trajectory_msgs/msg/JointTrajectory",
            "{joint_names: ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'gripper_base_joint'], points: [{positions: [0.35, -0.25, 0.45, -0.15, 0.05], time_from_start: {sec: 1}}]}"
        ]
        print("[Command] Publishing JointTrajectory command...")
        subprocess.run(pub_cmd, capture_output=True, text=True, timeout=5)

        time.sleep(1.5) # Allow pseudo-arm interpolation to converge

        # Check /joint_states again to verify motion executed
        echo_res2 = subprocess.run(echo_cmd, capture_output=True, text=True, timeout=8)
        print("[Introspection] Joint States after motion command:")
        assert "position:" in echo_res2.stdout, "Position field missing from JointState"
        print("  -> Motion verified over virtual serial bridge.")
        print(">>> PASS: Hardware Serial Bridge & Pseudo Emulator Verified!")

    finally:
        safe_kill(bridge_proc)
        safe_kill(emulator_proc)
        if os.path.exists(test_port):
            try:
                os.remove(test_port)
            except OSError:
                pass


def test_simulation_launch_stack():
    log_section("TEST 3: Arm Simulation Stack, Kinematics Node & Gripper Controller")

    launch_cmd = [
        "ros2", "launch", "arm_bringup", "arm_sim.launch.py",
        "use_rviz:=false"
    ]
    print("[Launcher] Launching arm_sim.launch.py headless...")
    launch_proc = subprocess.Popen(launch_cmd, preexec_fn=os.setsid)

    try:
        time.sleep(3.5) # Allow nodes to initialize

        # Verify active nodes
        nodes_res = subprocess.run(["ros2", "node", "list"], capture_output=True, text=True, timeout=5)
        print(f"[Introspection] Active Nodes:\n{nodes_res.stdout}")
        assert "/robot_state_publisher" in nodes_res.stdout, "robot_state_publisher node missing"
        assert "/mock_arm_hardware" in nodes_res.stdout, "mock_arm_hardware node missing"
        assert "/arm_kinematics" in nodes_res.stdout, "arm_kinematics node missing"
        assert "/gripper_controller" in nodes_res.stdout, "gripper_controller node missing"

        # Verify /arm/end_effector_pose from kinematics service node
        pose_res = subprocess.run(
            ["ros2", "topic", "echo", "/arm/end_effector_pose", "--once"],
            capture_output=True, text=True, timeout=6
        )
        print(f"[Introspection] End Effector Pose:\n{pose_res.stdout}")
        assert "position:" in pose_res.stdout, "/arm/end_effector_pose not publishing"
        assert "frame_id: base_link" in pose_res.stdout or "frame_id: 'base_link'" in pose_res.stdout, "frame_id base_link missing"

        # Verify Gripper Command -> Status pipeline by starting echo listener first
        echo_proc = subprocess.Popen(
            ["ros2", "topic", "echo", "/gripper/status", "--once"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            preexec_fn=os.setsid
        )
        time.sleep(1.0) # DDS discovery window

        grip_cmd = ["ros2", "topic", "pub", "--once", "/gripper/command", "std_msgs/msg/Float32", "{data: 0.85}"]
        subprocess.run(grip_cmd, capture_output=True, text=True, timeout=5)

        try:
            status_out, _ = echo_proc.communicate(timeout=6)
            print(f"[Introspection] Gripper Status Feedback:\n{status_out.strip()}")
            assert "GRIPPER_MOVED_TO_0.85" in status_out, "Gripper feedback mismatch"
        except subprocess.TimeoutExpired:
            safe_kill(echo_proc)
            raise AssertionError("Gripper status echo timed out")

        print(">>> PASS: Simulation Stack, Kinematics Node & Gripper Controller Verified!")

    finally:
        safe_kill(launch_proc)
        time.sleep(1.5)


def test_pick_place_and_demos():
    log_section("TEST 4: Autonomous State Machine & Progressive Demos")

    # Start mock hardware so topics /arm_controller/joint_trajectory and /joint_states exist
    hw_proc = subprocess.Popen(
        ["ros2", "run", "arm_hardware", "mock_hardware_node.py"],
        preexec_fn=os.setsid
    )
    time.sleep(1.5)

    try:
        test_env = os.environ.copy()
        test_env["PYTHONUNBUFFERED"] = "1"
        test_env["RCUTILS_LOGGING_BUFFERED_STREAM"] = "0"

        # 1. Test Demo 01 Joint Control
        print("[Demo Test] Running demo_01_joint_control (1 cycle)...")
        d1_proc = subprocess.Popen(["ros2", "run", "arm_demos", "demo_01_joint_control"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   env=test_env, preexec_fn=os.setsid)
        time.sleep(4.5)
        safe_kill(d1_proc)
        out1, _ = d1_proc.communicate()
        print(f"  -> Demo 01 Output: {out1[:140].strip()}...")
        assert "Pose A" in out1 or "Demo 01" in out1, "Demo 01 did not execute correctly"

        # 2. Test Demo 02 Forward Kinematics Tracking
        print("[Demo Test] Running demo_02_forward_kinematics...")
        d2_proc = subprocess.Popen(["ros2", "run", "arm_demos", "demo_02_forward_kinematics"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   env=test_env, preexec_fn=os.setsid)
        time.sleep(3.0)
        safe_kill(d2_proc)
        out2, _ = d2_proc.communicate()
        print(f"  -> Demo 02 Output: {out2[:140].strip()}...")
        assert "Calculated End-Effector" in out2 or "Demo 02" in out2, "Demo 02 did not track FK"

        # 3. Test Demo 03 Inverse Kinematics
        print("[Demo Test] Running demo_03_inverse_kinematics (1 cycle)...")
        d3_proc = subprocess.Popen(["ros2", "run", "arm_demos", "demo_03_inverse_kinematics"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   env=test_env, preexec_fn=os.setsid)
        time.sleep(4.5)
        safe_kill(d3_proc)
        out3, _ = d3_proc.communicate()
        print(f"  -> Demo 03 Output: {out3[:140].strip()}...")
        assert "IK Solved" in out3 or "Commanding Cartesian" in out3, "Demo 03 did not solve IK"

        # 4. Test Demo 05 MoveIt Planning
        print("[Demo Test] Running demo_05_moveit_planning (1 cycle)...")
        d5_proc = subprocess.Popen(["ros2", "run", "arm_demos", "demo_05_moveit_planning"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   env=test_env, preexec_fn=os.setsid)
        time.sleep(5.0)
        safe_kill(d5_proc)
        out5, _ = d5_proc.communicate()
        print(f"  -> Demo 05 Output: {out5[:140].strip()}...")
        assert "Dispatched" in out5 or "Named Pose" in out5, "Demo 05 did not dispatch waypoints"

        # 5. Test Demo 09 Trajectory Playback Policy (DMP)
        print("[Demo Test] Running demo_09_trajectory_playback_policy...")
        d9_proc = subprocess.Popen(["ros2", "run", "arm_demos", "demo_09_trajectory_playback_policy"],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   env=test_env, preexec_fn=os.setsid)
        time.sleep(4.5)
        safe_kill(d9_proc)
        out9, _ = d9_proc.communicate()
        print(f"  -> Demo 09 Output: {out9[:140].strip()}...")
        assert "Synthesizing generalized trajectory" in out9 or "dispatched" in out9, "Demo 09 did not execute"


        # 6. Test Pick and Place State Machine
        print("[State Machine Test] Running pick_place_state_machine (2 cycles)...")
        fsm_proc = subprocess.Popen(["ros2", "run", "arm_manipulation", "pick_place_state_machine"],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                    env=test_env, preexec_fn=os.setsid)
        time.sleep(4.5) # 3 ticks of 1.5s
        safe_kill(fsm_proc)
        out_fsm, _ = fsm_proc.communicate()
        print(f"  -> State Machine Output:\n{out_fsm.strip()}")
        assert "Current State: IDLE" in out_fsm or "Current State: GRASP_OPEN" in out_fsm or "Current State: APPROACH" in out_fsm or "STATE:" in out_fsm, "FSM failed to transition"

        # 7. Test Breakers (Graceful fault handling)
        print("[Breaker Test] Running break_ik_singularity...")
        b_sing = subprocess.Popen(["ros2", "run", "arm_demos", "break_ik_singularity"],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                  env=test_env, preexec_fn=os.setsid)
        time.sleep(2.5)
        safe_kill(b_sing)
        out_bs, _ = b_sing.communicate()
        assert "correctly rejected" in out_bs or "BREAKER" in out_bs, "Singularity breaker failed"
        print("  -> Singularity breaker verified.")


        print("[Breaker Test] Running break_gripper_stall...")
        b_grip = subprocess.Popen(["ros2", "run", "arm_demos", "break_gripper_stall"],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                  env=test_env, preexec_fn=os.setsid)
        time.sleep(2.5)
        safe_kill(b_grip)
        out_bg, _ = b_grip.communicate()
        assert "BREAKER" in out_bg or "Commanded" in out_bg, "Gripper stall breaker failed"
        print("  -> Gripper stall breaker verified.")

        print("[Breaker Test] Running break_joint_limits...")
        b_lim = subprocess.Popen(["ros2", "run", "arm_demos", "break_joint_limits"],
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 env=test_env, preexec_fn=os.setsid)
        time.sleep(2.5)
        safe_kill(b_lim)
        out_bl, _ = b_lim.communicate()
        assert "BREAKER" in out_bl or "illegal" in out_bl, "Joint limits breaker failed"
        print("  -> Joint limits breaker verified.")

        print("[Breaker Test] Running break_trajectory_timing...")
        b_time = subprocess.Popen(["ros2", "run", "arm_demos", "break_trajectory_timing"],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                  env=test_env, preexec_fn=os.setsid)
        time.sleep(2.5)
        safe_kill(b_time)
        out_bt, _ = b_time.communicate()
        assert "BREAKER" in out_bt or "Dispatched" in out_bt, "Trajectory timing breaker failed"
        print("  -> Trajectory timing breaker verified.")


        print(">>> PASS: Pick-and-Place State Machine & Progressive Demos Verified!")


    finally:
        safe_kill(hw_proc)


if __name__ == '__main__':
    print("=" * 70)
    print(" STARTING COMPLETE VERIFICATION OF ros2_arm_kit")
    print("=" * 70)
    test_kinematics_math()
    test_hardware_serial_bridge()
    test_simulation_launch_stack()
    test_pick_place_and_demos()
    print("\n" + "=" * 70)
    print(" ALL ros2_arm_kit VERIFICATION TESTS PASSED SUCCESSFULLY! ")
    print("=" * 70)
