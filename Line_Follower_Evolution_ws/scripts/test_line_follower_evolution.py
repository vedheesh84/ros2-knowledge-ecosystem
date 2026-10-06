#!/usr/bin/env python3
"""
test_line_follower_evolution.py
Comprehensive End-to-End Regression Test Suite for Line Follower Evolution Workspace.

Covers all 4 Generations and 8 Curriculum Articles:
- Phase 1: Generation 1 (V1) Reactive Threshold Tracking (Article LFE-02)
- Phase 2: Generation 2/3 (V2-V3) 8-Channel Weighted Centroid Math (Article LFE-04)
- Phase 3: Generation 2/3 (V2-V3) Stabilized Motion Control & IMU Gyro Damping (Articles LFE-03 & 04)
- Phase 4: Generation 3 (V4) Symbolic Topological Graph Parsing (Article LFE-05)
- Phase 5: Generation 3 (V4-V5) Topological Navigator FSM & Rollback Recovery (Article LFE-06)
- Phase 6: Generation 4 (V6) Unconstrained Frontier Exploration (Article LFE-07)
- Phase 7: Pseudo-Hardware Serial Protocol & Arduino Firmware Command Exchange
- Phase 8: Master Evolution Selector Launch Recipe Verification
"""

import sys
import os
import time
import math
import json
import select
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from std_msgs.msg import Float32MultiArray, Float32, Bool, String
from geometry_msgs.msg import Twist, PoseStamped
from sensor_msgs.msg import Imu
from nav_msgs.msg import OccupancyGrid

from line_follower_v1_reactive.reactive_threshold_node import ReactiveThresholdNode
from line_follower_v1_reactive.simulated_track_sensor import SimulatedTrackSensor
from line_follower_v2_v3_stabilized.sensor_array_processor import SensorArrayProcessor
from line_follower_v2_v3_stabilized.stabilized_motion_controller import StabilizedMotionController
from line_follower_v4_v5_topological.topological_navigator_node import TopologicalNavigatorNode
from line_follower_v4_v5_topological.tag_detector_node import TagDetectorNode
from line_follower_v6_exploratory.frontier_explorer_node import FrontierExplorerNode


def print_header(title):
    print(f"\n{'='*75}\n  {title}\n{'='*75}")

def assert_true(cond, msg):
    if cond:
        print(f"  [PASS] {msg}")
    else:
        print(f"  [FAIL] {msg}")
        sys.exit(1)

def spin_until(executor, predicate, timeout_sec=0.5):
    start = time.time()
    while time.time() - start < timeout_sec:
        executor.spin_once(timeout_sec=0.02)
        if predicate():
            return True
    return False


