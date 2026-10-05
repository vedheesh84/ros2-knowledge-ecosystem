# PeerState.msg
# Shared peer state for decentralized formation, reciprocal collision avoidance (ORCA), and auctioning.

std_msgs/Header header

# Robot identifier
string robot_id

# 3D spatial pose and linear/angular velocity in shared 'map' frame
geometry_msgs/Pose pose
geometry_msgs/Twist twist

# Bounding cylinder radius for collision avoidance (meters)
float32 safety_radius_m

# Current goal position
geometry_msgs/Point current_goal_position

# Auction capability vector [exploration_speed, payload_capacity_kg, arm_reach_m]
float32[3] capabilities
