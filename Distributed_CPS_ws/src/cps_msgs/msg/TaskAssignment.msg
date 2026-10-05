# TaskAssignment.msg
# Represents a coordinated mission task dispatched by the Base Coordinator to an edge robot.

std_msgs/Header header

# Unique identifier for the task
string task_id

# Target robot identifier (e.g. "robot1", "robot2", "all")
string assigned_robot_id

# Task Type enumeration
uint8 TASK_TYPE_EXPLORE = 1
uint8 TASK_TYPE_NAVIGATE_TO_POSE = 2
uint8 TASK_TYPE_PICK_OBJECT = 3
uint8 TASK_TYPE_PLACE_OBJECT = 4
uint8 TASK_TYPE_STATION_KEEPING = 5
uint8 task_type

# Spatial goal coordinates in global 'map' frame
geometry_msgs/PoseStamped target_pose

# Task priority (1 = lowest, 100 = critical safety/override)
uint8 priority

# Estimated time budget for task completion (seconds)
float32 timeout_seconds

# Auxiliary payload parameters in JSON or structured string
string task_parameters
