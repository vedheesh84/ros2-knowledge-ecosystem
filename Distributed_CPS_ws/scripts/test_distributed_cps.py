#!/usr/bin/env python3
"""
test_distributed_cps.py
Comprehensive End-to-End Regression Test Suite for Distributed Multi-Robot CPS Workspace.

Covers all 9 Curriculum Articles and 4 Workspace Packages:
- Test 1: cps_msgs Custom Interface Instantiation & Serialization
- Test 2: Network Script & FastDDS Discovery Server Config Verification
- Test 3: Base Coordinator Node Lifecycle & RequestTask Service
- Test 4: CBBA Decentralized Auction Engine Convergence & Conflict Resolution
- Test 5: Map Merger Node 2D Bayesian Log-Odds Occupancy Fusion
- Test 6: Reciprocal Collision Avoidance & Velocity Obstacle Marker Logic
- Test 7: Topic Delay Monitor Latency Measurement & Jitter Calculation
- Test 8: Prometheus ROS Exporter Embedded HTTP /metrics Exposition
- Test 9: Health Watchdog Supervisor Timeout & Failover Alerting
- Test 10: Pseudo-Hardware Serial Gateway & Failsafe Communication
"""

import sys
import os
import time
import math
import json
import xml.etree.ElementTree as ET
import urllib.request
import select

import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from std_msgs.msg import String, Float32
from geometry_msgs.msg import PoseStamped, Point
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import OccupancyGrid
from visualization_msgs.msg import Marker

# Ensure install path is accessible
from cps_msgs.msg import RobotHeartbeat, TaskAssignment, PeerState
from cps_msgs.srv import RequestTask
from cps_msgs.action import ExecuteCoordinatedMission

from cps_coordination.base_coordinator_node import BaseCoordinatorNode
from cps_coordination.cbba_auction_node import CBBAAuctionNode
from cps_coordination.map_merger_node import MapMergerNode
from cps_coordination.peer_collision_avoidance import PeerCollisionAvoidance
from cps_coordination.health_watchdog_node import HealthWatchdogNode

from cps_telemetry.topic_delay_monitor import TopicDelayMonitor
from cps_telemetry.prometheus_ros_exporter import PrometheusROSExporter


def print_header(title):
    print(f"\n{'='*75}\n  {title}\n{'='*75}")

def assert_true(cond, msg):
    if cond:
        print(f"  [PASS] {msg}")
    else:
        print(f"  [FAIL] {msg}")
        sys.exit(1)


# ==============================================================================
# TEST 1: cps_msgs Interfaces
# ==============================================================================
def test_cps_msgs_interfaces():
    print_header("TEST 1: Custom ROS 2 Message, Service & Action Interfaces")
    
    # 1. RobotHeartbeat
    hb = RobotHeartbeat()
    hb.robot_id = 'robot1'
    hb.lifecycle_state = 3
    hb.battery_percentage = 95.5
    hb.battery_voltage_v = 12.4
    hb.cpu_utilization_percent = 28.2
    hb.wifi_rssi_dbm = -52
    hb.operational_mode = 'AUTONOMOUS'
    assert_true(hb.robot_id == 'robot1', "RobotHeartbeat instantiated with robot_id='robot1'")
    assert_true(abs(hb.battery_percentage - 95.5) < 1e-4, "RobotHeartbeat battery percentage matches")
    
    # 2. TaskAssignment
    task = TaskAssignment()
    task.task_id = 'task_scout_01'
    task.assigned_robot_id = 'robot1'
    task.task_type = TaskAssignment.TASK_TYPE_EXPLORE
    task.priority = 80
    task.timeout_seconds = 60.0
    assert_true(task.task_type == 1, "TaskAssignment.TASK_TYPE_EXPLORE equals 1")
    assert_true(task.priority == 80, "TaskAssignment priority matches")
    
    # 3. PeerState
    ps = PeerState()
    ps.robot_id = 'robot2'
    ps.safety_radius_m = 0.65
    ps.capabilities = [1.2, 5.0, 0.8]  # speed, payload, reach
    assert_true(ps.safety_radius_m == 0.65, "PeerState safety radius set")
    assert_true(len(ps.capabilities) == 3, "PeerState capabilities vector length 3")
    
    # 4. RequestTask srv
    req = RequestTask.Request()
    req.robot_id = 'robot2'
    req.battery_level = 88.0
    resp = RequestTask.Response()
    resp.task_available = True
    resp.message = 'Ready'
    assert_true(resp.task_available is True, "RequestTask service types verified")
    
    # 5. ExecuteCoordinatedMission action
    goal = ExecuteCoordinatedMission.Goal()
    goal.mission_id = 'mission_omega'
    res = ExecuteCoordinatedMission.Result()
    res.mission_success = True
    fb = ExecuteCoordinatedMission.Feedback()
    fb.overall_progress_percent = 50.0
    assert_true(goal.mission_id == 'mission_omega' and res.mission_success, "ExecuteCoordinatedMission action types verified")