# ==============================================================================
# TEST 1: Generation 1 (V1) Reactive Bang-Bang Tracker (Article LFE-02)
# ==============================================================================
def test_v1_reactive_tracker():
    print_header("TEST 1: Generation 1 (V1) Reactive Threshold Tracker")
    
    node = ReactiveThresholdNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    cmds = []
    def on_cmd(msg):
        cmds.append(msg)
    sub_c = node.create_subscription(Twist, '/cmd_vel', on_cmd, 10)
    
    # 1. Both sensors on line -> CENTERED
    m1 = Float32MultiArray()
    m1.data = [0.85, 0.85]
    node.ir_callback(m1)
    spin_until(executor, lambda: len(cmds) >= 1)
    assert_true(node.last_state == "CENTERED", "Both sensors on line -> CENTERED")
    assert_true(cmds[-1].linear.x == node.v_fwd and cmds[-1].angular.z == 0.0, "Centered robot drives forward at v_fwd")
    
    # 2. Left sensor only on line -> Hard Bang-Bang Left Turn
    m2 = Float32MultiArray()
    m2.data = [0.85, 0.15]
    node.ir_callback(m2)
    spin_until(executor, lambda: len(cmds) >= 2)
    assert_true(node.last_state == "TURN_LEFT_OVERSHOOT", "Line on left -> TURN_LEFT_OVERSHOOT")
    assert_true(cmds[-1].angular.z > 0.0, f"Positive yaw rate commands left turn ({cmds[-1].angular.z:.2f} rad/s)")
    
    # 3. Right sensor only on line -> Hard Bang-Bang Right Turn
    m3 = Float32MultiArray()
    m3.data = [0.15, 0.85]
    node.ir_callback(m3)
    spin_until(executor, lambda: len(cmds) >= 3)
    assert_true(node.last_state == "TURN_RIGHT_OVERSHOOT", "Line on right -> TURN_RIGHT_OVERSHOOT")
    assert_true(cmds[-1].angular.z < 0.0, f"Negative yaw rate commands right turn ({cmds[-1].angular.z:.2f} rad/s)")
    
    # 4. Off line completely -> Blind search spin
    m4 = Float32MultiArray()
    m4.data = [0.10, 0.10]
    node.ir_callback(m4)
    spin_until(executor, lambda: len(cmds) >= 4)
    assert_true(node.last_state == "LOST_LINE_SEARCHING", "Off line -> LOST_LINE_SEARCHING")
    assert_true(cmds[-1].linear.x == 0.0, "Forward drive disabled during line search")
    
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 2: Generation 2/3 (V2-V3) 8-Channel Weighted Centroid Math (Article LFE-04)
# ==============================================================================
def test_v2_v3_sensor_array_math():
    print_header("TEST 2: V2-V3 8-Channel IR Array Weighted Centroid Math")
    
    node = SensorArrayProcessor()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    errors = []
    intersections = []
    
    def on_error(msg):
        errors.append(msg.data)
    def on_int(msg):
        intersections.append(msg.data)
        
    sub_e = node.create_subscription(Float32, '/v2_v3/line_centroid_error', on_error, 10)
    sub_i = node.create_subscription(Bool, '/v2_v3/intersection_detected', on_int, 10)
    
    # 1. Symmetric Centered Line
    m_center = Float32MultiArray()
    m_center.data = [0.0, 0.1, 0.5, 0.9, 0.9, 0.5, 0.1, 0.0]
    node.raw_array_callback(m_center)
    spin_until(executor, lambda: len(errors) >= 1 and len(intersections) >= 1)
    assert_true(abs(errors[-1]) < 0.005, f"Centered line centroid error is near zero: {errors[-1]:.4f} m")
    assert_true(intersections[-1] is False, "Normal line is not flagged as an intersection")
    
    # 2. Shifted Left Line (Peak on sensor index 1: x = -25mm)
    m_left = Float32MultiArray()
    m_left.data = [0.4, 0.9, 0.4, 0.05, 0.0, 0.0, 0.0, 0.0]
    node.raw_array_callback(m_left)
    spin_until(executor, lambda: len(errors) >= 2 and len(intersections) >= 2)
    assert_true(errors[-1] < -0.015, f"Shifted left line centroid error is negative: {errors[-1]:.4f} m")
    
    # 3. Shifted Right Line (Peak on sensor index 6: x = +25mm)
    m_right = Float32MultiArray()
    m_right.data = [0.0, 0.0, 0.0, 0.0, 0.05, 0.4, 0.9, 0.4]
    node.raw_array_callback(m_right)
    spin_until(executor, lambda: len(errors) >= 3 and len(intersections) >= 3)
    assert_true(errors[-1] > +0.015, f"Shifted right line centroid error is positive: {errors[-1]:.4f} m")
    
    # 4. Crossbar Intersection (all 8 sensors dark)
    m_cross = Float32MultiArray()
    m_cross.data = [0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95]
    node.raw_array_callback(m_cross)
    spin_until(executor, lambda: len(errors) >= 4 and len(intersections) >= 4)
    assert_true(intersections[-1] is True, "Crossbar with 8 active sensors flags intersection_detected = True")
    
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 3: Generation 2/3 (V2-V3) Stabilized Motion Controller (Articles LFE-03 & 04)
# ==============================================================================
def test_v2_v3_stabilized_motion_controller():
    print_header("TEST 3: V2-V3 Motion Layer: Closed-Loop Dual PID & Gyro Damping")
    
    node = StabilizedMotionController()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    cmds = []
    def on_cmd(msg):
        cmds.append(msg)
    sub_c = node.create_subscription(Twist, '/cmd_vel', on_cmd, 10)
    
    # 1. Zero Error, zero IMU rate -> Maximum forward speed
    e0 = Float32()
    e0.data = 0.0
    node.error_callback(e0)
    spin_until(executor, lambda: len(cmds) >= 1)
    assert_true(abs(cmds[-1].linear.x - 0.65) < 0.05, f"Zero error drives near maximum speed: {cmds[-1].linear.x:.2f} m/s")
    assert_true(abs(cmds[-1].angular.z) < 0.05, "Zero error commands near zero yaw rate")
    
    # 2. Positive lateral error (line is to the right) -> negative steering command
    e_pos = Float32()
    e_pos.data = 0.02 # +20mm error
    node.error_callback(e_pos)
    spin_until(executor, lambda: len(cmds) >= 2)
    assert_true(cmds[-1].angular.z < 0.0, f"Positive error generates negative yaw rate: {cmds[-1].angular.z:.2f} rad/s")
    
    # 3. IMU Gyroscopic Damping Effect
    node.last_error = 0.0 # Reset derivative state to isolate gyro damping
    imu_disturb = Imu()
    imu_disturb.angular_velocity.z = 2.0 # spinning at +2.0 rad/s
    node.imu_callback(imu_disturb)
    node.error_callback(e0)
    spin_until(executor, lambda: len(cmds) >= 3)
    assert_true(cmds[-1].angular.z < 0.0, f"Gyro damping counteracted positive yaw disturbance: {cmds[-1].angular.z:.2f} rad/s")
    
    # 4. Adaptive speed reduction on sharp curves
    e_large = Float32()
    e_large.data = 0.035 # maximum 35mm error
    node.error_callback(e_large)
    spin_until(executor, lambda: len(cmds) >= 4)
    assert_true(cmds[-1].linear.x < 0.50, f"Speed automatically throttled on sharp curve: {cmds[-1].linear.x:.2f} < 0.50 m/s")
    
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 4: Generation 3 (V4) Symbolic Topological Graph Parsing (Article LFE-05)
# ==============================================================================
def test_v4_topological_graph_parsing():
    print_header("TEST 4: Generation 3 (V4) Symbolic Topological Graph Parsing")
    
    candidates = [
        "/media/ved/DATA/Intelligent Systems Knowledge Ecosystem/02 — Domains/ROS2/Line_Follower_Evolution_ws/src/line_follower_v4_v5_topological/maps/warehouse_topology_graph.json",
        "/media/ved/DATA/testing_sandbox/src/Line_Follower_Evolution_ws/line_follower_v4_v5_topological/maps/warehouse_topology_graph.json"
    ]
    graph_path = next((p for p in candidates if os.path.exists(p)), None)
    assert_true(graph_path is not None, "Found warehouse_topology_graph.json in workspace or sandbox")
    
    with open(graph_path, 'r') as f:
        data = json.load(f)
        
    nodes = data.get("nodes", {})
    assert_true("N1" in nodes and "N5" in nodes, "Topological graph contains origin (N1) and destination (N5)")
    assert_true(len(nodes) == 5, f"Topological graph contains 5 warehouse vertices (got {len(nodes)})")
    assert_true("N2" in nodes["N1"]["neighbors"], "N1 connects to N2")
    assert_true("N4" in nodes["N2"]["neighbors"], "N2 connects to N4")
    assert_true("N5" in nodes["N4"]["neighbors"], "N4 connects to N5")


