# RobotHeartbeat.msg
# Published at regular intervals (e.g. 2 Hz) by every edge robot to signal health and vitality.

std_msgs/Header header

# Unique robot identifier (e.g. "robot1", "robot2")
string robot_id

# Lifecycle state (1 = UNCONFIGURED, 2 = INACTIVE, 3 = ACTIVE, 4 = FINALIZED)
uint8 lifecycle_state

# Battery telemetry
float32 battery_voltage_v
float32 battery_percentage

# Onboard SBC resource utilization
float32 cpu_utilization_percent
float32 memory_usage_mb
float32 cpu_temperature_c

# Network QoS & RF link quality
int16 wifi_rssi_dbm
float32 topic_latency_ms
uint32 packets_dropped_count

# Active execution status
string current_task_id
string operational_mode
bool emergency_stop_active