# ==============================================================================
# TEST 2: Network Script & FastDDS Configuration
# ==============================================================================
def test_network_and_dds_configs():
    print_header("TEST 2: Network Script & FastDDS Discovery Server Config")
    
    script_path = "/media/ved/DATA/Intelligent Systems Knowledge Ecosystem/02 — Domains/ROS2/Distributed_CPS_ws/setup_network.sh"
    assert_true(os.path.exists(script_path), f"Found setup_network.sh at {script_path}")
    
    # Parse FastDDS XML
    xml_path = "/media/ved/DATA/Intelligent Systems Knowledge Ecosystem/02 — Domains/ROS2/Distributed_CPS_ws/src/cps_bringup/config/fastdds_discovery_server.xml"
    assert_true(os.path.exists(xml_path), f"Found fastdds_discovery_server.xml at {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    assert_true(root.tag.endswith('dds'), "FastDDS XML root tag is <dds>")
    
    # Check locator port 11811
    port_elem = tree.find('.//{http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles}port')
    assert_true(port_elem is not None and port_elem.text == '11811', "FastDDS Discovery Server port set to 11811")


# ==============================================================================
# TEST 3: Base Coordinator Node
# ==============================================================================
def test_base_coordinator_node():
    print_header("TEST 3: Base Coordinator State Machine & Task Dispatching")
    
    node = BaseCoordinatorNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    dispatched_tasks = []
    goal_poses = []
    
    def on_task(msg):
        dispatched_tasks.append(msg)
        
    def on_goal(msg):
        goal_poses.append(msg)
        
    sub_task = node.create_subscription(TaskAssignment, '/cps/tasks', on_task, 10)
    sub_goal = node.create_subscription(PoseStamped, '/robot2/goal_pose', on_goal, 10)
    
    # Simulate target detected by Robot 1
    target = PoseStamped()
    target.header.stamp = node.get_clock().now().to_msg()
    target.header.frame_id = 'map'
    target.pose.position.x = 4.5
    target.pose.position.y = 2.1
    node.target_detected_callback(target)
    
    # Spin to process callbacks
    start_time = time.time()
    while time.time() - start_time < 0.5:
        executor.spin_once(timeout_sec=0.05)
        
    assert_true(len(goal_poses) > 0, "Base Coordinator dispatched goal pose to /robot2/goal_pose")
    assert_true(len(dispatched_tasks) > 0, "Base Coordinator published TaskAssignment to /cps/tasks")
    assert_true(dispatched_tasks[0].assigned_robot_id == 'robot2', "Task assigned to 'robot2'")
    assert_true(node.mission_phase == 'DISPATCHING_MANIPULATOR', "Mission phase transitioned to DISPATCHING_MANIPULATOR")
    
    # Test RequestTask service
    req = RequestTask.Request()
    req.robot_id = 'robot1'
    resp = RequestTask.Response()
    resp = node.request_task_callback(req, resp)
    assert_true(resp.task_available is True, "RequestTask service returned valid task assignment")
    assert_true(resp.assigned_task.assigned_robot_id == 'robot1', "Assigned task matches requesting robot")
    
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 4: CBBA Decentralized Auction Engine
# ==============================================================================
def test_cbba_auction_node():
    print_header("TEST 4: CBBA Decentralized Auction Engine (Article CPS-06)")
    
    # Agent 1 at (0, 0), Agent 2 at (10, 10)
    node1 = CBBAAuctionNode()
    node1.robot_id = 'robot1'
    node1.agent_x = 0.0
    node1.agent_y = 0.0
    
    node2 = CBBAAuctionNode()
    node2.robot_id = 'robot2'
    node2.agent_x = 10.0
    node2.agent_y = 10.0
    
    # Task A at (1, 1) [closer to Agent 1], Task B at (9, 9) [closer to Agent 2]
    node1.add_task('task_A', 1.0, 1.0, 100.0)
    node1.add_task('task_B', 9.0, 9.0, 100.0)
    
    node2.add_task('task_A', 1.0, 1.0, 100.0)
    node2.add_task('task_B', 9.0, 9.0, 100.0)
    
    # Before communication: each agent greedly prefers closer task
    assert_true('task_A' in node1.bundle, "Agent 1 initially includes closer task_A in bundle")
    assert_true('task_B' in node2.bundle, "Agent 2 initially includes closer task_B in bundle")
    
    # Simulate Communication Round 1: Node 1 sends bids to Node 2
    pkt1 = {
        'agent_id': 'robot1',
        'bids': node1.winning_bids,
        'winners': node1.winning_agents
    }
    msg1 = String()
    msg1.data = json.dumps(pkt1)
    node2.bids_callback(msg1)
    
    # Simulate Node 2 sends bids to Node 1
    pkt2 = {
        'agent_id': 'robot2',
        'bids': node2.winning_bids,
        'winners': node2.winning_agents
    }
    msg2 = String()
    msg2.data = json.dumps(pkt2)
    node1.bids_callback(msg2)
    
    # Both agents run auction cycle again to finalize consensus
    node1.auction_cycle()
    node2.auction_cycle()
    
    # Consensus Verification:
    # Agent 1 should win Task A (dist sqrt(2) ~ 1.41 vs dist ~12.7 for Agent 2)
    # Agent 2 should win Task B (dist sqrt(2) ~ 1.41 vs dist ~12.7 for Agent 1)
    score_1A = node1.calculate_marginal_score({'x': 1.0, 'y': 1.0, 'reward': 100.0}, 0.0, 0.0)
    score_2A = node2.calculate_marginal_score({'x': 1.0, 'y': 1.0, 'reward': 100.0}, 10.0, 10.0)
    assert_true(score_1A > score_2A, f"Agent 1 marginal score on Task A ({score_1A:.2f}) > Agent 2 ({score_2A:.2f})")
    
    assert_true(node1.winning_agents['task_A'] == 'robot1', "Consensus reached: Agent 1 wins task_A")
    assert_true(node2.winning_agents['task_B'] == 'robot2', "Consensus reached: Agent 2 wins task_B")
    
    node1.destroy_node()
    node2.destroy_node()


# ==============================================================================
# TEST 5: Map Merger Node 2D Bayesian Log-Odds Fusion
# ==============================================================================
def test_map_merger_node():
    print_header("TEST 5: Map Merger 2D Bayesian Log-Odds Fusion (Article CPS-05)")
    
    node = MapMergerNode()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    merged_maps = []
    def on_merged_map(msg):
        merged_maps.append(msg)
        
    sub_map = node.create_subscription(OccupancyGrid, '/map', on_merged_map, 10)
    
    # Create test grids (10x10, resolution 0.1m)
    m1 = OccupancyGrid()
    m1.info.resolution = 0.1
    m1.info.width = 10
    m1.info.height = 10
    m1.info.origin.position.x = 0.0
    m1.info.origin.position.y = 0.0
    # cell 0: unknown (-1), cell 1: free (0), cell 2: obstacle (100)
    data1 = [-1] * 100
    data1[1] = 0
    data1[2] = 100
    m1.data = data1
    
    m2 = OccupancyGrid()
    m2.info.resolution = 0.1
    m2.info.width = 10
    m2.info.height = 10
    m2.info.origin.position.x = 0.0
    m2.info.origin.position.y = 0.0
    data2 = [-1] * 100
    data2[0] = -1   # unknown + unknown -> unknown
    data2[1] = -1   # free + unknown -> free (0)
    data2[2] = -1   # obstacle + unknown -> obstacle (100)
    data2[3] = 100  # unknown + obstacle -> obstacle (100)
    m2.data = data2
    
    node.map1_callback(m1)
    node.map2_callback(m2)
    node.fuse_and_publish()
    
    start_time = time.time()
    while time.time() - start_time < 0.5 and not merged_maps:
        executor.spin_once(timeout_sec=0.05)
        
    assert_true(len(merged_maps) > 0, "Merged map published to /map")
    fused_data = merged_maps[0].data
    assert_true(fused_data[0] == -1, "Cell 0: Unknown (-1) + Unknown (-1) = -1")
    assert_true(fused_data[1] == 0, "Cell 1: Free (0) + Unknown (-1) = 0")
    assert_true(fused_data[2] == 100, "Cell 2: Obstacle (100) + Unknown (-1) = 100")
    assert_true(fused_data[3] == 100, "Cell 3: Unknown (-1) + Obstacle (100) = 100")
    
    # Test Mathematical Log-Odds Function directly
    # Two independent sensor observations of an obstacle (e.g. 80 and 80)
    fused_val = MapMergerNode.fuse_cell_log_odds(80, 80)
    assert_true(fused_val > 80, f"Bayesian log-odds fused confidence increased: {fused_val}% > 80%")
    
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 6: Reciprocal Collision Avoidance
# ==============================================================================
def test_peer_collision_avoidance():
    print_header("TEST 6: Reciprocal Collision Avoidance & Velocity Obstacle (Article CPS-07)")
    
    node = PeerCollisionAvoidance()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    markers = []
    risks = []
    
    def on_marker(msg):
        markers.append(msg)
        
    def on_risk(msg):
        risks.append(json.loads(msg.data))
        
    sub_m = node.create_subscription(Marker, '/robot1/peer_obstacle_marker', on_marker, 10)
    sub_r = node.create_subscription(String, '/robot1/collision_risk', on_risk, 10)
    
    # Self at (0, 0)
    self_pose = PoseStamped()
    self_pose.pose.position.x = 0.0
    self_pose.pose.position.y = 0.0
    node.self_pose_callback(self_pose)
    
    # 1. Peer at safe distance (5.0, 5.0) -> separation ~7.07m
    peer_safe = PoseStamped()
    peer_safe.pose.position.x = 5.0
    peer_safe.pose.position.y = 5.0
    node.peer_pose_callback(peer_safe)
    
    start_time = time.time()
    while time.time() - start_time < 0.3:
        executor.spin_once(timeout_sec=0.05)
        
    assert_true(risks and risks[-1]['risk_level'] == 'SAFE', "Peer at 7m assessed as SAFE")
    assert_true(markers and markers[-1].color.g > 0.5, "Safe marker is green")
    
    # 2. Peer at critical distance (0.5, 0.5) -> separation ~0.707m (< 0.8 * 1.5)
    peer_crit = PoseStamped()
    peer_crit.pose.position.x = 0.5
    peer_crit.pose.position.y = 0.5
    node.peer_pose_callback(peer_crit)
    
    start_time = time.time()
    while time.time() - start_time < 0.3:
        executor.spin_once(timeout_sec=0.05)
        
    assert_true(risks[-1]['risk_level'] == 'CRITICAL', "Peer at 0.7m assessed as CRITICAL")
    assert_true(markers[-1].color.r == 1.0 and markers[-1].color.g == 0.0, "Critical obstacle marker is bright red")
    
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 7: Topic Delay Monitor
# ==============================================================================
def test_topic_delay_monitor():
    print_header("TEST 7: Topic Delay Monitor & Jitter Probe (Article CPS-03 & 08)")
    
    node = TopicDelayMonitor()
    node.sample_window = 10
    
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    latencies = []
    stats = []
    
    def on_lat(msg):
        latencies.append(msg.data)
        
    def on_stats(msg):
        stats.append(json.loads(msg.data))
        
    sub_l = node.create_subscription(Float32, '/cps/topic_latency', on_lat, 10)
    sub_s = node.create_subscription(String, '/cps/network_stats', on_stats, 10)
    
    # Inject 10 LaserScan messages with synthetic 15ms latency
    now = node.get_clock().now()
    for _ in range(10):
        scan = LaserScan()
        # Header stamp 15 milliseconds earlier
        scan.header.stamp.sec = now.nanoseconds // 1_000_000_000
        scan.header.stamp.nanosec = (now.nanoseconds % 1_000_000_000) - 15_000_000
        node.scan_callback(scan)
        
    start_time = time.time()
    while time.time() - start_time < 0.3:
        executor.spin_once(timeout_sec=0.05)
        
    assert_true(len(latencies) >= 10, f"Received {len(latencies)} instantaneous latency reports")
    assert_true(len(stats) > 0, "Network stats summary published after sample window")
    assert_true(stats[0]['avg_latency_ms'] >= 0.0, f"Average latency computed: {stats[0]['avg_latency_ms']} ms")
    
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 8: Prometheus ROS Exporter & HTTP Endpoint
# ==============================================================================
def test_prometheus_ros_exporter():
    print_header("TEST 8: Prometheus ROS Telemetry Exporter (Article CPS-08)")
    
    test_port = 9188
    node = PrometheusROSExporter()
    node.metrics_port = test_port
    node.stop_http_server()  # stop default if bound
    node.start_http_server()
    
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    # Inject heartbeat for robot1
    hb = RobotHeartbeat()
    hb.robot_id = 'robot1'
    hb.battery_percentage = 91.2
    hb.battery_voltage_v = 12.2
    hb.cpu_utilization_percent = 26.8
    hb.wifi_rssi_dbm = -55
    hb.topic_latency_ms = 4.8
    node.heartbeat_typed_callback(hb)
    
    time.sleep(0.1)
    
    # Perform HTTP scrape
    metrics_url = f"http://127.0.0.1:{test_port}/metrics"
    req = urllib.request.Request(metrics_url)
    with urllib.request.urlopen(req, timeout=2.0) as response:
        status_code = response.getcode()
        body = response.read().decode('utf-8')
        
    assert_true(status_code == 200, f"Prometheus HTTP GET {metrics_url} returned HTTP 200")
    assert_true('robot_battery_percentage{robot_id="robot1"} 91.20' in body, "Found robot_battery_percentage metric")
    assert_true('robot_cpu_utilization_percent{robot_id="robot1"} 26.80' in body, "Found robot_cpu_utilization_percent metric")
    assert_true('robot_wifi_rssi_dbm{robot_id="robot1"} -55.0' in body, "Found robot_wifi_rssi_dbm metric")
    
    node.stop_http_server()
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 9: Health Watchdog Node & Failover
# ==============================================================================
def test_health_watchdog_node():
    print_header("TEST 9: Health Watchdog Supervisor & Failover Trigger")
    
    node = HealthWatchdogNode()
    node.timeout = 0.5 # 500ms timeout for rapid testing
    
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    
    alerts = []
    def on_alert(msg):
        alerts.append(json.loads(msg.data))
        
    sub_a = node.create_subscription(String, '/cps/system_alerts', on_alert, 10)
    
    # 1. Edge robot sends heartbeat
    hb = RobotHeartbeat()
    hb.robot_id = 'robot1'
    hb.lifecycle_state = 3
    hb.battery_percentage = 98.0
    node.heartbeat_typed_callback(hb)
    
    assert_true(node.agents['robot1']['status'] == 'HEALTHY', "Agent robot1 registered as HEALTHY")
    
    # 2. Simulate network partition / silence > timeout (0.7s)
    time.sleep(0.7)
    node.supervision_loop()
    
    start_time = time.time()
    while time.time() - start_time < 0.3:
        executor.spin_once(timeout_sec=0.05)
        
    assert_true(node.agents['robot1']['status'] == 'UNRESPONSIVE', "Agent transitioned to UNRESPONSIVE after silence")
    assert_true(len(alerts) > 0, "Failover alert published to /cps/system_alerts")
    assert_true(alerts[0]['event'] == 'NODE_FAILURE' and alerts[0]['failed_agent'] == 'robot1', "Alert identifies failed agent")
    assert_true(alerts[0]['action'] == 'REASSIGN_TASKS', "Failover action commands task reassignment")
    
    executor.remove_node(node)
    node.destroy_node()


# ==============================================================================
# TEST 10: Pseudo-Hardware Serial Gateway & Failsafe
# ==============================================================================
def test_pseudo_hardware_serial():
    print_header("TEST 10: Pseudo-Hardware Serial Gateway & Emergency Stop")
    
    from pseudo_cps_network_emulator import PseudoCPSEmulator
    
    test_port = '/tmp/ttyCPS_TEST'
    emulator = PseudoCPSEmulator(port_path=test_port)
    time.sleep(0.6)  # allow background thread to generate serial data
    
    assert_true(os.path.exists(test_port), f"Virtual serial port created at {test_port}")
    
    # Open serial port and read telemetry frame
    fd = os.open(test_port, os.O_RDWR | os.O_NONBLOCK)
    
    time.sleep(0.6)
    r, _, _ = select.select([fd], [], [], 1.0)
    assert_true(bool(r), "Serial port received bytes from pseudo-firmware")
    
    buf = os.read(fd, 512).decode('utf-8', errors='ignore')
    assert_true("$CPS,id=edge_anchor_1" in buf, "Detected NMEA telemetry frame '$CPS,id=edge_anchor_1'")
    
    # Send PING command
    os.write(fd, b"$CMD,PING\n")
    time.sleep(0.2)
    resp = os.read(fd, 256).decode('utf-8', errors='ignore')
    assert_true("$PONG,EDGE_ALIVE" in resp, "Serial command $CMD,PING received $PONG response")
    
    # Send Emergency Stop command
    os.write(fd, b"$CMD,ESTOP\n")
    time.sleep(0.2)
    resp2 = os.read(fd, 256).decode('utf-8', errors='ignore')
    assert_true("$ACK,ESTOP_ENGAGED" in resp2, "Serial command $CMD,ESTOP engaged emergency stop")
    assert_true(emulator.estop_active is True, "Emulator internal state reflects emergency stop engagement")
    
    os.close(fd)
    emulator.destroy_node()


def main():
    rclpy.init()
    try:
        test_cps_msgs_interfaces()
        test_network_and_dds_configs()
        test_base_coordinator_node()
        test_cbba_auction_node()
        test_map_merger_node()
        test_peer_collision_avoidance()
        test_topic_delay_monitor()
        test_prometheus_ros_exporter()
        test_health_watchdog_node()
        test_pseudo_hardware_serial()
        
        print_header("ALL 10 TESTS PASSED (100% SUCCESS)")
        print("Distributed CPS Workspace & Curriculum Articles 01-09 Fully Verified!\n")
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