# ==============================================================================
# TEST 5: Generation 3 (V4-V5) Topological Navigator FSM (Article LFE-06)
# ==============================================================================
def test_v4_v5_topological_navigator():
    print_header("TEST 5: Generation 3 (V4-V5) Topological Navigator FSM & Rollback")
    
    node = TopologicalNavigatorNode()
    node.timer.cancel() # Deterministic step testing
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    cmds = []
    statuses = []
    
    def on_cmd(msg):
        cmds.append(msg)
    def on_status(msg):
        statuses.append(json.loads(msg.data))
        
    sub_c = node.create_subscription(Twist, '/cmd_vel', on_cmd, 10)
    sub_s = node.create_subscription(String, '/v4_v5/navigation_status', on_status, 10)
    
    assert_true(node.state == "TRAVERSING_EDGE", "Initial FSM state is TRAVERSING_EDGE")
    
    # 1. Traverse edge towards N2
    node.fsm_step()
    spin_until(executor, lambda: len(cmds) >= 1)
    assert_true(cmds[-1].linear.x > 0.4, "Robot drives forward during TRAVERSING_EDGE")
    
    # 2. Arrive at expected node N2
    tag_n2 = String()
    tag_n2.data = "N2"
    node.tag_callback(tag_n2)
    assert_true(node.current_node == "N2", "Node verified as N2")
    assert_true(node.state == "EXECUTING_TURN", "Transitioned to EXECUTING_TURN")
    
    # 3. Simulate turn duration completion
    node.turn_start_time = time.time() - 1.5 # 1.5s elapsed > 1.0s turn_duration
    node.fsm_step()
    spin_until(executor, lambda: len(cmds) >= 2)
    assert_true(node.state == "TRAVERSING_EDGE", "Turn completed; resumed TRAVERSING_EDGE")
    
    # 4. Unexpected tag -> Trigger ROLLBACK_RECOVERY
    tag_wrong = String()
    tag_wrong.data = "UNEXPECTED_OBSTACLE_NODE"
    node.tag_callback(tag_wrong)
    assert_true(node.state == "ROLLBACK_RECOVERY", "Unexpected tag triggered ROLLBACK_RECOVERY")
    node.fsm_step()
    spin_until(executor, lambda: len(cmds) >= 3)
    assert_true(cmds[-1].linear.x < 0.0, "Rollback commands reverse velocity to backtrack")
    
    # 5. Goal completion
    node.state = "TRAVERSING_EDGE"
    node.path_index = len(node.planned_path) - 2 # At N4
    tag_final = String()
    tag_final.data = "N5"
    node.tag_callback(tag_final)
    assert_true(node.state == "GOAL_REACHED", "Final destination N5 reached -> GOAL_REACHED")
    node.fsm_step()
    spin_until(executor, lambda: len(cmds) >= 4)
    assert_true(cmds[-1].linear.x == 0.0 and cmds[-1].angular.z == 0.0, "Robot stops completely on GOAL_REACHED")
    
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 6: Generation 4 (V6) Unconstrained Frontier Exploration (Article LFE-07)
# ==============================================================================
def test_v6_frontier_exploration():
    print_header("TEST 6: Generation 4 (V6) Unconstrained Frontier Exploration")
    
    node = FrontierExplorerNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    goals = []
    def on_goal(msg):
        goals.append(msg)
    sub_g = node.create_subscription(PoseStamped, '/goal_pose', on_goal, 10)
    
    # Create 10x10 occupancy grid
    # Free space (0) in rows [2..7], cols [2..7]
    # Unknown space (-1) everywhere else
    grid = OccupancyGrid()
    grid.info.resolution = 0.1
    grid.info.width = 10
    grid.info.height = 10
    grid.info.origin.position.x = 0.0
    grid.info.origin.position.y = 0.0
    
    data = np.full((10, 10), -1, dtype=np.int8)
    data[2:8, 2:8] = 0 # 6x6 free space room
    grid.data = data.flatten().tolist()
    
    # Test boundary frontier detection algorithm directly
    frontier_mask = node.find_frontier_cells(data)
    
    # Inner cells (e.g. [4, 4]) are surrounded by free space -> NOT a frontier
    assert_true(frontier_mask[4, 4] == False, "Interior free cell (4, 4) is NOT a frontier")
    # Perimeter cells (e.g. [2, 2]) border unknown cells (-1) -> IS a frontier
    assert_true(frontier_mask[2, 2] == True, "Perimeter free cell (2, 2) IS a true frontier")
    
    node.map_callback(grid)
    spin_until(executor, lambda: len(goals) >= 1)
    
    assert_true(len(goals) > 0, "Frontier explorer published exploration goal to /goal_pose")
    assert_true(goals[-1].pose.position.x > 0.0 and goals[-1].pose.position.y > 0.0, "Dispatched goal coordinates are within map bounds")
    
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 7: Pseudo-Hardware Serial Protocol & Arduino Firmware Command Exchange
# ==============================================================================
def test_pseudo_hardware_serial():
    print_header("TEST 7: Pseudo-Hardware Serial Protocol & Arduino Firmware Exchange")
    
    from pseudo_line_follower_emulator import PseudoLineFollowerEmulator
    
    test_port = '/tmp/ttyLFE_TEST'
    emulator = PseudoLineFollowerEmulator(port_path=test_port)
    time.sleep(0.4)
    
    assert_true(os.path.exists(test_port), f"Virtual serial port established at {test_port}")
    
    fd = os.open(test_port, os.O_RDWR | os.O_NONBLOCK)
    time.sleep(0.4)
    
    r, _, _ = select.select([fd], [], [], 1.0)
    assert_true(bool(r), "Serial port received streaming telemetry bytes")
    
    buf = os.read(fd, 512).decode('utf-8', errors='ignore')
    assert_true("$LFE,seq=" in buf, "Detected Arduino NMEA telemetry frame '$LFE,seq='")
    
    def read_until_token(token, timeout=1.5):
        accum = ""
        start = time.time()
        while time.time() - start < timeout:
            r, _, _ = select.select([fd], [], [], 0.05)
            if r:
                accum += os.read(fd, 512).decode('utf-8', errors='ignore')
                if token in accum:
                    return True
        return False

    # Send PING
    os.write(fd, b"$CMD,PING\n")
    found_pong = read_until_token("$PONG,LFE_CONTROLLER_ALIVE")
    assert_true(found_pong, "Serial command $CMD,PING received $PONG response")
    
    # Send Emergency Stop
    os.write(fd, b"$CMD,ESTOP\n")
    found_ack = read_until_token("$ACK,ESTOP_ENGAGED")
    assert_true(found_ack, "Serial command $CMD,ESTOP engaged emergency stop")
    assert_true(emulator.estop_active is True, "Emulator internal state reflects emergency stop")
    
    os.close(fd)
    emulator.destroy_node()


# ==============================================================================
# TEST 8: Master Evolution Selector Launch Recipe Verification
# ==============================================================================
def test_master_evolution_selector():
    print_header("TEST 8: Master Evolution Selector Launch Recipe Verification")
    
    import importlib.util
    candidates = [
        "/media/ved/DATA/Intelligent Systems Knowledge Ecosystem/02 — Domains/ROS2/Line_Follower_Evolution_ws/src/line_follower_evolution_bringup/launch/master_evolution_selector.launch.py",
        "/media/ved/DATA/testing_sandbox/src/Line_Follower_Evolution_ws/line_follower_evolution_bringup/launch/master_evolution_selector.launch.py"
    ]
    launch_path = next((p for p in candidates if os.path.exists(p)), None)
    assert_true(launch_path is not None, "Found master_evolution_selector.launch.py in workspace or sandbox")
    
    spec = importlib.util.spec_from_file_location("master_launch", launch_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ld = mod.generate_launch_description()
    
    assert_true(len(ld.entities) == 5, f"Launch description has 5 entities (1 arg + 4 generational launches, got {len(ld.entities)})")


def main():
    rclpy.init()
    try:
        test_v1_reactive_tracker()
        test_v2_v3_sensor_array_math()
        test_v2_v3_stabilized_motion_controller()
        test_v4_topological_graph_parsing()
        test_v4_v5_topological_navigator()
        test_v6_frontier_exploration()
        test_pseudo_hardware_serial()
        test_master_evolution_selector()
        
        print_header("ALL 8 PHASES PASSED (100% SUCCESS)")
        print("Line Follower Evolution Workspace & Curriculum Articles 01-08 Fully Verified!\n")
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
